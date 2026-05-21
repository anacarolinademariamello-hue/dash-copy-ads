import streamlit as st
import base64

from src.niches import NICHES, OBJECTIVES, TONES, CTAS, FORMAT_OPTIONS, FORMAT_TIPS
from src.copy_gen import generate_copies, COPY_TYPES, CRIATIVO_LABELS
from src.clients import load_clients, save_client, delete_client, extract_text, delete_client_supabase, save_performance_context, load_latest_report_metrics
from src.copies_db import save_approved_copy, save_rejected_copy, load_saved, get_rejection_patterns, get_campaign_performance
from src.styles import (
    get_sidebar_css,
    get_main_css,
    get_page_header_html,
    get_sidebar_welcome_html,
    get_sidebar_copy_header_html,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gerador de Copy · Meta Ads",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"<style>{get_sidebar_css()}{get_main_css()}</style>",
    unsafe_allow_html=True,
)


def get_logo_base64():
    try:
        with open("assets/logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""


# ── HTML de download ───────────────────────────────────────────────────────────
def _build_download_html(copies: list, fd: dict) -> str:
    criativo_label = CRIATIVO_LABELS.get(fd.get("tipo_criativo", ""), "Copy do Criativo")
    cards_html = ""
    for i, copy in enumerate(copies, 1):
        cor = copy.get("cor", "#003f7c")
        cor_bg = copy.get("cor_bg", "#eff6ff")
        tipo_nome = copy.get("tipo_nome", "")
        hook = copy.get("legenda_hook", "").replace("<", "&lt;").replace(">", "&gt;")
        body = copy.get("legenda_corpo", "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        cta_text = copy.get("legenda_cta", "").replace("<", "&lt;").replace(">", "&gt;")
        criativo = copy.get("criativo", "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

        cards_html += f"""
        <div class="card">
          <div class="card-accent" style="background:linear-gradient(90deg,{cor},{cor}88)"></div>
          <div class="card-inner">
            <div class="card-header">
              <span class="copy-num">Copy {i} de 5</span>
              <span class="badge" style="background:{cor_bg};color:{cor}">{tipo_nome}</span>
            </div>
            <div class="slabel">Legenda — Hook</div>
            <div class="hook" style="border-color:{cor}">{hook}</div>
            <div class="slabel">Legenda — Corpo</div>
            <div class="body-text">{body}</div>
            <div class="slabel">CTA</div>
            <div class="cta-box" style="background:{cor_bg};color:{cor}">{cta_text}</div>
            <div class="slabel" style="margin-top:18px;padding-top:14px;border-top:1px solid #eef1f6;">{criativo_label}</div>
            <div class="criativo-box">{criativo}</div>
          </div>
          <div class="approval-box">
            <div class="approval-label">Feedback do cliente</div>
            <div class="approval-options">
              <label><input type="radio" name="approval_{i}"> Aprovado</label>
              <label><input type="radio" name="approval_{i}"> Requer ajuste</label>
              <label><input type="radio" name="approval_{i}"> Reprovado</label>
            </div>
            <div class="approval-note">Observações: _______________________________________________</div>
          </div>
        </div>"""

    tags = [fd["objective"], fd["tone"], f'CTA: {fd["cta"]}', fd.get("tipo_criativo", "")]
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags if t)
    client_line = f'<div style="font-size:.8rem;color:rgba(255,255,255,.6);margin-top:4px;">Cliente: {fd["client_name"]}</div>' if fd.get("client_name") else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Copies — {fd['product']}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',system-ui,sans-serif;background:#f0f3f8;color:#1a1a2e;padding:32px 16px}}
  .container{{max-width:820px;margin:0 auto}}
  .ph{{background:linear-gradient(135deg,#003f7c,#1a5a9a);border-radius:16px;padding:28px 32px;color:#fff;margin-bottom:24px}}
  .nl{{font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.65);margin-bottom:4px}}
  .pn{{font-size:1.5rem;font-weight:700}}
  .tags{{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}}
  .tag{{background:rgba(255,255,255,.12);color:rgba(255,255,255,.9);font-size:.75rem;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.2)}}
  .card{{background:#fff;border:1px solid #dde3ed;border-radius:16px;margin-bottom:20px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
  .card-accent{{height:4px}}
  .card-inner{{padding:22px 26px 20px}}
  .card-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
  .copy-num{{font-size:.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#9ca3af}}
  .badge{{font-size:.78rem;font-weight:700;padding:4px 14px;border-radius:20px}}
  .slabel{{font-size:.65rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#9ca3af;margin-bottom:4px}}
  .hook{{font-size:1.05rem;font-weight:700;line-height:1.45;padding-left:12px;border-left:3px solid;margin-bottom:14px;color:#1a1a2e}}
  .body-text{{font-size:.92rem;color:#374151;line-height:1.7;margin-bottom:14px}}
  .cta-box{{display:inline-block;padding:7px 18px;border-radius:8px;font-size:.88rem;font-weight:700;margin-bottom:4px}}
  .criativo-box{{background:#f8fafc;border:1px solid #e5e9f0;border-radius:8px;padding:12px 14px;font-size:.9rem;color:#374151;line-height:1.65}}
  .approval-box{{background:#f8fafc;border:1px dashed #dde3ed;border-radius:10px;padding:14px 18px;margin-top:8px}}
  .approval-label{{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#9ca3af;margin-bottom:8px}}
  .approval-options{{display:flex;gap:20px;font-size:.85rem;color:#374151;margin-bottom:8px}}
  .approval-options label{{display:flex;align-items:center;gap:6px;cursor:pointer}}
  .approval-note{{font-size:.82rem;color:#9ca3af;padding-top:8px;border-top:1px solid #e5e9f0}}
  .pf{{text-align:center;margin-top:32px;font-size:.78rem;color:#9ca3af}}
</style>
</head>
<body>
<div class="container">
  <div class="ph">
    <div class="nl">{fd['niche']} › {fd['sub_niche']}</div>
    <div class="pn">{fd['product']}</div>
    {client_line}
    <div class="tags">{tags_html}</div>
  </div>
  {cards_html}
  <div class="pf">Gerado por Copy Generator · Dash Digital</div>
</div>
</body>
</html>"""


# ── Session state ──────────────────────────────────────────────────────────────
for key, default in [
    ("copies", None),
    ("form_data", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── SIDEBAR — copies ───────────────────────────────────────────────────────────
with st.sidebar:
    _logo_b64 = get_logo_base64()
    if _logo_b64:
        st.markdown(
            f'<div class="sb-brand"><img src="data:image/png;base64,{_logo_b64}" '
            f'style="height:38px;"></div>'
            f'<hr class="sb-divider">',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("""
    <div class="sb-brand">
      <span class="sb-icon">✍️</span>
      <div>
        <div class="sb-title">Copy Generator</div>
        <div class="sb-sub">Meta Ads · Dash Digital</div>
      </div>
    </div>
    <hr class="sb-divider">
    """, unsafe_allow_html=True)

    if st.session_state.copies:
        fd = st.session_state.form_data
        copies = st.session_state.copies
        criativo_label = CRIATIVO_LABELS.get(fd.get("tipo_criativo", ""), "Copy do Criativo")

        st.markdown(get_sidebar_copy_header_html(fd), unsafe_allow_html=True)

        for i, copy in enumerate(copies, 1):
            tipo_nome = copy.get("tipo_nome", f"Copy {i}")
            with st.expander(f"Copy {i} — {tipo_nome}"):
                st.markdown('<div class="copy-block-label">Legenda</div>', unsafe_allow_html=True)
                st.text_area("leg", value=copy.get("legenda_completa", ""),
                             height=165, label_visibility="collapsed", key=f"leg_{i}")
                st.markdown(f'<div class="copy-block-label">{criativo_label}</div>', unsafe_allow_html=True)
                st.text_area("cri", value=copy.get("criativo", ""),
                             height=110, label_visibility="collapsed", key=f"cri_{i}")

                # ── Campo de campanha (para fechar o loop de performance) ─────
                campaign_input = st.text_input(
                    "🔗 Campanha (opcional)",
                    placeholder="Ex: Nutrição Maio · Captação Leads",
                    key=f"campaign_{i}",
                    help="Nomeie a campanha onde essa copy será usada. "
                         "Quando o relatório for gerado, o CTR real aparecerá aqui.",
                )

                col_ap1, col_ap2 = st.columns(2)
                status_key    = f"approval_{i}"
                rejecting_key = f"rejecting_{i}"
                if status_key not in st.session_state:
                    st.session_state[status_key] = None
                if rejecting_key not in st.session_state:
                    st.session_state[rejecting_key] = False

                with col_ap1:
                    if st.button("✅ Aprovar", key=f"btn_aprove_{i}", use_container_width=True):
                        st.session_state[status_key]   = "aprovada"
                        st.session_state[rejecting_key] = False
                        save_approved_copy(
                            st.session_state.form_data, copy, i,
                            campaign_name=campaign_input.strip(),
                        )
                        load_saved.clear()
                with col_ap2:
                    if st.button("❌ Rejeitar", key=f"btn_reject_{i}", use_container_width=True):
                        if st.session_state[status_key] != "rejeitada":
                            st.session_state[rejecting_key] = True

                # ── Fluxo de rejeição: campo de motivo ────────────────────────
                if st.session_state[rejecting_key]:
                    reason_input = st.text_area(
                        "Motivo da rejeição",
                        placeholder="Ex: tom muito agressivo, não combina com o cliente, hook fraco...",
                        key=f"reason_{i}",
                        height=80,
                    )
                    rc1, rc2 = st.columns(2)
                    with rc1:
                        if st.button("Confirmar rejeição", key=f"btn_confirm_reject_{i}", use_container_width=True, type="primary"):
                            if reason_input.strip():
                                st.session_state[status_key]   = "rejeitada"
                                st.session_state[rejecting_key] = False
                                save_rejected_copy(st.session_state.form_data, copy, i, reason_input.strip())
                                load_saved.clear()
                            else:
                                st.warning("Escreva o motivo antes de confirmar.")
                    with rc2:
                        if st.button("Cancelar", key=f"btn_cancel_reject_{i}", use_container_width=True):
                            st.session_state[rejecting_key] = False

                status = st.session_state.get(status_key)
                if status:
                    color_map = {"aprovada": "#d1fae5", "rejeitada": "#fee2e2"}
                    text_map  = {"aprovada": "#065f46", "rejeitada": "#991b1b"}
                    label_map = {"aprovada": "APROVADA", "rejeitada": "REJEITADA"}
                    st.markdown(
                        f'<div style="background:{color_map.get(status,"#f3f4f6")};'
                        f'color:{text_map.get(status,"#374151")};'
                        f'font-size:.75rem;font-weight:700;padding:4px 12px;border-radius:8px;'
                        f'text-align:center;margin-top:4px;">Status: {label_map.get(status, status.upper())}</div>',
                        unsafe_allow_html=True,
                    )

            score = copy.get("hook_score", "")
            if score:
                st.markdown(
                    f'<div style="font-size:.72rem;color:rgba(255,255,255,.55);margin-top:2px;">🎯 Hook: {score}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        st.download_button(
            label="Baixar todas em HTML",
            data=_build_download_html(copies, fd),
            file_name=f"copies_{fd['product'][:20].replace(' ','_').lower()}.html",
            mime="text/html",
            use_container_width=True,
        )
        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        if st.button("Gerar novamente", use_container_width=True):
            with st.spinner("Gerando..."):
                try:
                    st.session_state.copies = generate_copies(st.session_state.form_data)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown(get_sidebar_welcome_html(), unsafe_allow_html=True)


# ── MAIN — briefing ────────────────────────────────────────────────────────────
st.markdown(get_page_header_html(), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — Modo de uso (cliente ou consulta avulsa)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="client-section"><div class="form-section-title">Modo de uso</div>', unsafe_allow_html=True)

modo = st.radio("", ["Consulta avulsa", "Cliente cadastrado"],
                horizontal=True, label_visibility="collapsed", key="modo")

# Limpa campos do briefing ao trocar para modo avulso para evitar
# que conteúdo de sessões de clientes anteriores contamine a geração.
if st.session_state.get("_last_modo") != modo:
    if modo == "Consulta avulsa":
        for _wk in ("criativo_estrutura", "referencias"):
            if st.session_state.get(_wk):
                st.session_state[_wk] = ""
    st.session_state["_last_modo"] = modo

selected_client = None

if modo == "Cliente cadastrado":
    st.info("📋 Lembre-se de upar o relatório de performance mais recente do cliente para melhorar as copies.")

    all_clients = load_clients()

    if all_clients:
        names = [c["name"] for c in all_clients]
        chosen = st.selectbox("Selecionar cliente", names,
                              label_visibility="collapsed", key="chosen_client")
        selected_client = next((c for c in all_clients if c["name"] == chosen), None)
    else:
        st.info("Nenhum cliente cadastrado. Acesse **Gerenciar Clientes** no hub para cadastrar.")

    if selected_client:
        has_tov = bool(selected_client.get("tone_of_voice", "").strip())
        badge = "Tom de voz carregado" if has_tov else "Sem tom de voz"
        color = "#d1fae5" if has_tov else "#fef3c7"
        text_color = "#065f46" if has_tov else "#92400e"
        col_badge, col_del = st.columns([5, 1])
        with col_badge:
            st.markdown(
                f'<span style="background:{color};color:{text_color};font-size:.75rem;'
                f'font-weight:700;padding:4px 12px;border-radius:20px;">{badge}</span>',
                unsafe_allow_html=True,
            )
        with col_del:
            if st.button("🗑️ Excluir", key="btn_delete_client", use_container_width=True):
                st.session_state["confirm_delete"] = selected_client["name"]

        if st.session_state.get("confirm_delete") == selected_client["name"]:
            st.warning(f"Tem certeza que deseja excluir **{selected_client['name']}**? Esta ação não pode ser desfeita.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ Sim, excluir", key="btn_confirm_delete", use_container_width=True):
                    _del_key = selected_client.get("key", "").strip()
                    if not _del_key:
                        st.session_state["confirm_delete"] = None
                        st.error("Este cliente não possui identificador (key) — exclusão não é possível. Verifique o cadastro.")
                        st.rerun()
                    ok, msg = delete_client_supabase(_del_key, selected_client["name"])
                    st.session_state["confirm_delete"] = None
                    if ok:
                        st.success(f"Cliente '{selected_client['name']}' desativado.")
                    else:
                        st.error(msg)
                    st.rerun()
            with col_no:
                if st.button("Cancelar", key="btn_cancel_delete", use_container_width=True):
                    st.session_state["confirm_delete"] = None
                    st.rerun()

        # ── Painel: métricas do último relatório automático ───────────────
        _client_key_panel = selected_client.get("key", "")
        _metrics_raw = load_latest_report_metrics(_client_key_panel) if _client_key_panel else ""
        if _metrics_raw:
            with st.expander("📊 Último relatório automático — dados que a IA vai usar", expanded=False):
                st.markdown(
                    f'<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;'
                    f'padding:12px 16px;font-size:.82rem;white-space:pre-wrap;color:#374151;line-height:1.7;">'
                    f'{_metrics_raw}</div>',
                    unsafe_allow_html=True,
                )
                st.caption("Esses dados são injetados automaticamente no prompt toda vez que você gerar copies para este cliente.")
        else:
            with st.expander("📊 Contexto de performance — complementar (opcional)", expanded=False):
                st.caption("Ainda não há relatório automático para este cliente. Cole dados manualmente para enriquecer a IA enquanto o histórico não acumula.")
                report_manual = st.text_area(
                    "Dados de performance (opcional)",
                    height=80, key="report_manual",
                    placeholder="Ex: CTR médio 2.1%, CPM R$18, melhor formato: Reels, público 25-34 anos..."
                )
                if st.button("💾 Salvar contexto", use_container_width=True, key="btn_save_report"):
                    if report_manual.strip():
                        ok, msg = save_performance_context(selected_client["name"], report_manual.strip())
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Digite algum contexto antes de salvar.")

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — Nicho & Produto
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-section"><div class="form-section-title">Nicho & Produto</div>', unsafe_allow_html=True)

_client_nicho     = selected_client.get("nicho", "") if selected_client else ""
_client_sub_nicho = selected_client.get("sub_nicho", "") if selected_client else ""
_niche_keys       = list(NICHES.keys())
_niche_index      = _niche_keys.index(_client_nicho) if _client_nicho in _niche_keys else 0

col1, col2 = st.columns(2)
with col1:
    niche = st.selectbox("Nicho", options=_niche_keys,
                         format_func=lambda x: f"{NICHES[x]['icon']} {x}",
                         index=_niche_index, key="niche")
with col2:
    _sub_opts  = NICHES[niche]["sub"]
    _sub_index = _sub_opts.index(_client_sub_nicho) if _client_sub_nicho in _sub_opts else 0
    sub_niche  = st.selectbox("Sub-nicho", options=_sub_opts, index=_sub_index, key="sub_niche")

niche_data = NICHES[niche]
col3, col4 = st.columns(2)
with col3:
    product = st.text_input("Produto ou Serviço",
                            placeholder="Ex: Consultoria de emagrecimento online", key="product")
with col4:
    _pub_default = selected_client.get("publico_alvo", "") if selected_client else ""
    audience = st.text_input(
        "Público-Alvo",
        value=_pub_default,
        placeholder="Ex: Mulheres 30-50 que já tentaram dieta",
        key="audience",
        help="Auto-preenchido com o público-alvo cadastrado. Edite se necessário.",
    )

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — Dor, Desejo & Oferta
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-section"><div class="form-section-title">Dor, Desejo & Oferta</div>', unsafe_allow_html=True)

dor_ph    = niche_data["dores_comuns"][0]   if niche_data["dores_comuns"]   else ""
desejo_ph = niche_data["desejos_comuns"][0] if niche_data["desejos_comuns"] else ""

col5, col6 = st.columns(2)
with col5:
    pain = st.text_area("Principal Dor / Problema", placeholder=f"Ex: {dor_ph}",
                        height=90, key="pain")
with col6:
    desire = st.text_area("Principal Desejo", placeholder=f"Ex: {desejo_ph}",
                          height=90, key="desire")

col7, col8 = st.columns(2)
with col7:
    usp = st.text_area("Diferencial / USP",
                       placeholder="O que torna esse produto único?",
                       height=90, key="usp")
with col8:
    offer = st.text_input("Oferta / Preço (opcional)",
                          placeholder="Ex: 3x de R$97 | Primeira semana grátis", key="offer")

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — Configurações do Anúncio
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-section"><div class="form-section-title">Configurações do Anúncio</div>', unsafe_allow_html=True)

col9, col10, col11 = st.columns(3)
with col9:
    objective = st.selectbox("Objetivo", options=list(OBJECTIVES.keys()), key="objective")
with col10:
    # Se cliente tem tom de voz, mostra aviso; caso contrário, mostra selectbox
    if selected_client and selected_client.get("tone_of_voice"):
        st.markdown("**Tom de Voz**")
        st.markdown(
            f'<span style="background:#d1fae5;color:#065f46;font-size:.78rem;'
            f'font-weight:600;padding:5px 12px;border-radius:8px;display:inline-block;">'
            f'Definido pelo perfil de {selected_client["name"]}</span>',
            unsafe_allow_html=True,
        )
        tone = "Definido pelo perfil do cliente"
    else:
        tone = st.selectbox("Tom de Voz", options=TONES, key="tone")
with col11:
    cta = st.selectbox("CTA", options=CTAS, key="cta")

extra_keywords = st.text_input(
    "Palavras-chave / Diferenciais adicionais (opcional)",
    placeholder="Ex: sem glúten, aprovado por nutricionistas, entrega em 24h",
    key="extra_keywords",
)

sazonalidade = st.text_input(
    "Sazonalidade / Contexto de data (opcional)",
    placeholder="Ex: Black Friday, Volta às aulas, Dia das Mães, Carnaval...",
    key="sazonalidade",
)

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 — Criativo
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-section"><div class="form-section-title">Criativo</div>', unsafe_allow_html=True)

tipo_criativo = st.radio(
    "Tipo de criativo",
    options=["Card (imagem)", "Vídeo", "Carrossel"],
    horizontal=True,
    key="tipo_criativo",
)

formato_anuncio = st.radio(
    "Formato / Placement",
    options=FORMAT_OPTIONS,
    horizontal=True,
    key="formato_anuncio",
    help="Onde o anúncio vai aparecer — determina limites de texto e estrutura ideal da copy.",
)

criativo_estrutura = st.text_area(
    "Estrutura do criativo",
    placeholder=(
        "Descreva o que vai ter no criativo para que a copy seja exata.\n\n"
        "Exemplos:\n"
        "• Vídeo de 30s — médica fala para câmera nos primeiros 5s, depois mostra resultado de paciente\n"
        "• Card — headline grande no topo, subheadline abaixo, botão CTA no rodapé\n"
        "• Carrossel de 4 slides — slide 1: problema, slides 2-3: benefícios, slide 4: oferta"
    ),
    height=110,
    key="criativo_estrutura",
)

referencias = st.text_area(
    "Referências de copy (opcional)",
    placeholder="Cole copies ou anúncios que já funcionaram bem. O modelo usa como referência de tom — não copia.",
    height=80,
    key="referencias",
)

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BOTÃO GERAR
# ══════════════════════════════════════════════════════════════════════════════
if st.button("Gerar 5 Copies", use_container_width=True):
    if not product.strip():
        st.error("Preencha o campo Produto ou Serviço.")
    else:
        if not criativo_estrutura.strip():
            st.warning("Sem estrutura do criativo — o modelo vai usar seu julgamento para o tipo selecionado.")

        with st.spinner("Gerando copies com IA..."):
            try:
                # ── Busca histórico de copies do cliente ──────────────────
                client_approved = []
                client_rejected = []
                client_report_metrics = ""
                client_rejection_patterns = ""
                if selected_client:
                    all_saved = load_saved(client_name=selected_client["name"], limit=20)
                    client_approved = [c for c in all_saved if c.get("status") == "aprovada"]
                    client_rejected = [c for c in all_saved if c.get("status") == "rejeitada"]
                    # Métricas reais do último relatório gerado
                    client_key = selected_client.get("key", "")
                    if client_key:
                        client_report_metrics = load_latest_report_metrics(client_key)
                    # Padrões de rejeição agregados
                    client_rejection_patterns = get_rejection_patterns(selected_client["name"])

                # ── Enriquece copies aprovadas com CTR real da campanha ───────
                _client_key = selected_client.get("key", "") if selected_client else ""
                for _copy in client_approved:
                    _camp = (_copy.get("campaign_name") or "").strip()
                    if _camp and _client_key:
                        _perf = get_campaign_performance(_client_key, _camp)
                        _copy["campaign_ctr"] = _perf["ctr"] if _perf else 0
                    else:
                        _copy["campaign_ctr"] = 0

                form_data = {
                    "niche": niche,
                    "sub_niche": sub_niche,
                    "product": product.strip(),
                    "audience": audience.strip() or f"Público interessado em {product}",
                    "pain": pain.strip() or niche_data["dores_comuns"][0],
                    "desire": desire.strip() or niche_data["desejos_comuns"][0],
                    "usp": usp.strip(),
                    "offer": offer.strip(),
                    "objective": objective,
                    "objective_desc": OBJECTIVES[objective],
                    "tone": tone,
                    "cta": cta,
                    "extra_keywords": extra_keywords.strip(),
                    "sazonalidade": sazonalidade.strip(),
                    "tipo_criativo": tipo_criativo,
                    "formato_anuncio": formato_anuncio,
                    "criativo_estrutura": criativo_estrutura.strip(),
                    "referencias": referencias.strip(),
                    "niche_data": niche_data,
                    # ── Dados do cliente ──────────────────────────────────
                    "client_name":          selected_client["name"] if selected_client else "",
                    "client_key":           selected_client.get("key", "") if selected_client else "",
                    "client_tone_of_voice": selected_client.get("tone_of_voice", "") if selected_client else "",
                    "client_bio":           selected_client.get("bio", "") if selected_client else "",
                    "client_tags":          selected_client.get("tags", []) if selected_client else [],
                    "client_observations":  selected_client.get("observations", "") if selected_client else "",
                    "client_goals":         selected_client.get("goals", {}) if selected_client else {},
                    "client_competitors":         selected_client.get("competitors", "") if selected_client else "",
                    "client_publico_alvo":        selected_client.get("publico_alvo", "") if selected_client else "",
                    "client_performance_context": selected_client.get("performance_context", "") if selected_client else "",
                    "client_report_metrics":      client_report_metrics,
                    # ── Histórico de copies (com CTR enriquecido) ─────────
                    "client_approved_copies":    client_approved,
                    "client_rejected_copies":    client_rejected,
                    "client_rejection_patterns": client_rejection_patterns,
                }
                copies = generate_copies(form_data)
                st.session_state.copies = copies
                st.session_state.form_data = form_data
                # Limpa status individuais da sessão anterior
                for _k in [f"approval_{j}" for j in range(1, 6)]:
                    st.session_state.pop(_k, None)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar copies: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# HISTÓRICO DE COPIES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
with st.expander("📋 Banco de Copies Salvas", expanded=False):
    tab_apr, tab_rej = st.tabs(["✅ Aprovadas", "❌ Rejeitadas"])

    with tab_apr:
        aprovadas = load_saved(status="aprovada", limit=50)
        if not aprovadas:
            st.info("Nenhuma copy aprovada ainda. Clique em ✅ Aprovar para salvar.")
        else:
            for row in aprovadas:
                created       = row.get("created_at", "")[:10] if row.get("created_at") else ""
                client_str    = f" · {row['client_name']}" if row.get("client_name") else ""
                campaign_name = row.get("campaign_name", "").strip()
                camp_label    = f" · 🔗 {campaign_name}" if campaign_name else ""
                with st.expander(f"**{row.get('product','Sem título')}**{client_str}{camp_label} — {row.get('tipo_nome','')} — {created}", expanded=False):
                    st.markdown(f'<div style="font-size:.78rem;color:#6b7280;margin-bottom:10px;">{row.get("niche","")} · {row.get("objective","")} · {row.get("tipo_criativo","")}</div>', unsafe_allow_html=True)

                    # ── Performance real da campanha (loop fechado) ────────────
                    if campaign_name and row.get("client_key"):
                        perf = get_campaign_performance(row["client_key"], campaign_name)
                        if perf:
                            status_map = {
                                "best":    ("✅ Melhor desempenho", "#d1fae5", "#065f46"),
                                "warning": ("⚠️ Atenção — CTR baixo", "#fef3c7", "#92400e"),
                                "ok":      ("📊 Regular", "#eff6ff", "#1e40af"),
                                "ended":   ("⏹️ Encerrada", "#f3f4f6", "#374151"),
                            }
                            s_label, s_bg, s_color = status_map.get(perf["status"], ("", "#f3f4f6", "#374151"))
                            st.markdown(
                                f'<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:10px;'
                                f'padding:10px 14px;margin-bottom:12px;font-size:.83rem;">'
                                f'<strong style="color:#15803d;">📈 Performance real — {perf["name"]}</strong>'
                                f'<span style="float:right;background:{s_bg};color:{s_color};'
                                f'padding:2px 8px;border-radius:6px;font-size:.75rem;font-weight:700;">{s_label}</span>'
                                f'<br><span style="color:#374151;">CTR <strong>{perf["ctr"]}%</strong>'
                                f' &nbsp;·&nbsp; CPM <strong>R${perf["cpm"]:.2f}</strong>'
                                f' &nbsp;·&nbsp; CPC <strong>R${perf["cpc"]:.2f}</strong>'
                                f' &nbsp;·&nbsp; Gasto <strong>R${perf["spend"]:.2f}</strong></span>'
                                f'<br><span style="color:#9ca3af;font-size:.72rem;">Período: {perf["period"]}</span>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                        elif campaign_name:
                            st.markdown(
                                f'<div style="background:#fafafa;border:1px solid #e5e7eb;border-radius:8px;'
                                f'padding:8px 12px;margin-bottom:10px;font-size:.78rem;color:#6b7280;">'
                                f'🔗 Campanha <strong>{campaign_name}</strong> — aguardando dados do relatório</div>',
                                unsafe_allow_html=True,
                            )

                    if row.get("legenda_hook"):
                        st.markdown("**Hook**"); st.code(row["legenda_hook"], language=None)
                    if row.get("legenda_corpo"):
                        st.markdown("**Corpo**"); st.code(row["legenda_corpo"], language=None)
                    if row.get("legenda_cta"):
                        st.markdown("**CTA**"); st.code(row["legenda_cta"], language=None)
                    if row.get("criativo"):
                        st.markdown("**Criativo**"); st.code(row["criativo"], language=None)

    with tab_rej:
        rejeitadas = load_saved(status="rejeitada", limit=50)
        if not rejeitadas:
            st.info("Nenhuma copy rejeitada ainda.")
        else:
            for row in rejeitadas:
                created    = row.get("created_at", "")[:10] if row.get("created_at") else ""
                client_str = f" · {row['client_name']}" if row.get("client_name") else ""
                with st.expander(f"**{row.get('product','Sem título')}**{client_str} — {row.get('tipo_nome','')} — {created}", expanded=False):
                    st.markdown(f'<div style="font-size:.78rem;color:#6b7280;margin-bottom:10px;">{row.get("niche","")} · {row.get("objective","")} · {row.get("tipo_criativo","")}</div>', unsafe_allow_html=True)
                    if row.get("reason"):
                        st.markdown(f'<div style="background:#fee2e2;color:#991b1b;border-radius:8px;padding:8px 12px;font-size:.85rem;margin-bottom:10px;">❌ Motivo: {row["reason"]}</div>', unsafe_allow_html=True)
                    if row.get("legenda_completa"):
                        st.code(row["legenda_completa"], language=None)

st.markdown(
    '<p style="text-align:center;font-size:.72rem;color:#9ca3af;margin-top:16px;">'
    "Desenvolvido por Dash Digital · @dashdgt · Todos os direitos reservados</p>",
    unsafe_allow_html=True,
)
