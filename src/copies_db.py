"""
copies_db.py — Persistência de copies no Supabase.

Tabela: saved_copies
  status = 'aprovada' | 'rejeitada'
  reason = motivo da rejeição (apenas para rejeitadas)
"""
from __future__ import annotations

import re
import requests
import streamlit as st


# ── Credenciais ───────────────────────────────────────────────────────────────

def _creds() -> tuple[str, str]:
    try:
        url = st.secrets.get("supabase_url", "") or ""
        key = st.secrets.get("supabase_service_key", "") or ""
        return url, key
    except Exception:
        return "", ""


def _configured() -> bool:
    url, key = _creds()
    return bool(url and key)


def _headers() -> dict:
    _, key = _creds()
    return {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }


def _rest() -> str:
    url, _ = _creds()
    return f"{url}/rest/v1/saved_copies"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_score_num(hook_score: str) -> int:
    """Extrai o número inteiro de strings como '8/10 — justificativa'."""
    import re
    m = re.search(r"(\d+)\s*/\s*10", hook_score)
    return int(m.group(1)) if m else 0


# ── Montar payload base ────────────────────────────────────────────────────────

def _build_payload(form_data: dict, copy: dict, copy_index: int, status: str, reason: str = "", campaign_name: str = "") -> dict:
    return {
        "client_name":      form_data.get("client_name") or "",
        "client_key":       form_data.get("client_key") or "",
        "product":          form_data.get("product", ""),
        "niche":            form_data.get("niche", ""),
        "sub_niche":        form_data.get("sub_niche", ""),
        "objective":        form_data.get("objective", ""),
        "tone":             form_data.get("tone", ""),
        "cta":              form_data.get("cta", ""),
        "tipo_criativo":    form_data.get("tipo_criativo", ""),
        "copy_index":       copy_index,
        "tipo_nome":        copy.get("tipo_nome", ""),
        "legenda_hook":     copy.get("legenda_hook", ""),
        "legenda_corpo":    copy.get("legenda_corpo", ""),
        "legenda_cta":      copy.get("legenda_cta", ""),
        "legenda_completa": copy.get("legenda_completa", ""),
        "criativo":         copy.get("criativo", ""),
        "status":           status,
        "reason":           reason,
        "hook_score":       copy.get("hook_score", ""),
        "hook_score_num":   _extract_score_num(copy.get("hook_score", "")),
        "campaign_name":    campaign_name,
    }


# ── Salvar copy aprovada ──────────────────────────────────────────────────────

def save_approved_copy(form_data: dict, copy: dict, copy_index: int, campaign_name: str = "") -> bool:
    """Salva uma copy aprovada. Chamada ao clicar ✅ Aprovar."""
    if not _configured():
        return False
    try:
        r = requests.post(
            _rest(),
            headers=_headers(),
            json=_build_payload(form_data, copy, copy_index, "aprovada", campaign_name=campaign_name),
            timeout=10,
        )
        return r.status_code in (200, 201)
    except Exception:
        return False


# ── Salvar copy rejeitada ─────────────────────────────────────────────────────

def save_rejected_copy(form_data: dict, copy: dict, copy_index: int, reason: str) -> bool:
    """Salva uma copy rejeitada com o motivo. Chamada ao confirmar rejeição."""
    if not _configured():
        return False
    try:
        r = requests.post(
            _rest(),
            headers=_headers(),
            json=_build_payload(form_data, copy, copy_index, "rejeitada", reason),
            timeout=10,
        )
        return r.status_code in (200, 201)
    except Exception:
        return False


