import json
from google import genai
from google.genai import types
from app.core.config import settings
from app.schemas.gemini import ExtractedTransaction

# Initialiser le client (utilise la variable GEMINI_API_KEY par défaut ou via params)
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def parse_expense_text(text: str, membres_dict: dict[str, int]) -> ExtractedTransaction:
    """
    Interroge Gemini 1.5 pour extraire les données financières du texte.
    membres_dict est un dict de { "Prénom": ID_technique }.
    """
    
    prompt = f"""
    Tu es l'assistant financier d'un groupe de musique.
    Ton rôle est d'analyser le message suivant et d'en extraire les informations de dépense.
    
    Voici le dictionnaire des membres actuels du groupe (Nom -> ID) :
    {json.dumps(membres_dict, ensure_ascii=False)}
    
    Règles :
    - Si le message dit "J'ai payé pour tout le monde" ou ne précise pas de bénéficiaires, mets les IDs de TOUS les membres.
    - Si le message précise des bénéficiaires (ex: "pour moi et Nico"), mets uniquement les IDs correspondants.
    - Si la personne parle d'elle-même ("moi", "j'ai"), tu dois identifier qui parle en fonction du contexte que je te fournis plus tard ou assumer que l'auteur est implicitement inclus.
    
    Texte à analyser : "{text}"
    """
    
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractedTransaction,
            temperature=0.0
        ),
    )
    
    return ExtractedTransaction.model_validate_json(response.text)
