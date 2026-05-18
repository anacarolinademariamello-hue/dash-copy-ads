import json
import base64
import requests
import streamlit as st

REPO = "anacarolinademariamello-hue/dash-copy-ads"
FILE_PATH = "clients.json"


# ── Supabase (fonte primária) ─────────────────────────────────────────────────

def _supabase_creds() -> tuple[str, str]:
    try:
        url = st.secrets.get("supabase_url", "") or ""
        key = st.secrets.get("supabase_service_key", "") or ""
        return url, key
    except Exception:
        return "", ""


def _supabase_configured() -> bool:
    url, key = _supabase_creds()
    return bool(url and key)


def _supabase_headers() -> dict:
    _, key = _supabase_creds()
    return {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


@st.cache_data(ttl=120)
def _load_from_supabase() -> list[dict]:
    """Carrega clientes ativos do Supabase no formato copy-ads."""
    if not _supabase_configured():
        return []
    url, _ = _supabase_creds()
    try:
        resp = requests.get(
            f"{url}/rest/v1/clients",
            headers=_supabase_headers(),
            params={
                "active": "eq.true",
                "order":  "name.asc",
                "select": "key,name,handle,tone_of_voice,competitors,bio,tags,observations,goals",
            },
            timeout=10,
        )
        resp.raise_for_status()
        rows = resp.json()
        return [
            {
                "name":          r["name"],
                "tone_of_voice": r.get("tone_of_voice") or "",
                "competitors":   r.get("competitors") or "",
                "bio":           r.get("bio") or "",
                "tags":          r.get("tags") or [],
                "observations":  r.get("observations") or "",
                "goals":         r.get("goals") or {},
                "_source":       "supabase",
            }
            for r in rows
        ]
    except Exception:
        return []


def _gh_headers() -> dict:
    token = ""
    try:
        token = st.secrets.get("GITHUB_TOKEN", "")
    except Exception:
        pass
    h = {"Accept": "application/vnd.github.v3+json"}
    if token:
        h["Authorization"] = f"token {token}"
    return h


@st.cache_data(ttl=120)
def load_clients() -> list[dict]:
    """
    Carrega clientes — Supabase primeiro (fonte principal), depois GitHub JSON (fallback).
    Clientes do Supabase e do JSON são mesclados sem duplicatas por nome.
    """
    # 1. Tenta Supabase (fonte principal)
    supabase_clients = _load_from_supabase()
    if supabase_clients:
        return supabase_clients

    # 2. Fallback: GitHub API
    try:
        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        resp = requests.get(url, headers=_gh_headers(), timeout=8)
        if resp.status_code == 200:
            raw = base64.b64decode(resp.json()["content"]).decode("utf-8")
            return json.loads(raw).get("clients", [])
    except Exception:
        pass

    # 3. Fallback: arquivo local
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("clients", [])
    except Exception:
        return []


def save_client(new_client: dict) -> tuple[bool, str]:
    """Adiciona cliente e salva no GitHub."""
    clients = load_clients()

    if any(c["name"].lower() == new_client["name"].lower() for c in clients):
        return False, f"Já existe um cliente com o nome '{new_client['name']}'."

    clients.append(new_client)

    content = json.dumps({"clients": clients}, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    try:
        token = ""
        try:
            token = st.secrets.get("GITHUB_TOKEN", "")
        except Exception:
            pass

        if not token:
            # Salva só localmente
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            load_clients.clear()
            return True, "Cliente salvo localmente. Adicione GITHUB_TOKEN nos secrets para persistir no Streamlit Cloud."

        headers = _gh_headers()
        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

        resp = requests.get(url, headers=headers, timeout=8)
        sha = resp.json().get("sha") if resp.status_code == 200 else None

        payload = {"message": f"Cadastra cliente: {new_client['name']}", "content": encoded}
        if sha:
            payload["sha"] = sha

        put = requests.put(url, headers=headers, json=payload, timeout=15)
        if put.status_code in (200, 201):
            load_clients.clear()
            return True, f"Cliente '{new_client['name']}' salvo com sucesso!"

        return False, f"Erro ao salvar no GitHub ({put.status_code}). Verifique o GITHUB_TOKEN."

    except Exception as e:
        return False, f"Erro de conexão: {e}"


def delete_client(name: str) -> tuple[bool, str]:
    """Remove cliente pelo nome e salva."""
    clients = load_clients()
    updated = [c for c in clients if c["name"] != name]

    if len(updated) == len(clients):
        return False, "Cliente não encontrado."

    content = json.dumps({"clients": updated}, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    try:
        token = ""
        try:
            token = st.secrets.get("GITHUB_TOKEN", "")
        except Exception:
            pass

        if not token:
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            load_clients.clear()
            return True, "Cliente removido localmente."

        headers = _gh_headers()
        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        resp = requests.get(url, headers=headers, timeout=8)
        sha = resp.json().get("sha") if resp.status_code == 200 else None

        payload = {"message": f"Remove cliente: {name}", "content": encoded}
        if sha:
            payload["sha"] = sha

        put = requests.put(url, headers=headers, json=payload, timeout=15)
        if put.status_code in (200, 201):
            load_clients.clear()
            return True, f"Cliente '{name}' removido."

        return False, f"Erro ao remover no GitHub ({put.status_code})."

    except Exception as e:
        return False, f"Erro: {e}"


def extract_text(uploaded_file) -> str:
    """Extrai texto de arquivo TXT ou PDF."""
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore").strip()
    elif name.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(uploaded_file)
            pages = [p.extract_text() or "" for p in reader.pages]
            return "\n".join(pages).strip()
        except Exception as e:
            return f"[Erro ao ler PDF: {e}]"
    return uploaded_file.read().decode("utf-8", errors="ignore").strip()
