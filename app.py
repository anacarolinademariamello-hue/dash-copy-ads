import streamlit as st

from src.niches import NICHES, OBJECTIVES, TONES, CTAS
from src.copy_gen import generate_copies, COPY_TYPES
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


# ── HTML de download ───────────────────────────────────────────────────────────
def _build_download_html(copies: list, fd: dict) -> str:
    cards_html = ""
    for i, copy in enumerate(copies, 1):
        cor = copy.get("cor", "#003f7c")
        cor_bg = copy.get("cor_bg", "#eff6ff")
        tipo_nome = copy.get("tipo_nome", "")
        hook = copy.get("legenda_hook", "").replace("<", "&lt;").replace(">", "&gt;")
        body = (
            copy.get("legenda_corpo", "")
            .replace("<", "&lt;").replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        cta_text = copy.get("legenda_cta", "").replace("<", "&lt;").replace(">", "&gt;")
        legenda = copy.get("legenda_completa", "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        criativo = copy.get("criativo", "").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

        cards_html += f"""
        <div class="card">
          <div class="card-accent" style="background:linear-gradient(90deg,{cor},{cor}88)"></div>
          <div class="card-inner">
            <div class="card-header">
              <span class="copy-num">Copy {i} de 5</span>
              <span class="badge" style="background:{cor_bg};color:{cor}">{tipo_nome}</span>
            </div>
            <div class="section-label">Legenda — Hook</div>
            <div class="hook" style="border-color:{cor}">{hook}</div>
            <div class="section-label">Legenda — Corpo</div>
            <div class="body-text">{body}</div>
            <div class="section-label">CTA</div>
            <div class="cta-box" style="background:{cor_bg};color:{cor}">{cta_text}</div>
            <div class="section-label" style="margin-top:18px;padding-top:14px;border-top:1px solid #eef1f6;">Copy do Criativo</div>
            <div class="criativo-box">{criativo}</div>
          </div>
        </div>"""

    tags = [fd["objective"], fd["tone"], f'CTA: {fd["cta"]}']
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Copies Meta Ads — {fd['product']}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',system-ui,sans-serif;background:#f0f3f8;color:#1a1a2e;padding:32px 16px}}
  .container{{max-width:820px;margin:0 auto}}
  .page-header{{background:linear-gradient(135deg,#003f7c,#1a5a9a);border-radius:16px;padding:28px 32px;color:#fff;margin-bottom:24px}}
  .niche-label{{font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.65);margin-bottom:4px}}
  .product-name{{font-size:1.5rem;font-weight:700}}
  .tags{{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}}
  .tag{{background:rgba(255,255,255,.12);color:rgba(255,255,255,.9);font-size:.75rem;padding:4px 12px;border-radius:20px;border:1px solid rgba(255,255,255,.2)}}
  .card{{background:#fff;border:1px solid #dde3ed;border-radius:16px;margin-bottom:20px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
  .card-accent{{height:4px}}
  .card-inner{{padding:22px 26px 20px}}
  .card-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
  .copy-num{{font-size:.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#9ca3af}}
  .badge{{font-size:.78rem;font-weight:700;padding:4px 14px;border-radius:20px}}
  .section-label{{font-size:.65rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#9ca3af;margin-bottom:4px}}
  .hook{{font-size:1.05rem;font-weight:700;line-height:1.45;padding-left:12px;border-left:3px solid;margin-bottom:14px;color:#1a1a2e}}
  .body-text{{font-size:.92rem;color:#374151;line-height:1.7;margin-bottom:14px}}
  .cta-box{{display:inline-block;padding:7px 18px;border-radius:8px;font-size:.88rem;font-weight:700;margin-bottom:4px}}
  .criativo-box{{background:#f8fafc;border:1px solid #e5e9f0;border-radius:8px;padding:12px 14px;font-size:.9rem;color:#374151;line-height:1.65;white-space:pre-line}}
  .page-footer{{text-align:center;margin-top:32px;font-size:.78rem;color:#9ca3af}}
</style>
</head>
<body>
<div class="container">
  <div class="page-header">
    <div class="niche-label">{fd['niche']} › {fd['sub_niche']}</div>
    <div class="product-name">{fd['product']}</div>
    <div class="tags">{tags_html}</div>
  </div>
  {cards_html}
  <div class="page-footer">Gerado por Copy Generator · Dash Digital</div>
</div>
</body>
</html>"""


# ── Session state ──────────────────────────────────────────────────────────────
if "copies" not in st.session_state:
    st.session_state.copies = None
if "form_data" not in st.session_state:
    st.session_state.form_data = None

# ── SIDEBAR — exibe copies geradas ────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sb-brand">
          <span class="sb-icon">✍️</span>
          <div>
            <div class="sb-title">Copy Generator</div>
            <div class="sb-sub">Meta Ads · Dash Digital</div>
          </div>
        </div>
        <hr class="sb-divider">
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.copies:
        fd = st.session_state.form_data
        copies = st.session_state.copies

        st.markdown(get_sidebar_copy_header_html(fd), unsafe_allow_html=True)

        type_map = {c["id"]: c for c in COPY_TYPES}

        for i, copy in enumerate(copies, 1):
            tid = copy.get("tipo_id", "")
            tipo_nome = copy.get("tipo_nome", f"Copy {i}")
            cor = copy.get("cor", "#003f7c")
            cor_bg = copy.get("cor_bg", "#eff6ff")

            with st.expander(f"Copy {i} — {tipo_nome}"):
                st.markdown(
                    f'<div class="copy-block-label">Legenda</div>',
                    unsafe_allow_html=True,
                )
                st.text_area(
                    label="leg",
                    value=copy.get("legenda_completa", ""),
                    height=160,
                    label_visibility="collapsed",
                    key=f"leg_{i}",
                )
                st.markdown(
                    '<div class="copy-block-label">Copy do Criativo</div>',
                    unsafe_allow_html=True,
                )
                st.text_area(
                    label="cri",
                    value=copy.get("criativo", ""),
                    height=100,
                    label_visibility="collapsed",
                    key=f"cri_{i}",
                )

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        html_content = _build_download_html(copies, fd)
        st.download_button(
            label="Baixar todas em HTML",
            data=html_content,
            file_name=f"copies_{fd['sub_niche'].split()[0].lower()}_{fd['product'][:15].replace(' ','_').lower()}.html",
            mime="text/html",
            use_container_width=True,
        )

        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

        if st.button("Gerar novamente", use_container_width=True):
            with st.spinner("Gerando novas copies..."):
                try:
                    st.session_state.copies = generate_copies(st.session_state.form_data)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    else:
        st.markdown(get_sidebar_welcome_html(), unsafe_allow_html=True)


# ── MAIN — briefing form ───────────────────────────────────────────────────────
st.markdown(get_page_header_html(), unsafe_allow_html=True)

# ── Seção 1: Nicho & Produto ───────────────────────────────────────────────────
st.markdown('<div class="form-section"><div class="form-section-title">Nicho & Produto</div>', unsafe_allow_html=True)

niche_names = list(NICHES.keys())
col1, col2 = st.columns(2)

with col1:
    niche = st.selectbox(
        "Nicho",
        options=niche_names,
        format_func=lambda x: f"{NICHES[x]['icon']} {x}",
        key="niche",
    )
with col2:
    sub_niche = st.selectbox(
        "Sub-nicho",
        options=NICHES[niche]["sub"],
        key="sub_niche",
    )

niche_data = NICHES[niche]
col3, col4 = st.columns(2)

with col3:
    product = st.text_input(
        "Produto ou Serviço",
        placeholder="Ex: Consultoria de emagrecimento online",
        key="product",
    )
with col4:
    audience = st.text_input(
        "Público-Alvo",
        placeholder="Ex: Mulheres 30-50, com sobrepeso, que já tentaram dieta",
        key="audience",
    )

st.markdown('</div>', unsafe_allow_html=True)

# ── Seção 2: Dor, Desejo & Oferta ─────────────────────────────────────────────
st.markdown('<div class="form-section"><div class="form-section-title">Dor, Desejo & Oferta</div>', unsafe_allow_html=True)

dor_ph = niche_data["dores_comuns"][0] if niche_data["dores_comuns"] else ""
desejo_ph = niche_data["desejos_comuns"][0] if niche_data["desejos_comuns"] else ""

col5, col6 = st.columns(2)
with col5:
    pain = st.text_area(
        "Principal Dor / Problema",
        placeholder=f"Ex: {dor_ph}",
        height=90,
        key="pain",
    )
with col6:
    desire = st.text_area(
        "Principal Desejo",
        placeholder=f"Ex: {desejo_ph}",
        height=90,
        key="desire",
    )

col7, col8 = st.columns(2)
with col7:
    usp = st.text_area(
        "Diferencial / USP",
        placeholder="O que torna esse produto único? Ex: acompanhamento individualizado, método próprio, garantia...",
        height=90,
        key="usp",
    )
with col8:
    offer = st.text_input(
        "Oferta / Preço (opcional)",
        placeholder="Ex: 3x de R$97 | Primeira semana grátis | De R$497 por R$197",
        key="offer",
    )

st.markdown('</div>', unsafe_allow_html=True)

# ── Seção 3: Configurações do Anúncio ─────────────────────────────────────────
st.markdown('<div class="form-section"><div class="form-section-title">Configurações do Anúncio</div>', unsafe_allow_html=True)

col9, col10, col11 = st.columns(3)
with col9:
    objective = st.selectbox("Objetivo", options=list(OBJECTIVES.keys()), key="objective")
with col10:
    tone = st.selectbox("Tom de Voz", options=TONES, key="tone")
with col11:
    cta = st.selectbox("CTA", options=CTAS, key="cta")

extra_keywords = st.text_input(
    "Palavras-chave / Diferenciais adicionais (opcional)",
    placeholder="Ex: sem glúten, aprovado por nutricionistas, entrega em 24h",
    key="extra_keywords",
)

st.markdown('</div>', unsafe_allow_html=True)

# ── Seção 4: Criativo ──────────────────────────────────────────────────────────
st.markdown('<div class="form-section"><div class="form-section-title">Criativo</div>', unsafe_allow_html=True)

criativo_estrutura = st.text_area(
    "Estrutura do criativo",
    placeholder=(
        "Descreva o que vai ter no criativo para que a copy seja exata.\n\n"
        "Exemplos:\n"
        "• Vídeo de 30s — médica fala direto para câmera nos primeiros 5s, depois mostra resultado de paciente\n"
        "• Imagem estática — headline grande no topo, subheadline abaixo, botão CTA no final\n"
        "• Carrossel de 4 slides — slide 1: problema, slides 2-3: benefícios, slide 4: oferta"
    ),
    height=110,
    key="criativo_estrutura",
)

referencias = st.text_area(
    "Referências de copy (opcional)",
    placeholder=(
        "Cole aqui copies ou anúncios que já funcionaram bem para esse cliente ou nicho.\n"
        "O modelo vai usar como referência de tom e estilo — não vai copiar."
    ),
    height=90,
    key="referencias",
)

st.markdown('</div>', unsafe_allow_html=True)

# ── Botão gerar ────────────────────────────────────────────────────────────────
if st.button("Gerar 5 Copies", use_container_width=True):
    if not product.strip():
        st.error("Preencha o campo Produto ou Serviço.")
    else:
        if not criativo_estrutura.strip():
            st.warning("Sem estrutura do criativo — o modelo vai gerar uma sugestão genérica para essa parte.")
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
                    "criativo_estrutura": criativo_estrutura.strip(),
                    "referencias": referencias.strip(),
                    "niche_data": niche_data,
                }
                copies = generate_copies(form_data)
                st.session_state.copies = copies
                st.session_state.form_data = form_data
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar copies: {e}")

st.markdown(
    '<p style="text-align:center;font-size:.72rem;color:#9ca3af;margin-top:16px;">'
    "Powered by Claude AI · Dash Digital"
    "</p>",
    unsafe_allow_html=True,
)
