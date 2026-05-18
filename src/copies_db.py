"""
copies_db.py — Persistência de copies geradas no Supabase.

Tabela: copy_batches
  id            UUID PK default gen_random_uuid()
  client_name   TEXT
  client_key    TEXT
  product       TEXT
  niche         TEXT
  sub_niche     TEXT
  objective     TEXT
  tone          TEXT
  cta           TEXT
  tipo_criativo TEXT
  copies        JSONB   — lista de 5 copies, cada uma com campo "status"
  created_at    TIMESTAMPTZ default now()
"""
import json
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


def _headers(extra: dict | None = None) -> dict:
    _, key = _creds()
    h = {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }
    if extra:
        h.update(extra)
    return h


def _rest(table: str) -> str:
    url, _ = _creds()
    return f"{url}/rest/v1/{table}"


# ── Salvar lote ───────────────────────────────────────────────────────────────

def save_batch(form_data: dict, copies: list) -> str | None:
    """
    Salva um lote de 5 copies no Supabase.
    Cada copy recebe status='pendente' inicialmente.
    Retorna o UUID do lote (id) ou None em caso de erro.
    """
    if not _configured():
        return None

    copies_with_status = [
        {**c, "status": "pendente"} for c in copies
    ]

    payload = {
        "client_name":   form_data.get("client_name") or "",
        "client_key":    form_data.get("client_key") or "",
        "product":       form_data.get("product", ""),
        "niche":         form_data.get("niche", ""),
        "sub_niche":     form_data.get("sub_niche", ""),
        "objective":     form_data.get("objective", ""),
        "tone":          form_data.get("tone", ""),
        "cta":           form_data.get("cta", ""),
        "tipo_criativo": form_data.get("tipo_criativo", ""),
        "copies":        copies_with_status,
    }

    try:
        r = requests.post(
            _rest("copy_batches"),
            headers=_headers(),
            json=payload,
            timeout=10,
        )
        if r.status_code in (200, 201):
            data = r.json()
            return data[0]["id"] if data else None
        return None
    except Exception:
        return None


# ── Atualizar status de uma copy ──────────────────────────────────────────────

def update_copy_status(batch_id: str, copy_index: int, status: str) -> bool:
    """
    Atualiza o status de uma copy dentro do lote.
    copy_index: 1-5 (1-based, como mostrado na UI).
    status: 'aprovada' | 'em_teste' | 'rejeitada' | 'pendente'
    """
    if not _configured() or not batch_id:
        return False

    # Busca o lote atual
    try:
        r = requests.get(
            _rest("copy_batches"),
            headers=_headers(),
            params={"id": f"eq.{batch_id}", "select": "copies"},
            timeout=10,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            return False

        copies = rows[0]["copies"]
        if isinstance(copies, str):
            copies = json.loads(copies)

        idx = copy_index - 1  # converte para 0-based
        if 0 <= idx < len(copies):
            copies[idx]["status"] = status

        patch = requests.patch(
            _rest("copy_batches"),
            headers=_headers({"Prefer": "return=minimal"}),
            params={"id": f"eq.{batch_id}"},
            json={"copies": copies},
            timeout=10,
        )
        return patch.status_code in (200, 204)
    except Exception:
        return False


# ── Carregar histórico ────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_batches(client_name: str = "", limit: int = 50) -> list[dict]:
    """
    Carrega histórico de lotes salvos.
    Se client_name for fornecido, filtra por cliente.
    """
    if not _configured():
        return []

    params = {
        "order":  "created_at.desc",
        "limit":  str(limit),
        "select": "id,client_name,product,niche,objective,copies,created_at",
    }
    if client_name:
        params["client_name"] = f"eq.{client_name}"

    try:
        r = requests.get(
            _rest("copy_batches"),
            headers=_headers(),
            params=params,
            timeout=10,
        )
        r.raise_for_status()
        rows = r.json()
        for row in rows:
            if isinstance(row.get("copies"), str):
                row["copies"] = json.loads(row["copies"])
        return rows
    except Exception:
        return []
