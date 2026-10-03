import httpx
from typing import Optional
from app.core.config import settings

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

async def send_message(chat_id: int, text: str, reply_markup: Optional[dict] = None) -> None:
    """Envoie un message sur Telegram, potentiellement avec un clavier Inline."""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

async def answer_callback_query(callback_query_id: str, text: str = "", show_alert: bool = False) -> None:
    """Répond à un clic sur un bouton (obligatoire pour enlever l'icône de chargement sur le client)."""
    url = f"{TELEGRAM_API_URL}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

async def edit_message_text(chat_id: int, message_id: int, text: str) -> None:
    """Modifie le texte d'un message existant (ex: remplacer les boutons par 'Validé !')."""
    url = f"{TELEGRAM_API_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
