def get_sidebar_css() -> str:
    return """
/* ── Sidebar base ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] { background: #0d2137 !important; }

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #fff !important;
}

/* Inputs */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] textarea {
    background-color: #1a3a5c !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 8px !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-baseweb="base-input"],
[data-testid="stSidebar"] [data-baseweb="textarea"] {
    background-color: #1a3a5c !important;
    border-color: rgba(255,255,255,0.25) !important;
    border-radius: 8px !important;
    color: #fff !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div { color: #fff !important; }
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #fff !important; }

/* Placeholder text */
[data-testid="stSidebar"] ::placeholder { color: rgba(255,255,255,0.4) !important; }

/* Botão gerar */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #f8b940, #d99a20) !important;
    color: #003f7c !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px !important;
    font-size: 1rem !important;
    width: 100% !important;
    margin-top: 8px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #ffc94d, #e8aa30) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(248,185,64,0.35) !important;
}

/* Nav padrão do Streamlit */
div[data-testid="stSidebarNav"] { display: none; }

/* ── Textarea da área principal (para copiar) ─────────────────────────────── */
.main [data-testid="stTextArea"] textarea {
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 0.9rem;
    line-height: 1.6;
    background: #f8fafc !important;
    border: 1px solid #dde3ed !important;
    border-radius: 10px !important;
    color: #1a1a2e !important;
    resize: vertical;
}
"""


def get_main_css() -> str:
    return """
/* ── Reset & base ─────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 900px;
}

/* ── Welcome screen ──────────────────────────────────────────────────────── */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
}
.welcome-icon { font-size: 4rem; margin-bottom: 16px; }
.welcome-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #003f7c;
    margin-bottom: 10px;
}
.welcome-sub {
    font-size: 1.05rem;
    color: #6b7280;
    max-width: 480px;
    line-height: 1.6;
}
.welcome-steps {
    margin-top: 36px;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    justify-content: center;
}
.welcome-step {
    background: #fff;
    border: 1px solid #dde3ed;
    border-radius: 14px;
    padding: 20px 24px;
    max-width: 200px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.welcome-step-icon { font-size: 1.8rem; margin-bottom: 8px; }
.welcome-step-text { font-size: 0.88rem; color: #374151; line-height: 1.4; }

/* ── Result header ───────────────────────────────────────────────────────── */
.result-header {
    background: linear-gradient(135deg, #003f7c 0%, #1a5a9a 60%, #0d4080 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: #fff;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
}
.result-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0; bottom: 0; left: 0;
    background: radial-gradient(ellipse at 85% 15%, rgba(255,255,255,0.10) 0%, transparent 60%);
    pointer-events: none;
}
.result-header-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 12px;
}
.result-niche {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.7);
    margin-bottom: 4px;
}
.result-product {
    font-size: 1.45rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.3;
}
.result-badge {
    background: rgba(248,185,64,0.18);
    border: 1px solid rgba(248,185,64,0.45);
    color: #f8b940;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 5px 14px;
    border-radius: 20px;
    white-space: nowrap;
}
.result-tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 16px;
}
.result-tag {
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.90);
    font-size: 0.78rem;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.18);
}

/* ── Copy card ───────────────────────────────────────────────────────────── */
.copy-card {
    background: #fff;
    border: 1px solid #dde3ed;
    border-radius: 16px;
    margin-bottom: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    overflow: hidden;
    transition: box-shadow 0.2s, transform 0.15s;
}
.copy-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.10);
    transform: translateY(-1px);
}
.copy-card-accent {
    height: 4px;
    width: 100%;
}
.copy-card-inner { padding: 22px 26px 18px; }
.copy-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}
.copy-number {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9ca3af;
}
.copy-type-badge {
    font-size: 0.78rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 20px;
}
.copy-section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.copy-hook-text {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.45;
    margin-bottom: 14px;
    padding-left: 12px;
    border-left: 3px solid;
}
.copy-body-text {
    font-size: 0.92rem;
    color: #374151;
    line-height: 1.7;
    white-space: pre-line;
    margin-bottom: 14px;
}
.copy-cta-box {
    display: inline-block;
    padding: 7px 18px;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 700;
    margin-bottom: 12px;
}
.copy-card-footer {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding-top: 10px;
    border-top: 1px solid #f0f3f8;
}
.copy-char-count {
    font-size: 0.72rem;
    color: #9ca3af;
}

/* ── Divider between cards ───────────────────────────────────────────────── */
.card-spacer { height: 20px; }

/* ── Sidebar brand ───────────────────────────────────────────────────────── */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 0 8px;
}
.sb-icon { font-size: 1.8rem; }
.sb-title { font-size: 1.1rem; font-weight: 700; color: #fff; }
.sb-sub { font-size: 0.75rem; color: rgba(255,255,255,0.55); margin-top: 1px; }
.sb-divider { border: none; border-top: 1px solid rgba(255,255,255,0.12); margin: 10px 0; }
.sb-section-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45) !important;
    margin-bottom: 6px;
    margin-top: 4px;
}
"""


