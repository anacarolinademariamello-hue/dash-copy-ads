"""
copies_db.py — Persistência de copies no Supabase.

Tabela: saved_copies
  status = 'aprovada' | 'rejeitada'
  reason = motivo da rejeição (apenas para rejeitadas)
"""
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

def _build_payload(form_data: dict, copy: dict, copy_index: int, status: str, reason: str = "") -> dict:
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
    }


# ── Salvar copy aprovada ──────────────────────────────────────────────────────

def save_approved_copy(form_data: dict, copy: dict, copy_index: int) -> bool:
    """Salva uma copy aprovada. Chamada ao clicar ✅ Aprovar."""
    if not _configured():
        return False
    try:
        r = requests.post(
            _rest(),
            headers=_headers(),
            json=_build_payload(form_data, copy, copy_index, "aprovada"),
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
        "select": "id,client_name,product,niche,objective,tipo_criativo,"
                  "tipo_nome,legenda_hook,legenda_corpo,legenda_cta,"
                  "legenda_completa,criativo,status,reason,hook_score,created_at",
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
