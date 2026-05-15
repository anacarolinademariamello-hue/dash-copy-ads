import streamlit as st

from src.niches import NICHES, OBJECTIVES, TONES, CTAS, FORMAT_OPTIONS
from src.copy_gen import generate_copies
from src.styles import (
    get_sidebar_css,
    get_main_css,
    get_welcome_html,
    get_result_header_html,
    get_copy_card_html,
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


# ── Helpers ────────────────────────────────────────────────────────────────────
def _build_download_html(copies: list, fd: dict) -> str:
    cards_html = ""
    for i, copy in enumerate(copies, 1):
        cor = copy.get("cor", "#003f7c")
        cor_bg = copy.get("cor_bg", "#eff6ff")
        tipo_nome = copy.get("tipo_nome", "")
        tipo_emoji = copy.get("tipo_emoji", "")
        hook = copy.get("hook", "").replace("<", "&lt;").replace(">", "&gt;")
        body = (
            copy.get("corpo", "")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        cta_text = copy.get("cta_texto", "").replace("<", "&lt;").replace(">", "&gt;")
        full = copy.get("copy_completa", "")
        chars = len(full)

        cards_html += f"""
        <div class="card">
          <div class="card-accent" style="background:linear-gradient(90deg,{cor},{cor}88)"></div>
          <div class="card-inner">
            <div class="card-header">
              <span class="copy-num">Copy {i} de 5</span>
              <span class="badge" style="background:{cor_bg};color:{cor}">{tipo_emoji} {tipo_nome}</span>
            </div>
            <div class="label" style="color:{cor}">Hook</div>
            <div class="hook" style="border-color:{cor}">{hook}</div>
            <div class="label" style="color:{cor}">Corpo</div>
            <div class="body">{body}</div>
            <div class="label" style="color:{cor}">CTA</div>
            <div class="cta-box" style="background:{cor_bg};color:{cor}">{cta_text}</div>
            <div class="footer"><span class="chars">{chars} caracteres</span></div>
          </div>
        </div>"""

    tags = [fd["objective"], fd["format_type"], fd["tone"], fd["cta"]]
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
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
  .card-inner{{padding:22px 26px 18px}}
  .card-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
  .copy-num{{font-size:.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#9ca3af}}
  .badge{{font-size:.78rem;font-weight:700;padding:4px 14px;border-radius:20px}}
  .label{{font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px}}
  .hook{{font-size:1.05rem;font-weight:700;line-height:1.45;padding-left:12px;border-left:3px solid;margin-bottom:14px;color:#1a1a2e}}
  .body{{font-size:.92rem;color:#374151;line-height:1.7;margin-bottom:14px}}
  .cta-box{{display:inline-block;padding:7px 18px;border-radius:8px;font-size:.88rem;font-weight:700;margin-bottom:12px}}
  .footer{{display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid #f0f3f8}}
  .chars{{font-size:.7rem;color:#9ca3af}}
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

# ── Sidebar ────────────────────────────────────────────────────────────────────
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

    # ── Nicho ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="sb-section-label">Nicho & Produto</div>', unsafe_allow_html=True)

    niche_names = list(NICHES.keys())
    niche = st.selectbox(
        "Nicho",
        options=niche_names,
        format_func=lambda x: f"{NICHES[x]['icon']} {x}",
        label_visibility="collapsed",
        key="niche",
    )

    sub_niche = st.selectbox(
        "Sub-nicho",
        options=NICHES[niche]["sub"],
        label_visibility="collapsed",
        key="sub_niche",
    )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sb-section-label">Sobre o Produto</div>', unsafe_allow_html=True)

    niche_data = NICHES[niche]
    dor_ph = niche_data["dores_comuns"][0] if niche_data["dores_comuns"] else "Descreva a principal dor"
    desejo_ph = niche_data["desejos_comuns"][0] if niche_data["desejos_comuns"] else "Descreva o principal desejo"

    product = st.text_input(
        "Produto ou Serviço",
        placeholder="Ex: Curso online de nutrição funcional",
        key="product",
    )
    audience = st.text_input(
        "Público-Alvo",
        placeholder="Ex: Mulheres 25-45, mães que querem emagrecer",
        key="audience",
    )
    pain = st.text_area(
        "Principal Dor / Problema",
        placeholder=f"Ex: {dor_ph}",
        height=80,
        key="pain",
    )
    desire = st.text_area(
        "Principal Desejo",
        placeholder=f"Ex: {desejo_ph}",
        height=80,
        key="desire",
    )
    usp = st.text_area(
        "Diferencial / USP",
        placeholder="Ex: Método exclusivo com cardápio personalizado + suporte semanal",
        height=80,
        key="usp",
    )
    offer = st.text_input(
        "Oferta / Preço (opcional)",
        placeholder="Ex: 3x de R$97 | Grátis por 7 dias",
        key="offer",
    )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)
    st.markdown('<div class="sb-section-label">Configurações do Anúncio</div>', unsafe_allow_html=True)

    objective = st.selectbox(
        "Objetivo",
        options=list(OBJECTIVES.keys()),
        key="objective",
    )
    tone = st.selectbox(
        "Tom de Voz",
        options=TONES,
        key="tone",
    )
    format_type = st.selectbox(
        "Formato",
        options=FORMAT_OPTIONS,
        key="format_type",
    )
    cta = st.selectbox(
        "CTA",
        options=CTAS,
        key="cta",
    )
    extra_keywords = st.text_input(
        "Palavras-chave extras (opcional)",
        placeholder="Ex: natural, sem dieta radical, resultado rápido",
        key="extra_keywords",
    )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    generate_btn = st.button("Gerar 5 Copies", use_container_width=True)

    st.markdown(
        '<p style="font-size:.72rem;color:rgba(255,255,255,.35);text-align:center;margin-top:8px;">'
        "Powered by Claude AI · Dash Digital"
        "</p>",
        unsafe_allow_html=True,
    )

# ── Lógica de geração ──────────────────────────────────────────────────────────
if generate_btn:
    if not product.strip():
        st.error("⚠️ Preencha o campo **Produto ou Serviço** para gerar as copies.")
    else:
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
            "format_type": format_type,
            "cta": cta,
            "extra_keywords": extra_keywords.strip(),
            "niche_data": niche_data,
        }

        with st.spinner("✍️ Gerando 5 copies com IA... aguarde alguns segundos"):
            try:
                copies = generate_copies(form_data)
                st.session_state.copies = copies
                st.session_state.form_data = form_data
            except Exception as e:
                st.error(f"❌ Erro ao gerar copies: {e}")

# ── Exibição das copies ────────────────────────────────────────────────────────
if st.session_state.copies:
    fd = st.session_state.form_data
    copies = st.session_state.copies

    st.markdown(get_result_header_html(fd), unsafe_allow_html=True)
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    for i, copy in enumerate(copies, 1):
        st.markdown(get_copy_card_html(copy, i), unsafe_allow_html=True)

        full_copy = copy.get("copy_completa", "")
        st.text_area(
            label=f"Copiar texto da Copy {i}",
            value=full_copy,
            height=140,
            label_visibility="collapsed",
            key=f"ta_copy_{i}",
        )
        if i < len(copies):
            st.markdown('<div class="card-spacer"></div>', unsafe_allow_html=True)

    # ── Botões de ação ──────────────────────────────────────────────────────────
    st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)
    st.markdown("---")

    col_dl, col_re = st.columns([3, 1])

    with col_dl:
        html_content = _build_download_html(copies, fd)
        st.download_button(
            label="⬇️ Baixar Copies em HTML",
            data=html_content,
            file_name=(
                f"copies_{fd['sub_niche'].split()[0].lower()}_"
                f"{fd['product'][:20].replace(' ', '_').lower()}.html"
            ),
            mime="text/html",
            use_container_width=True,
        )

    with col_re:
        if st.button("🔄 Gerar Novamente", use_container_width=True):
            with st.spinner("✍️ Gerando novas copies..."):
                try:
                    new_copies = generate_copies(st.session_state.form_data)
                    st.session_state.copies = new_copies
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

else:
    st.markdown(get_welcome_html(), unsafe_allow_html=True)
