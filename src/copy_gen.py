import json
import re
import anthropic
import streamlit as st

from .niches import FORMAT_TIPS

COPY_TYPES = [
    {
        "id": "dor",
        "nome": "Identificação com a Dor",
        "emoji": "😔",
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
        "emoji": "🚀",
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
        "emoji": "🏆",
        "cor": "#f59e0b",
        "cor_bg": "#fffbeb",
        "instrucao": (
            "Abra com um dado de credibilidade: número de clientes, anos de experiência, "
            "resultado comprovado, avaliação ou depoimento. "
            "Autoridade e prova social constroem confiança antes de qualquer pitch."
        ),
    },
    {
        "id": "urgencia",
        "nome": "Urgência / Escassez",
        "emoji": "⏰",
        "cor": "#f97316",
        "cor_bg": "#fff7ed",
        "instrucao": (
            "Crie senso de urgência ou escassez REAL e justificável — prazo, vagas, estoque, "
            "oferta especial por tempo limitado. "
            "Nunca invente urgência falsa. Explique o POR QUE da limitação."
        ),
    },
    {
        "id": "story",
        "nome": "Storytelling",
        "emoji": "📖",
        "cor": "#8b5cf6",
        "cor_bg": "#f5f3ff",
        "instrucao": (
            "Conte uma mini-história de 2-4 frases que o público-alvo se identifique. "
            "Pode ser sobre um cliente, sobre o fundador, ou uma situação fictícia verossímil. "
            "A história deve levar naturalmente para a solução que você oferece."
        ),
    },
]


def _build_prompt(form: dict) -> str:
    niche_data = form.get("niche_data", {})
    format_tip = FORMAT_TIPS.get(form["format_type"], "")
    o_que_funciona = niche_data.get("o_que_funciona", "")
    hooks_validados = "\n".join(f"- {h}" for h in niche_data.get("hooks_validados", []))

    copies_spec = "\n".join(
        f"{i+1}. {c['nome']} ({c['emoji']}): {c['instrucao']}"
        for i, c in enumerate(COPY_TYPES)
    )

    offer_line = f"\n- Oferta/Preço: {form['offer']}" if form.get("offer") else ""
    keywords_line = f"\n- Palavras-chave/Diferenciais: {form['extra_keywords']}" if form.get("extra_keywords") else ""
    usp_line = f"\n- Diferencial/USP: {form['usp']}" if form.get("usp") else ""

    prompt = f"""Você é um redator sênior especialista em Meta Ads (Facebook e Instagram Ads) com profundo conhecimento do mercado brasileiro. Você escreve EXCLUSIVAMENTE copies para anúncios pagos — não posts orgânicos, não legendas de conteúdo. Sua especialidade é criar textos que param o scroll, geram identificação imediata e convertem em cliques e leads.

## BRIEFING DO ANÚNCIO

- **Nicho:** {form['niche']} › {form['sub_niche']}
- **Produto/Serviço:** {form['product']}
- **Público-Alvo:** {form['audience']}
- **Principal Dor:** {form['pain']}
- **Principal Desejo:** {form['desire']}{usp_line}{offer_line}
- **Objetivo do Anúncio:** {form['objective']} — {form['objective_desc']}
- **Tom de Voz:** {form['tone']}
- **Formato:** {form['format_type']}
- **CTA Desejado:** {form['cta']}{keywords_line}

## O QUE FUNCIONA NESSE NICHO
{o_que_funciona}

## HOOKS VALIDADOS PARA ESSE NICHO (use como inspiração, não copie)
{hooks_validados}

## DIRETRIZES DO FORMATO: {form['format_type']}
{format_tip}

## SUA TAREFA

Gere EXATAMENTE 5 copies diferentes para esse anúncio, cada uma com uma abordagem distinta:

{copies_spec}

## REGRAS OBRIGATÓRIAS

**Linguagem e tom:**
- Português brasileiro natural, direto e humano — nunca robotizado, nunca formal demais
- Tom de voz consistente com: {form['tone']}
- Hook (primeira frase) DEVE parar o scroll — é o elemento mais crítico do anúncio

**Estruturas PROIBIDAS — jamais use:**
- "Não é X. É Y." / "Não é isso. É tal coisa." / qualquer variação dessa construção
- Clichês genéricos: "não perca tempo", "corra", "oferta imperdível", "oportunidade única"
- Perguntas retóricas óbvias demais: "Quer emagrecer?" / "Quer ganhar dinheiro?"
- Hipérboles exageradas sem respaldo: "revolucionário", "milagroso", "nunca visto antes"

**Emojis:**
- Use com extrema moderação — no máximo 1 ou 2 por copy, apenas se acrescentar contexto real
- Nunca use emojis decorativos ou no início de cada frase
- Copies de anúncio profissional não precisam de emojis; só use se o tom for leve e pedir

**CTA e formato:**
- CTA deve ser variação natural de: "{form['cta']}" — adapte ao contexto da copy
- Para Stories: máximo 4 linhas no total
- Para Feed: parágrafos curtos (máx 3 linhas por bloco) com espaço entre eles
- Cada copy deve estar COMPLETA e pronta para subir no gerenciador de anúncios sem edição

## FORMATO DE RESPOSTA

Responda APENAS com um JSON válido, sem markdown, sem explicações fora do JSON:

{{
  "copies": [
    {{
      "tipo_id": "dor",
      "tipo_nome": "Identificação com a Dor",
      "tipo_emoji": "😔",
      "hook": "primeira frase impactante do anúncio",
      "corpo": "restante do texto sem o hook e sem o CTA",
      "cta_texto": "chamada para ação final",
      "copy_completa": "copy inteira formatada, pronta para usar"
    }},
    {{
      "tipo_id": "beneficio",
      "tipo_nome": "Benefício Direto",
      "tipo_emoji": "🚀",
      "hook": "...",
      "corpo": "...",
      "cta_texto": "...",
      "copy_completa": "..."
    }},
    {{
      "tipo_id": "prova",
      "tipo_nome": "Prova Social",
      "tipo_emoji": "🏆",
      "hook": "...",
      "corpo": "...",
      "cta_texto": "...",
      "copy_completa": "..."
    }},
    {{
      "tipo_id": "urgencia",
      "tipo_nome": "Urgência / Escassez",
      "tipo_emoji": "⏰",
      "hook": "...",
      "corpo": "...",
      "cta_texto": "...",
      "copy_completa": "..."
    }},
    {{
      "tipo_id": "story",
      "tipo_nome": "Storytelling",
      "tipo_emoji": "📖",
      "hook": "...",
      "corpo": "...",
      "cta_texto": "...",
      "copy_completa": "..."
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
            "Chave ANTHROPIC_API_KEY não encontrada em .streamlit/secrets.toml. "
            "Adicione: ANTHROPIC_API_KEY = 'sk-ant-...'"
        )

    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_prompt(form)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Remove markdown code blocks if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
        copies = data.get("copies", [])
    except json.JSONDecodeError:
        # Fallback: try to extract JSON object
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            copies = data.get("copies", [])
        else:
            raise ValueError(f"Não foi possível interpretar a resposta da IA. Resposta recebida:\n{raw[:500]}")

    # Enrich with color data from COPY_TYPES
    type_map = {c["id"]: c for c in COPY_TYPES}
    for copy in copies:
        tid = copy.get("tipo_id", "")
        if tid in type_map:
            copy["cor"] = type_map[tid]["cor"]
            copy["cor_bg"] = type_map[tid]["cor_bg"]

    return copies
