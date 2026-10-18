import re
import json
import httpx
from datetime import date
from app.core.config import settings
from app.schemas.gemini import ExtractedTransaction

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def _parse_with_openrouter(text: str, membres_dict: dict[str, int], today_str: str) -> ExtractedTransaction:
    """Appel OpenRouter vers NVIDIA Nemotron (ou autre modèle configuré)."""
    system_prompt = f"""Tu es l'assistant financier d'un groupe de musique.
Ton rôle est d'analyser le message de l'utilisateur et d'en extraire les informations de dépense.
Nous sommes aujourd'hui le {today_str}.

Voici le dictionnaire des membres actuels du groupe (Nom -> ID) :
{json.dumps(membres_dict, ensure_ascii=False)}

Règles :
- Si le message dit "J'ai payé pour tout le monde" ou ne précise pas de bénéficiaires, mets les IDs de TOUS les membres.
- Si le message précise des bénéficiaires (ex: "pour moi et Minmin"), mets uniquement les IDs correspondants.
- Si la personne parle d'elle-même ("moi", "j'ai"), tu dois assumer que l'auteur est inclus.
- Pour la date : si une date relative ou absolue est mentionnée (ex: "hier", "le 10/09", "samedi"), calcule la date exacte au format YYYY-MM-DD par rapport à aujourd'hui ({today_str}). Sinon renvoie une chaîne vide "".

Tu DOIS répondre UNIQUEMENT par un objet JSON valide respectant strictement ce format :
{{
  "montant": <float positif>,
  "categorie": "<string: Transport, Restaurant, Studio, Matériel, Divers, etc.>",
  "participants_ids": [<liste des IDs entiers des membres>],
  "is_remboursement": <true si c'est explicitement un remboursement entre membres, sinon false>,
  "date_transaction": <"YYYY-MM-DD" ou "">
}}"""

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://hongre-app.web.app",
        "X-Title": "Hongre Cost Manager",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"[OPENROUTER ERROR] {response.status_code}: {response.text}")
            raise ValueError(f"OpenRouter ({response.status_code}): {response.text}")
            
        data = response.json()
        raw_content = data["choices"][0]["message"]["content"]

    # Extraction ciblée du bloc JSON {...}
    match = re.search(r"(\{.*\})", raw_content, flags=re.DOTALL)
    json_str = match.group(1) if match else raw_content.strip()
    
    return ExtractedTransaction.model_validate_json(json_str)

async def _parse_with_gemini(text: str, membres_dict: dict[str, int], today_str: str) -> ExtractedTransaction:
    """Appel de secours vers Gemini si la clé OpenRouter n'est pas configurée."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    prompt = f"""
    Tu es l'assistant financier d'un groupe de musique.
    Ton rôle est d'analyser le message suivant et d'en extraire les informations de dépense.
    
    Nous sommes aujourd'hui le {today_str}.
    
    Voici le dictionnaire des membres actuels du groupe (Nom -> ID) :
    {json.dumps(membres_dict, ensure_ascii=False)}
    
    Règles :
    - Si le message dit "J'ai payé pour tout le monde" ou ne précise pas de bénéficiaires, mets les IDs de TOUS les membres.
    - Si le message précise des bénéficiaires (ex: "pour moi et Minmin"), mets uniquement les IDs correspondants.
    - Si la personne parle d'elle-même ("moi", "j'ai"), tu dois assumer que l'auteur est inclus.
    - Pour la date : si une date relative ou absolue est mentionnée (ex: "hier", "le 10/09", "samedi"), calcule la date exacte au format YYYY-MM-DD par rapport à aujourd'hui ({today_str}). Sinon renvoie une chaîne vide "".
    
    Texte à analyser : "{text}"
    """
    
    response = await client.aio.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractedTransaction,
            temperature=0.0
        ),
    )
    
    return ExtractedTransaction.model_validate_json(response.text)

async def parse_expense_text(text: str, membres_dict: dict[str, int]) -> ExtractedTransaction:
    """
    Extrait les données financières depuis le texte avec Nemotron via OpenRouter (ou Gemini en fallback).
    """
    today_str = date.today().isoformat()
    
    if settings.OPENROUTER_API_KEY:
        return await _parse_with_openrouter(text, membres_dict, today_str)
    elif settings.GEMINI_API_KEY:
        return await _parse_with_gemini(text, membres_dict, today_str)
    else:
        raise ValueError("Aucune clé API configurée (ni OPENROUTER_API_KEY ni GEMINI_API_KEY)")