# ── Carregar histórico ────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_saved(status: str = "", client_name: str = "", limit: int = 50) -> list[dict]:
    """
    Carrega copies salvas.
    status: 'aprovada' | 'rejeitada' | '' (todas)
    """
    if not _configured():
        return []

    url_base, key = _creds()
    params = {
        "order":  "created_at.desc",
        "limit":  str(limit),
        "select": "id,client_name,client_key,product,niche,objective,tipo_criativo,"
                  "tipo_nome,legenda_hook,legenda_corpo,legenda_cta,"
                  "legenda_completa,criativo,status,reason,hook_score,hook_score_num,"
                  "campaign_name,created_at",
    }
    if status:
        params["status"] = f"eq.{status}"
    if client_name:
        params["client_name"] = f"eq.{client_name}"

    try:
        r = requests.get(
            f"{url_base}/rest/v1/saved_copies",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            params=params,
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


# ── Padrões de rejeição agregados ─────────────────────────────────────────────

def get_rejection_patterns(client_name: str) -> str:
    """
    Analisa os motivos de rejeição do cliente e retorna um resumo
    dos padrões mais frequentes para incluir no prompt do Claude.
    Retorna string vazia se não houver rejeições suficientes.
    """
    if not _configured() or not client_name:
        return ""

    url_base, key = _creds()
    try:
        r = requests.get(
            f"{url_base}/rest/v1/saved_copies",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            params={
                "client_name": f"eq.{client_name}",
                "status":      "eq.rejeitada",
                "order":       "created_at.desc",
                "limit":       "30",
                "select":      "reason",
            },
            timeout=10,
        )
        r.raise_for_status()
        rows = r.json()
    except Exception:
        return ""

    reasons = [row.get("reason", "").strip() for row in rows if row.get("reason", "").strip()]
    if len(reasons) < 3:
        return ""

    # Palavras-chave de rejeição mais comuns no contexto de copy
    keywords = [
        ("formal", ["formal", "sério", "corporativo", "frio"]),
        ("agressivo", ["agressivo", "forte demais", "exagerado", "forçado"]),
        ("longo", ["longo", "extenso", "grande demais", "comprido", "muito texto"]),
        ("genérico", ["genérico", "vago", "superficial", "geral", "sem especificidade"]),
        ("tom errado", ["tom", "linguagem", "voz", "estilo errado", "não combina"]),
        ("fraco", ["fraco", "sem impacto", "sem força", "sem gancho", "hook fraco"]),
        ("clichê", ["clichê", "batido", "óbvio", "lugar-comum"]),
        ("curto", ["curto demais", "faltou", "incompleto", "raso"]),
    ]

    counts = {}
    for label, terms in keywords:
        count = sum(
            1 for reason in reasons
            if any(t in reason.lower() for t in terms)
        )
        if count >= 2:
            counts[label] = count

    if not counts:
        return ""

    sorted_patterns = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    lines = [f"Padrões identificados nas últimas {len(reasons)} rejeições deste cliente:"]
    for label, count in sorted_patterns[:5]:
        lines.append(f"  • '{label}' mencionado {count}x — evite esse padrão proativamente")
    lines.append("  → Ajuste o tom e estrutura desde o início para não repetir esses erros.")

    return "\n".join(lines)


# ── Performance real da campanha ───────────────────────────────────────────────

import json as _json

def get_campaign_performance(client_key: str, campaign_name: str) -> dict | None:
    """
    Busca a performance real de uma campanha no histórico de relatórios.
    Retorna dict com ctr, cpm, cpc, status ou None se não encontrado.
    Compara pelo nome da campanha (case-insensitive, substring match).
    """
    if not _configured() or not client_key or not campaign_name:
        return None

    url_base, key = _creds()
    try:
        r = requests.get(
            f"{url_base}/rest/v1/report_history",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            params={
                "client_key": f"eq.{client_key}",
                "order":      "generated_at.desc",
                "limit":      "5",          # busca nos 5 relatórios mais recentes
                "select":     "metrics,date_from,date_to",
            },
            timeout=10,
        )
        r.raise_for_status()
        rows = r.json()
    except Exception:
        return None

    campaign_lower = campaign_name.strip().lower()

    for row in rows:
        metrics = row.get("metrics", {})
        if isinstance(metrics, str):
            try:
                metrics = _json.loads(metrics)
            except Exception:
                continue

        campaigns = metrics.get("top_campaigns", [])
        for c in campaigns:
            if campaign_lower in c.get("name", "").lower():
                return {
                    "name":      c.get("name", campaign_name),
                    "ctr":       round(float(c.get("ctr", 0)), 2),
                    "cpm":       round(float(c.get("cpm", 0)), 2),
                    "cpc":       round(float(c.get("cpc", 0)), 2),
                    "spend":     round(float(c.get("spend", 0)), 2),
                    "status":    c.get("status", ""),
                    "period":    f"{row.get('date_from','')[:7]} → {row.get('date_to','')[:7]}",
                }

    return None
