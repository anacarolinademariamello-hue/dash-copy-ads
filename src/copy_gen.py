import re
import anthropic
import streamlit as st

COPY_TYPES = [
    {
        "id": "dor",
        "nome": "Identificação com a Dor",
        "cor": "#ef4444",
        "cor_bg": "#fef2f2",
        "instrucao": (
            "Comece identificando e validando a principal dor/problema do público. "
            "O hook deve fazer o leitor sentir 'essa copy foi feita para mim'. "
            "Mostre que você entende a frustração, depois apresente a solução como alívio."
        ),
    },
    {
        "id": "beneficio",
        "nome": "Benefício Direto",
        "cor": "#3b82f6",
        "cor_bg": "#eff6ff",
        "instrucao": (
            "Comece direto com o maior benefício ou resultado que o produto entrega. "
            "Sem rodeios — a primeira linha já deve revelar o valor central. "
            "Use números, prazos e especificidades sempre que possível."
        ),
    },
    {
        "id": "prova",
        "nome": "Prova Social",
        "cor": "#f59e0b",
        "cor_bg": "#fffbeb",
        "instrucao": (
            "Abra com um dado de credibilidade: número de clientes, anos de experiência, "
            "resultado comprovado ou depoimento. "
            "Autoridade e prova social constroem confiança antes de qualquer pitch."
        ),
    },
    {
        "id": "urgencia",
        "nome": "Urgência / Escassez",
        "cor": "#f97316",
        "cor_bg": "#fff7ed",
        "instrucao": (
            "Crie senso de urgência ou escassez real e justificável — prazo, vagas, estoque, "
            "oferta especial por tempo limitado. "
            "Nunca invente urgência falsa. Explique o motivo da limitação."
        ),
    },
    {
        "id": "story",
        "nome": "Storytelling",
        "cor": "#8b5cf6",
        "cor_bg": "#f5f3ff",
        "instrucao": (
            "Conte uma mini-história de 2 a 4 frases com a qual o público se identifique. "
            "Pode ser sobre um cliente real, o fundador ou uma situação verossímil. "
            "A história deve conduzir naturalmente para a solução oferecida."
        ),
    },
]


