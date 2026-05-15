def get_sidebar_css() -> str:
    return """
/* ── Sidebar base ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] { background: #0d2137 !important; }

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] summary {
    color: #fff !important;
}

/* Expanders na sidebar */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"]:hover {
    border-color: rgba(255,255,255,0.22) !important;
}

/* Textarea dentro da sidebar */
[data-testid="stSidebar"] textarea {
    background-color: #0a1929 !important;
    color: #d1dbe8 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    line-height: 1.6 !important;
}

/* Botão de download na sidebar */
[data-testid="stSidebar"] .stDownloadButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.85) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    width: 100% !important;
    margin-top: 4px !important;
}
[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background: rgba(255,255,255,0.14) !important;
}

div[data-testid="stSidebarNav"] { display: none; }

/* ── Área principal — form ──────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1000px;
}
"""


def get_main_css() -> str:
    return """
/* ── Page header ────────────────────────────────────────────────────────────── */
.page-header {
    background: linear-gradient(135deg, #003f7c 0%, #1a5a9a 60%, #0d4080 100%);
    border-radius: 16px;
    padding: 26px 32px;
    color: #fff;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 85% 15%, rgba(255,255,255,0.10) 0%, transparent 60%);
    pointer-events: none;
}
.page-header-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 4px;
}
.page-header-sub {
    font-size: 0.88rem;
    color: rgba(255,255,255,0.65);
}

/* ── Form sections ──────────────────────────────────────────────────────────── */
.form-section {
    background: #fff;
    border: 1px solid #dde3ed;
    border-radius: 14px;
    padding: 20px 24px 16px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.form-section-title {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #003f7c;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eef1f6;
}

/* ── Gerar button ───────────────────────────────────────────────────────────── */
.main .stButton > button {
    background: linear-gradient(135deg, #f8b940, #d99a20) !important;
    color: #003f7c !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
    margin-top: 4px !important;
}
.main .stButton > button:hover {
    background: linear-gradient(135deg, #ffc94d, #e8aa30) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(248,185,64,0.35) !important;
}

/* ── Sidebar brand ──────────────────────────────────────────────────────────── */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 0 10px;
}
.sb-icon { font-size: 1.6rem; }
.sb-title { font-size: 1rem; font-weight: 700; color: #fff; }
.sb-sub { font-size: 0.72rem; color: rgba(255,255,255,0.5); margin-top: 1px; }
.sb-divider { border: none; border-top: 1px solid rgba(255,255,255,0.12); margin: 10px 0; }
.sb-section-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45) !important;
    margin-bottom: 6px;
}

/* ── Copy blocks inside sidebar expanders ───────────────────────────────────── */
.copy-block-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45) !important;
    margin: 8px 0 3px;
}
.copy-type-pill {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 8px;
}
"""


def get_page_header_html() -> str:
    return """
<div class="page-header">
  <div class="page-header-title">Gerador de Copy · Meta Ads</div>
  <div class="page-header-sub">Preencha o briefing abaixo e clique em Gerar — as 5 copies aparecem na barra lateral</div>
</div>
"""


def get_sidebar_welcome_html() -> str:
    return """
<div style="padding: 12px 4px; color: rgba(255,255,255,0.45); font-size: 0.82rem; line-height: 1.6; text-align: center;">
  Preencha o briefing e clique em<br>
  <strong style="color:rgba(255,255,255,0.7)">Gerar 5 Copies</strong><br>
  para ver os resultados aqui.
</div>
"""


def get_sidebar_copy_header_html(fd: dict) -> str:
    return f"""
<div style="
    background: linear-gradient(135deg, #003f7c, #1a5a9a);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
">
  <div style="font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.55);margin-bottom:3px;">
    {fd['niche']} › {fd['sub_niche']}
  </div>
  <div style="font-size:1rem;font-weight:700;color:#fff;line-height:1.3;">{fd['product']}</div>
  <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
    <span style="background:rgba(255,255,255,.1);color:rgba(255,255,255,.8);font-size:.7rem;padding:2px 8px;border-radius:12px;">{fd['objective']}</span>
    <span style="background:rgba(248,185,64,.18);color:#f8b940;font-size:.7rem;padding:2px 8px;border-radius:12px;">{fd['cta']}</span>
  </div>
</div>
"""
