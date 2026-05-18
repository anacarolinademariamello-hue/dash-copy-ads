"""
copies_db.py — Persistência de copies aprovadas no Supabase.

Tabela: approved_copies
  id               UUID PK default gen_random_uuid()
  client_name      TEXT
  product          TEXT
  niche            TEXT
  sub_niche        TEXT
  objective        TEXT
  tone             TEXT
  cta              TEXT
  tipo_criativo    TEXT
  copy_index       INT   (1–5)
  tipo_nome        TEXT
  legenda_hook     TEXT
  legenda_corpo    TEXT
  legenda_cta      TEXT
  legenda_completa TEXT
  criativo         TEXT
  created_at       TIMESTAMPTZ default now()
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
    return f"{url}/rest/v1/approved_copies"


# ── Salvar copy aprovada ──────────────────────────────────────────────────────

def save_approved_copy(form_data: dict, copy: dict, copy_index: int) -> bool:
    """
    Salva uma única copy aprovada no Supabase.
    Chamada quando o usuário clica em ✅ Aprovar.
    """
    if not _configured():
        return False

    payload = {
        "client_name":      form_data.get("client_name") or "",
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
    }

    try:
        r = requests.post(_rest(), headers=_headers(), json=payload, timeout=10)
        return r.status_code in (200, 201)
    except Exception:
        return False


# ── Carregar histórico de aprovadas ──────────────────────────────────────────

@st.cache_data(ttl=30)
def load_approved(client_name: str = "", limit: int = 50) -> list[dict]:
    """
    Carrega copies aprovadas, ordenadas da mais recente.
    Filtra por cliente se client_name for informado.
    """
    if not _configured():
        return []

    _, key = _creds()
    url_base, _ = _creds()
    params = {
        "order":  "created_at.desc",
        "limit":  str(limit),
        "select": "id,client_name,product,niche,objective,tipo_criativo,"
                  "tipo_nome,legenda_hook,legenda_corpo,legenda_cta,"
                  "legenda_completa,criativo,created_at",
    }
    if client_name:
        params["client_name"] = f"eq.{client_name}"

    try:
        r = requests.get(
            f"{url_base}/rest/v1/approved_copies",
            headers={
                "apikey":        key,
                "Authorization": f"Bearer {key}",
            },
            params=params,
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return []
