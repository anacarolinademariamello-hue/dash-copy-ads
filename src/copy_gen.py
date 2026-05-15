import json
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
    ref_line = (
        f"\n\n## REFERÊNCIAS DE COPY (tom e estilo para se inspirar, não copiar)\n{form['referencias']}"
        if form.get("referencias") else ""
    )

    prompt = f"""Você é um redator sênior especialista em Meta Ads (Facebook e Instagram Ads) com profundo conhecimento do mercado brasileiro. Você escreve EXCLUSIVAMENTE copies para anúncios pagos — não posts orgânicos. Sua especialidade é criar textos que param o scroll, geram identificação imediata e aumentam o ROI dos anúncios.

## BRIEFING DO ANÚNCIO

- **Nicho:** {form['niche']} › {form['sub_niche']}
- **Produto/Serviço:** {form['product']}
- **Público-Alvo:** {form['audience']}
- **Principal Dor:** {form['pain']}
- **Principal Desejo:** {form['desire']}{usp_line}{offer_line}
- **Objetivo:** {form['objective']} — {form['objective_desc']}
- **Tom de Voz:** {form['tone']}
- **CTA Desejado:** {form['cta']}{kw_line}

## ESTRUTURA DO CRIATIVO
{form['criativo_estrutura'] if form.get('criativo_estrutura') else 'Criativo livre — gere headlines e texto de apoio que funcionem bem em imagem estática ou vídeo curto.'}
{ref_line}

## O QUE FUNCIONA NESSE NICHO
{o_que_funciona}

## HOOKS VALIDADOS PARA ESSE NICHO (inspiração, não copiar)
{hooks_validados}

## SUA TAREFA

Gere EXATAMENTE 5 variações de copy para esse anúncio, cada uma com abordagem distinta:

{copies_spec}

Para cada variação, entregue DOIS blocos de texto:

**LEGENDA:** o texto completo da publicação no Meta Ads (aparece abaixo do criativo no feed). Estrutura: hook na primeira linha, corpo, CTA. Parágrafos curtos. Deve funcionar no feed do Facebook e do Instagram.

**COPY DO CRIATIVO:** o texto que vai dentro da imagem ou vídeo, conforme a estrutura descrita no briefing. Escreva exatamente o que o designer ou editor vai usar — sem instruções, sem explicações, só o texto em si.

## REGRAS OBRIGATÓRIAS

**Linguagem e tom:**
- Português brasileiro natural, direto e humano — nunca robotizado
- Tom de voz: {form['tone']}
- Hook da legenda (primeira frase) DEVE parar o scroll — é o elemento mais crítico

**Estruturas PROIBIDAS:**
- "Não é X. É Y." e qualquer variação dessa construção
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

Responda APENAS com JSON válido, sem markdown externo:

{{
  "copies": [
    {{
      "tipo_id": "dor",
      "tipo_nome": "Identificação com a Dor",
      "legenda_hook": "primeira frase da legenda",
      "legenda_corpo": "restante da legenda sem hook e sem CTA",
      "legenda_cta": "chamada para ação",
      "legenda_completa": "legenda inteira formatada, pronta para colar no Meta Ads",
      "criativo": "texto exato para o criativo conforme estrutura descrita"
    }},
    {{
      "tipo_id": "beneficio",
      "tipo_nome": "Benefício Direto",
      "legenda_hook": "...",
      "legenda_corpo": "...",
      "legenda_cta": "...",
      "legenda_completa": "...",
      "criativo": "..."
    }},
    {{
      "tipo_id": "prova",
      "tipo_nome": "Prova Social",
      "legenda_hook": "...",
      "legenda_corpo": "...",
      "legenda_cta": "...",
      "legenda_completa": "...",
      "criativo": "..."
    }},
    {{
      "tipo_id": "urgencia",
      "tipo_nome": "Urgência / Escassez",
      "legenda_hook": "...",
      "legenda_corpo": "...",
      "legenda_cta": "...",
      "legenda_completa": "...",
      "criativo": "..."
    }},
    {{
      "tipo_id": "story",
      "tipo_nome": "Storytelling",
      "legenda_hook": "...",
      "legenda_corpo": "...",
      "legenda_cta": "...",
      "legenda_completa": "...",
      "criativo": "..."
    }}
  ]
}}"""

    return prompt


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
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
        copies = data.get("copies", [])
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            copies = data.get("copies", [])
        else:
            raise ValueError(f"Não foi possível interpretar a resposta. Trecho:\n{raw[:500]}")

    type_map = {c["id"]: c for c in COPY_TYPES}
    for copy in copies:
        tid = copy.get("tipo_id", "")
        if tid in type_map:
            copy["cor"] = type_map[tid]["cor"]
            copy["cor_bg"] = type_map[tid]["cor_bg"]

    return copies