def _build_prompt(form: dict) -> str:
    o_que_funciona = form["niche_data"].get("o_que_funciona", "")
    hooks_validados = "\n".join(
        f"- {h}" for h in form["niche_data"].get("hooks_validados", [])
    )

    copies_spec = "\n".join(
        f"{i+1}. {c['nome']}: {c['instrucao']}"
        for i, c in enumerate(COPY_TYPES)
    )

    offer_line = f"\n- Oferta/Preço: {form['offer']}" if form.get("offer") else ""
    usp_line = f"\n- Diferencial/USP: {form['usp']}" if form.get("usp") else ""
    kw_line = f"\n- Palavras-chave/Diferenciais: {form['extra_keywords']}" if form.get("extra_keywords") else ""
    saz_line = f"\n- Sazonalidade/Contexto: {form['sazonalidade']}" if form.get("sazonalidade") else ""
    client_line = f"\n- Cliente: {form['client_name']}" if form.get("client_name") else ""
    ref_line = (
        f"\n\n## REFERÊNCIAS DE COPY (tom e estilo para se inspirar, não copiar)\n{form['referencias']}"
        if form.get("referencias") else ""
    )
    tov_line = (
        f"\n\n## TOM DE VOZ DO CLIENTE — SIGA RIGOROSAMENTE\n{form['client_tone_of_voice']}"
        if form.get("client_tone_of_voice") else ""
    )

    tipo = form.get("tipo_criativo", "Card (imagem)")
    criativo_instrucao = {
        "Vídeo": (
            "Escreva o ROTEIRO completo para o vídeo conforme a estrutura descrita. "
            "Inclua: o que falar nos primeiros 3 segundos (gancho), desenvolvimento da mensagem, CTA falado. "
            "Separe claramente cada parte. Escreva exatamente o que a pessoa vai falar — sem descrições de cena."
        ),
        "Card (imagem)": (
            "Escreva os TEXTOS EXATOS que vão na imagem conforme a estrutura descrita. "
            "Headline, subheadline, e qualquer outro texto visível. "
            "Sem instruções de design — só o texto em si."
        ),
        "Carrossel": (
            "Escreva os TEXTOS DE CADA SLIDE conforme a estrutura descrita. "
            "Numere claramente: Slide 1:, Slide 2:, etc. "
            "Cada slide deve ter sua headline e texto de apoio, se houver. Só o texto — sem instruções visuais."
        ),
    }.get(tipo, "Escreva os textos exatos para o criativo conforme a estrutura descrita.")

    criativo_label = {
        "Vídeo": "Roteiro",
        "Card (imagem)": "Texto da Imagem",
        "Carrossel": "Textos dos Slides",
    }.get(tipo, "Copy do Criativo")

    prompt = f"""Você é um redator sênior especialista em Meta Ads (Facebook e Instagram Ads) com profundo conhecimento do mercado brasileiro. Você escreve EXCLUSIVAMENTE copies para anúncios pagos — não posts orgânicos. Sua especialidade é criar textos que param o scroll, geram identificação imediata e aumentam o ROI dos anúncios.

## BRIEFING DO ANÚNCIO

- **Nicho:** {form['niche']} › {form['sub_niche']}
- **Produto/Serviço:** {form['product']}
- **Público-Alvo:** {form['audience']}
- **Principal Dor:** {form['pain']}
- **Principal Desejo:** {form['desire']}{usp_line}{offer_line}{client_line}
- **Objetivo:** {form['objective']} — {form['objective_desc']}
- **Tom de Voz:** {form['tone']}
- **CTA Desejado:** {form['cta']}{kw_line}{saz_line}{tov_line}

## TIPO DE CRIATIVO: {tipo}

## ESTRUTURA DO CRIATIVO
{form['criativo_estrutura'] if form.get('criativo_estrutura') else 'Sem estrutura definida — use seu julgamento para o tipo de criativo selecionado.'}
{ref_line}

## O QUE FUNCIONA NESSE NICHO
{o_que_funciona}

## HOOKS VALIDADOS PARA ESSE NICHO (inspiração, não copiar)
{hooks_validados}

## SUA TAREFA

Gere EXATAMENTE 5 variações de copy para esse anúncio, cada uma com abordagem distinta:

{copies_spec}

Para cada variação, entregue DOIS blocos de texto:

**{criativo_label}:** {criativo_instrucao}

Para cada variação, entregue DOIS blocos:

**LEGENDA:** o texto completo da publicação no Meta Ads (aparece abaixo do criativo no feed). Estrutura: hook na primeira linha, corpo, CTA. Parágrafos curtos. Deve funcionar no feed do Facebook e do Instagram.

**COPY DO CRIATIVO:** o texto que vai dentro da imagem ou vídeo, conforme a estrutura descrita no briefing. Escreva exatamente o que o designer ou editor vai usar — sem instruções, sem explicações, só o texto em si.

## REGRAS OBRIGATÓRIAS

**Linguagem e tom:**
- Português brasileiro natural, direto e humano — nunca robotizado
- Tom de voz: {form['tone']}
- Hook da legenda (primeira frase) DEVE parar o scroll — é o elemento mais crítico

**Estruturas PROIBIDAS:**
- O padrão "negação + afirmação em duas frases curtas": "Não é X. É Y.", "Não foi sorte. Foi método.", "Não é treino. É ciência.", "Não é dieta. É estilo de vida." — PROIBIDO em qualquer variação de verbo, substantivo ou tempo verbal. Se a segunda frase corrige ou redefine a primeira, é essa estrutura. Não use.
- Clichês: "não perca tempo", "corra", "oferta imperdível", "oportunidade única"
- Perguntas óbvias demais: "Quer emagrecer?", "Quer ganhar dinheiro?"
- Hipérboles sem respaldo: "revolucionário", "milagroso", "nunca visto antes"

**Emojis:**
- Máximo 1 a 2 por legenda, apenas se agregar contexto real
- Nunca use emojis decorativos ou no início de cada frase
- Copy do criativo: sem emojis

**CTA:**
- Variação natural de: "{form['cta']}" — adapte ao contexto de cada copy

**Qualidade:**
- Nada genérico — cada copy deve parecer escrita especificamente para esse produto e público
- Cada variação deve ter voz, ritmo e abordagem visivelmente distintos entre si
- Legenda e criativo de cada variação devem ser coerentes entre si em tom e mensagem

## FORMATO DE RESPOSTA

Use EXCLUSIVAMENTE o formato XML abaixo. Não use JSON. Não adicione nenhum texto fora das tags XML.

Para cada copy, inclua a tag <hook_score> com uma pontuação de 1 a 10 seguida de uma justificativa de 1 linha explicando a força do hook (ex: "8/10 — cria identificação imediata com a dor sem ser genérico").

<copies>
<copy>
<tipo_id>dor</tipo_id>
<tipo_nome>Identificação com a Dor</tipo_nome>
<legenda_hook>primeira frase da legenda</legenda_hook>
<legenda_corpo>restante da legenda sem hook e sem CTA</legenda_corpo>
<legenda_cta>chamada para ação</legenda_cta>
<legenda_completa>legenda inteira formatada, pronta para colar no Meta Ads</legenda_completa>
<criativo>texto exato para o criativo conforme estrutura descrita</criativo>
<hook_score>pontuação de 1 a 10 com justificativa de 1 linha</hook_score>
</copy>
<copy>
<tipo_id>beneficio</tipo_id>
<tipo_nome>Benefício Direto</tipo_nome>
<legenda_hook>...</legenda_hook>
<legenda_corpo>...</legenda_corpo>
<legenda_cta>...</legenda_cta>
<legenda_completa>...</legenda_completa>
<criativo>...</criativo>
<hook_score>...</hook_score>
</copy>
<copy>
<tipo_id>prova</tipo_id>
<tipo_nome>Prova Social</tipo_nome>
<legenda_hook>...</legenda_hook>
<legenda_corpo>...</legenda_corpo>
<legenda_cta>...</legenda_cta>
<legenda_completa>...</legenda_completa>
<criativo>...</criativo>
<hook_score>...</hook_score>
</copy>
<copy>
<tipo_id>urgencia</tipo_id>
<tipo_nome>Urgência / Escassez</tipo_nome>
<legenda_hook>...</legenda_hook>
<legenda_corpo>...</legenda_corpo>
<legenda_cta>...</legenda_cta>
<legenda_completa>...</legenda_completa>
<criativo>...</criativo>
<hook_score>...</hook_score>
</copy>
<copy>
<tipo_id>story</tipo_id>
<tipo_nome>Storytelling</tipo_nome>
<legenda_hook>...</legenda_hook>
<legenda_corpo>...</legenda_corpo>
<legenda_cta>...</legenda_cta>
<legenda_completa>...</legenda_completa>
<criativo>...</criativo>
<hook_score>...</hook_score>
</copy>
</copies>"""

    return prompt


