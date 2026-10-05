import uuid
import json
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Header, HTTPException, Request, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.api.deps import get_db
from app.core.config import settings
from app.db.models import Membre, TelegramUpdate, PendingTransaction, TypeTransactionEnum, SourceEnum, Transaction, TransactionParticipant
from app.services import telegram, nlp, balances
from app.schemas.transaction import TransactionCreate

router = APIRouter()

async def process_text_message(message: dict, db: Session):
    chat_id = message["chat"]["id"]
    from_id = str(message["from"]["id"])
    text = message.get("text", "")
    
    # Trouver le membre
    auteur = db.query(Membre).filter(Membre.telegram_user_id == from_id).first()
    if not auteur:
        await telegram.send_message(chat_id, "❌ Vous n'êtes pas reconnu comme membre du groupe.")
        return

    # Dictionnaire des membres pour Gemini
    membres = db.query(Membre).filter(Membre.is_active == True).all()
    membres_dict = {m.nom: m.id for m in membres}
    
    try:
        extracted = await nlp.parse_expense_text(text, membres_dict)
    except Exception as e:
        await telegram.send_message(chat_id, "🤖 Je n'ai pas réussi à comprendre la dépense. Réessayez de formuler différemment.")
        return
        
    if extracted.is_remboursement:
        await telegram.send_message(chat_id, "🚫 <b>Refusé :</b> Les remboursements entre membres doivent être saisis via l'interface Web pour garantir l'intégrité de la caisse.")
        return
        
    # Créer la pending transaction
    pending_id = str(uuid.uuid4())
    
    txn_data = {
        "type_transaction": TypeTransactionEnum.DEPENSE.value,
        "categorie": extracted.categorie,
        "details": text,
        "montant": extracted.montant,
        "date_transaction": date.today().isoformat(),
        "id_payeur": auteur.id,
        "participants": extracted.participants_ids,
        "source": SourceEnum.TELEGRAM.value
    }
    
    pt = PendingTransaction(
        id=pending_id,
        payload=json.dumps(txn_data),
        telegram_user_id=from_id
    )
    db.add(pt)
    db.commit()
    
    # Préparer les noms pour l'affichage
    part_names = [m.nom for m in membres if m.id in extracted.participants_ids]
    
    summary = f"<b>Nouvelle Dépense :</b>\n"
    summary += f"💰 Montant : {extracted.montant} €\n"
    summary += f"🏷️ Catégorie : {extracted.categorie}\n"
    summary += f"👥 Pour : {', '.join(part_names)}\n\n"
    summary += f"Confirmez-vous ?"
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Valider", "callback_data": f"valider:{pending_id}"},
                {"text": "❌ Annuler", "callback_data": f"annuler:{pending_id}"}
            ]
        ]
    }
    
    await telegram.send_message(chat_id, summary, reply_markup=keyboard)


async def process_callback_query(callback_query: dict, db: Session):
    cb_id = callback_query["id"]
    from_id = str(callback_query["from"]["id"])
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    data = callback_query.get("data", "")
    
    if not data.startswith("valider:") and not data.startswith("annuler:"):
        await telegram.answer_callback_query(cb_id, text="Action inconnue")
        return
        
    action, pending_id = data.split(":")
    
    pt = db.query(PendingTransaction).filter(PendingTransaction.id == pending_id).first()
    if not pt:
        await telegram.answer_callback_query(cb_id, text="Transaction expirée ou introuvable", show_alert=True)
        if message_id:
            await telegram.edit_message_text(chat_id, message_id, "Transaction expirée.")
        return
        
    if pt.telegram_user_id != from_id:
        await telegram.answer_callback_query(cb_id, text="Vous n'êtes pas l'auteur de cette dépense.", show_alert=True)
        return
        
    if action == "annuler":
        db.delete(pt)
        db.commit()
        await telegram.answer_callback_query(cb_id, text="Dépense annulée")
        if message_id:
            await telegram.edit_message_text(chat_id, message_id, "<i>Dépense annulée par l'utilisateur.</i>")
        return
        
    try:
        payload = json.loads(pt.payload)
        txn_in = TransactionCreate(**payload)
        auteur = db.query(Membre).filter(Membre.telegram_user_id == pt.telegram_user_id).first()
        
        db_obj = Transaction(
            type_transaction=txn_in.type_transaction,
            categorie=txn_in.categorie,
            details=txn_in.details,
            montant=txn_in.montant,
            date_transaction=txn_in.date_transaction,
            id_payeur=txn_in.id_payeur,
            id_auteur=auteur.id,
            source=txn_in.source
        )
        db.add(db_obj)
        db.flush()
        
        if txn_in.participants:
            for p_id in txn_in.participants:
                db.add(TransactionParticipant(id_transaction=db_obj.id, id_membre=p_id))
                
        db.delete(pt)
        db.commit()
        
        await telegram.answer_callback_query(cb_id, text="Validé avec succès !")
        if message_id:
            await telegram.edit_message_text(chat_id, message_id, f"✅ <b>Dépense validée !</b> ({txn_in.montant} €)")
            
    except Exception as e:
        db.rollback()
        await telegram.answer_callback_query(cb_id, text=f"Erreur: {str(e)}", show_alert=True)


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_telegram_bot_api_secret_token: str = Header(None)
):
    if x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    payload = await request.json()
    update_id = payload.get("update_id")
    
    if not update_id:
        return {"ok": True}
        
    try:
        db.add(TelegramUpdate(update_id=update_id, status="DONE"))
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"ok": True} # Requête concurrente / déjà traitée
    
    try:
        if "message" in payload and "text" in payload["message"]:
            await process_text_message(payload["message"], db)
        elif "callback_query" in payload:
            await process_callback_query(payload["callback_query"], db)
    except Exception as e:
        print(f"Error processing update: {e}")
        pass
        
    return {"ok": True}
