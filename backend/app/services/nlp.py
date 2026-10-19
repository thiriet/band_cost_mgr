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
- Pour le payeur : Si le message mentionne explicitement qui a payé ou avancé la dépense (ex: "Britt a payé", "JB a avancé 20€"), mets l'ID de ce membre dans id_payeur. Si l'auteur parle de lui-même ("J'ai payé", "moi") ou si non précisé, mets 0.
- Pour les bénéficiaires : Si le message dit "pour tout le monde" ou ne précise pas, mets les IDs de TOUS les membres.
- Si le message précise des bénéficiaires (ex: "pour moi et Minmin"), mets uniquement les IDs correspondants.
- Si la personne parle d'elle-même ("moi", "j'ai"), tu dois assumer que l'auteur est inclus dans les bénéficiaires.
- Pour la date : si une date relative ou absolue est mentionnée (ex: "hier", "le 10/09", "samedi"), calcule la date exacte au format YYYY-MM-DD par rapport à aujourd'hui ({today_str}). Sinon renvoie une chaîne vide "".

Tu DOIS répondre UNIQUEMENT par un objet JSON valide respectant strictement ce format :
{{
  "montant": <float positif>,
  "categorie": "<string: Transport, Restaurant, Studio, Matériel, Divers, etc.>",
  "participants_ids": [<liste des IDs entiers des membres>],
  "id_payeur": <int, ID du membre ayant payé ou 0>,
  "is_remboursement": <true si c'est explicitement un remboursement entre membres, sinon false>,
  "date_transaction": <"YYYY-MM-DD" ou "">
}}"""

    # Modèle principal demandé : nvidia/nemotron-3.5-super-vl:free
    primary_model = settings.OPENROUTER_MODEL or "nvidia/nemotron-3.5-super-vl:free"
    if "llama-3.1-nemotron" in primary_model:
        primary_model = "nvidia/nemotron-3.5-super-vl:free"

    fallback_models = [
        primary_model,
        "nvidia/nemotron-3.5-super-vl",
        "nvidia/nemotron-3.5-lightning:free"
    ]
    unique_fallbacks = list(dict.fromkeys(fallback_models))[:3]

    payload = {
        "model": primary_model,
        "models": unique_fallbacks,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.0
    }
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY.strip()}",
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
    - Pour le payeur : Si le message mentionne explicitement qui a payé ou avancé la dépense (ex: "Britt a payé", "JB a avancé 20€"), mets l'ID de ce membre dans id_payeur. Si l'auteur parle de lui-même ("J'ai payé", "moi") ou si non précisé, mets 0.
    - Pour les bénéficiaires : Si le message dit "pour tout le monde" ou ne précise pas, mets les IDs de TOUS les membres.
    - Si le message précise des bénéficiaires (ex: "pour moi et Minmin"), mets uniquement les IDs correspondants.
    - Si la personne parle d'elle-même ("moi", "j'ai"), tu dois assumer que l'auteur est inclus dans les bénéficiaires.
    - Pour la date : si une date relative ou absolue est mentionnée (ex: "hier", "le 10/09", "samedi"), calcule la date exacte au format YYYY-MM-DD par rapport à aujourd'hui ({today_str}). Sinon renvoie une chaîne vide "".
    
    Texte à analyser : "{text}"
    """
    
    gemini_models = ["gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash-002"]
    last_err = None
    for model_name in gemini_models:
        try:
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedTransaction,
                    temperature=0.0
                ),
            )
            return ExtractedTransaction.model_validate_json(response.text)
        except Exception as err:
            last_err = err
            print(f"[GEMINI MODEL {model_name} FAILED] {err}")
            continue
    raise last_err

async def parse_expense_text(text: str, membres_dict: dict[str, int]) -> ExtractedTransaction:
    """
    Extrait les données financières depuis le texte avec Nemotron via OpenRouter (ou Gemini en fallback).
    """
    today_str = date.today().isoformat()
    
    has_openrouter = bool(settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY.strip())
    has_gemini = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
    
    if has_openrouter:
        try:
            return await _parse_with_openrouter(text, membres_dict, today_str)
        except Exception as e:
            print(f"[OPENROUTER FAILED] {e}. Bascule sur Gemini...")
            if has_gemini:
                try:
                    return await _parse_with_gemini(text, membres_dict, today_str)
                except Exception as g_err:
                    raise ValueError(f"OpenRouter: {e} | Secours Gemini: {g_err}")
            raise ValueError(f"OpenRouter: {e}")
    elif has_gemini:
        return await _parse_with_gemini(text, membres_dict, today_str)
    else:
        raise ValueError("Aucune clé API configurée sur le serveur Render (OPENROUTER_API_KEY et GEMINI_API_KEY sont absentes).")