def get_welcome_html() -> str:
    return """
<div class="welcome-wrap">
  <div class="welcome-icon">✍️</div>
  <div class="welcome-title">Gerador de Copy para Meta Ads</div>
  <div class="welcome-sub">
    Preencha o briefing na barra lateral e clique em <strong>Gerar 5 Copies</strong>
    para receber textos prontos para subir no gerenciador de anúncios.
  </div>
  <div class="welcome-steps">
    <div class="welcome-step">
      <div class="welcome-step-text"><strong>1. Nicho e produto</strong><br>Selecione o segmento e descreva o que está sendo anunciado</div>
    </div>
    <div class="welcome-step">
      <div class="welcome-step-text"><strong>2. Dor e desejo</strong><br>Explique o problema do público e o que ele quer conquistar</div>
    </div>
    <div class="welcome-step">
      <div class="welcome-step-text"><strong>3. Configurações</strong><br>Defina objetivo, tom de voz, formato e CTA do anúncio</div>
    </div>
    <div class="welcome-step">
      <div class="welcome-step-text"><strong>4. Receba 5 copies</strong><br>Cada uma com abordagem diferente, prontas para uso</div>
    </div>
  </div>
</div>
"""


def get_result_header_html(fd: dict) -> str:
    tags = [
        fd["objective"],
        fd["format_type"],
        fd["tone"],
        f'CTA: {fd["cta"]}',
    ]
    tags_html = "".join(f'<span class="result-tag">{t}</span>' for t in tags)

    return f"""
<div class="result-header">
  <div class="result-header-top">
    <div>
      <div class="result-niche">{fd['niche']} &rsaquo; {fd['sub_niche']}</div>
      <div class="result-product">{fd['product']}</div>
    </div>
    <div class="result-badge">5 Copies · Meta Ads</div>
  </div>
  <div class="result-tags">{tags_html}</div>
</div>
"""


def get_copy_card_html(copy: dict, index: int) -> str:
    cor = copy.get("cor", "#003f7c")
    cor_bg = copy.get("cor_bg", "#eff6ff")
    hook = copy.get("hook", "")
    body = copy.get("corpo", "").replace("\n", "<br>")
    cta = copy.get("cta_texto", "")
    tipo_nome = copy.get("tipo_nome", "")
    tipo_emoji = copy.get("tipo_emoji", "")
    full_copy = copy.get("copy_completa", "")
    char_count = len(full_copy)

    return f"""
<div class="copy-card">
  <div class="copy-card-accent" style="background: linear-gradient(90deg, {cor}, {cor}aa);"></div>
  <div class="copy-card-inner">
    <div class="copy-card-header">
      <span class="copy-number">Copy {index} de 5</span>
      <span class="copy-type-badge" style="background:{cor_bg}; color:{cor};">{tipo_nome}</span>
    </div>
    <div class="copy-section-label" style="color:{cor};">Hook</div>
    <div class="copy-hook-text" style="border-color:{cor};">{hook}</div>
    <div class="copy-section-label" style="color:{cor};">Corpo</div>
    <div class="copy-body-text">{body}</div>
    <div class="copy-section-label" style="color:{cor};">CTA</div>
    <div class="copy-cta-box" style="background:{cor_bg}; color:{cor};">{cta}</div>
    <div class="copy-card-footer">
      <span class="copy-char-count">{char_count} caracteres</span>
    </div>
  </div>
</div>
"""
