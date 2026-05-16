import streamlit as st
import base64

from src.niches import NICHES, OBJECTIVES, TONES, CTAS
from src.copy_gen import generate_copies, COPY_TYPES, CRIATIVO_LABELS
from src.clients import load_clients, save_client, delete_client, extract_text
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
    ("show_registration", False),
    ("pending_clients", []),   # clientes adicionados nesta sessão (antes do redeploy)
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

                col_ap1, col_ap2, col_ap3 = st.columns(3)
                status_key = f"approval_{i}"
                if status_key not in st.session_state:
                    st.session_state[status_key] = None

                with col_ap1:
                    if st.button("✅ Aprovar", key=f"btn_aprove_{i}", use_container_width=True):
                        st.session_state[status_key] = "aprovada"
                with col_ap2:
                    if st.button("🧪 Testar", key=f"btn_test_{i}", use_container_width=True):
                        st.session_state[status_key] = "em teste"
                with col_ap3:
                    if st.button("❌ Rejeitar", key=f"btn_reject_{i}", use_container_width=True):
                        st.session_state[status_key] = "rejeitada"

                status = st.session_state.get(status_key)
                if status:
                    color_map = {"aprovada": "#d1fae5", "em teste": "#fef3c7", "rejeitada": "#fee2e2"}
                    text_map = {"aprovada": "#065f46", "em teste": "#92400e", "rejeitada": "#991b1b"}
                    st.markdown(
                        f'<div style="background:{color_map[status]};color:{text_map[status]};'
                        f'font-size:.75rem;font-weight:700;padding:4px 12px;border-radius:8px;'
                        f'text-align:center;margin-top:4px;">Status: {status.upper()}</div>',
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

selected_client = None

if modo == "Cliente cadastrado":
    # Mescla clientes do GitHub com os adicionados nessa sessão
    db_clients = load_clients()
    session_clients = [c for c in st.session_state.pending_clients
                       if not any(d["name"] == c["name"] for d in db_clients)]
    all_clients = db_clients + session_clients

    col_sel, col_new = st.columns([3, 1])
    with col_sel:
        if all_clients:
            names = [c["name"] for c in all_clients]
            chosen = st.selectbox("Selecionar cliente", names,
                                  label_visibility="collapsed", key="chosen_client")
            selected_client = next((c for c in all_clients if c["name"] == chosen), None)
        else:
            st.info("Nenhum cliente cadastrado ainda. Clique em '+ Novo cliente' para cadastrar.")

    with col_new:
        if st.button("+ Novo cliente", use_container_width=True):
            st.session_state.show_registration = not st.session_state.show_registration

    if selected_client:
        has_tov = bool(selected_client.get("tone_of_voice", "").strip())
        badge = "Tom de voz carregado" if has_tov else "Sem tom de voz"
        color = "#d1fae5" if has_tov else "#fef3c7"
        text_color = "#065f46" if has_tov else "#92400e"
        st.markdown(
            f'<span style="background:{color};color:{text_color};font-size:.75rem;'
            f'font-weight:700;padding:4px 12px;border-radius:20px;">{badge}</span>',
            unsafe_allow_html=True,
        )
        st.info("📋 Lembre-se de upar o relatório de performance mais recente deste cliente para melhorar as copies.")

# ── Formulário de cadastro ─────────────────────────────────────────────────────
if st.session_state.show_registration:
    with st.expander("Cadastrar novo cliente", expanded=True):
        reg_col1, reg_col2 = st.columns(2)
        with reg_col1:
            new_name = st.text_input("Nome do cliente", key="reg_name",
                                     placeholder="Ex: Questão de Texto")
        with reg_col2:
            tov_file = st.file_uploader("Arquivo de tom de voz (PDF ou TXT)",
                                        type=["pdf", "txt"], key="reg_file")

        competitors = st.text_input(
            "Páginas concorrentes no Facebook (opcional)",
            key="reg_competitors",
            placeholder="Ex: Página Concorrente 1, Página Concorrente 2",
        )

        tov_manual = st.text_area(
            "Ou cole o guia de tom de voz aqui",
            height=100, key="reg_manual",
            placeholder="Descreva como a marca fala: palavras que usa, tom, o que evita, exemplos de frases..."
        )

        col_save, col_cancel = st.columns([2, 1])
        with col_save:
            if st.button("Salvar cliente", use_container_width=True, key="btn_save_client"):
                if not new_name.strip():
                    st.error("Informe o nome do cliente.")
                else:
                    tov_content = ""
                    if tov_file:
                        tov_content = extract_text(tov_file)
                    elif tov_manual.strip():
                        tov_content = tov_manual.strip()

                    new_client = {"name": new_name.strip(), "tone_of_voice": tov_content, "competitors": competitors.strip()}
                    ok, msg = save_client(new_client)
                    if ok:
                        st.success(msg)
                        st.session_state.pending_clients.append(new_client)
                        st.session_state.show_registration = False
                        st.rerun()
                    else:
                        st.error(msg)
        with col_cancel:
            if st.button("Cancelar", use_container_width=True, key="btn_cancel"):
                st.session_state.show_registration = False
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — Nicho & Produto
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="form-section"><div class="form-section-title">Nicho & Produto</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    niche = st.selectbox("Nicho", options=list(NICHES.keys()),
                         format_func=lambda x: f"{NICHES[x]['icon']} {x}", key="niche")
with col2:
    sub_niche = st.selectbox("Sub-nicho", options=NICHES[niche]["sub"], key="sub_niche")

niche_data = NICHES[niche]
col3, col4 = st.columns(2)
with col3:
    product = st.text_input("Produto ou Serviço",
                            placeholder="Ex: Consultoria de emagrecimento online", key="product")
with col4:
    audience = st.text_input("Público-Alvo",
                             placeholder="Ex: Mulheres 30-50 que já tentaram dieta", key="audience")

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
                    "criativo_estrutura": criativo_estrutura.strip(),
                    "referencias": referencias.strip(),
                    "niche_data": niche_data,
                    "client_name": selected_client["name"] if selected_client else "",
                    "client_tone_of_voice": (selected_client.get("tone_of_voice", "") if selected_client else ""),
                }
                copies = generate_copies(form_data)
                st.session_state.copies = copies
                st.session_state.form_data = form_data
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar copies: {e}")

st.markdown(
    '<p style="text-align:center;font-size:.72rem;color:#9ca3af;margin-top:16px;">'
    "Desenvolvido por Dash Digital · @dashdgt · Todos os direitos reservados</p>",
    unsafe_allow_html=True,
)