def _extract_tag(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def _parse_xml_response(raw: str) -> list[dict]:
    copies = []
    blocks = re.findall(r"<copy>(.*?)</copy>", raw, re.DOTALL)
    for block in blocks:
        copies.append({
            "tipo_id":         _extract_tag(block, "tipo_id"),
            "tipo_nome":       _extract_tag(block, "tipo_nome"),
            "legenda_hook":    _extract_tag(block, "legenda_hook"),
            "legenda_corpo":   _extract_tag(block, "legenda_corpo"),
            "legenda_cta":     _extract_tag(block, "legenda_cta"),
            "legenda_completa": _extract_tag(block, "legenda_completa"),
            "criativo":        _extract_tag(block, "criativo"),
            "hook_score":      _extract_tag(block, "hook_score"),
        })
    return copies


CRIATIVO_LABELS = {
    "Vídeo": "Roteiro",
    "Card (imagem)": "Texto da Imagem",
    "Carrossel": "Textos dos Slides",
}


def generate_copies(form: dict) -> list[dict]:
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY") or st.secrets.get("anthropic_api_key")
    except Exception:
        api_key = None

    if not api_key:
        raise ValueError(
            "Chave ANTHROPIC_API_KEY não encontrada em .streamlit/secrets.toml."
        )

    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_prompt(form)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    copies = _parse_xml_response(raw)
    if not copies:
        raise ValueError(f"Não foi possível interpretar a resposta. Trecho:\n{raw[:500]}")

    type_map = {c["id"]: c for c in COPY_TYPES}
    for copy in copies:
        tid = copy.get("tipo_id", "")
        if tid in type_map:
            copy["cor"] = type_map[tid]["cor"]
            copy["cor_bg"] = type_map[tid]["cor_bg"]

    return copies
