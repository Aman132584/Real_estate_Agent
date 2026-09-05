# from fastapi import FastAPI, Request
# from db import SessionLocal, Lead, Message
# from agent import app as agent_graph
# from whatsapp import parse_incoming_message, send_message

# app = FastAPI()


# def extract_text(content):
#     if isinstance(content, list):
#         return content[0]["text"]
#     return content


# @app.get("/health")
# def health():
#     return {"status": "ok"}


# @app.post("/webhooks/whatsapp")
# async def receive_whatsapp(request: Request):
#     payload = await request.json()
#     print("RAW PAYLOAD:", payload)  # temporary debug line, remove once parsing is confirmed correct
#     incoming = parse_incoming_message(payload)

#     if incoming is None:
#         return {"status": "ignored"}

#     db = SessionLocal()
#     lead = db.query(Lead).filter(Lead.phone_number == incoming.phone_number).first()
#     if lead is None:
#         lead = Lead(phone_number=incoming.phone_number, source="whatsapp_organic")
#         db.add(lead)
#         db.commit()
#         db.refresh(lead)

#     db.add(Message(lead_id=lead.id, sender="lead", content=incoming.content))
#     db.commit()

#     history = (
#         db.query(Message)
#         .filter(Message.lead_id == lead.id)
#         .order_by(Message.created_at)
#         .all()
#     )
#     langgraph_messages = [
#         {"role": "user" if m.sender == "lead" else "assistant", "content": m.content}
#         for m in history
#     ]

#     result = agent_graph.invoke({"messages": langgraph_messages})
#     reply_text = extract_text(result["messages"][-1].content)

#     db.add(Message(lead_id=lead.id, sender="agent", content=reply_text))
#     db.commit()
#     db.close()

#     try:
#         send_message(to=incoming.phone_number, text=reply_text)
#     except Exception as e:
#         print(f"[skipped sending - no WhatsApp credentials yet] would have sent: {reply_text}")

#     return {"status": "replied", "reply": reply_text}


# @app.get("/leads/{lead_id}/status")
# def lead_status(lead_id: int):
#     db = SessionLocal()
#     lead = db.query(Lead).filter(Lead.id == lead_id).first()
#     db.close()
#     if lead is None:
#         return {"error": "not found"}
#     return {"id": lead.id, "status": lead.status, "tier": lead.tier, "phone_number": lead.phone_number}

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db import SessionLocal, Lead, Message
from agent import app as agent_graph
from whatsapp import parse_incoming_message, send_message, send_welcome_template
from config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual dashboard's domain once deployed
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_text(content):
    if isinstance(content, list):
        return content[0]["text"]
    return content


def parse_meta_lead(payload: dict):
    """Extract name/phone from a Meta Lead Ads webhook payload.
    Real payload structure: entry[].changes[].value with leadgen_id, field_data[].
    For now we accept a simplified fake shape for testing: {"name": ..., "phone_number": ...}
    """
    try:
        # simplified/fake shape, used for local testing before touching Meta's real dashboard
        if "phone_number" in payload:
            return {"name": payload.get("name"), "phone_number": payload["phone_number"]}

        # real Meta Lead Ads shape (field_data is a list of {name, values})
        value = payload["entry"][0]["changes"][0]["value"]
        field_data = value.get("field_data", [])
        fields = {f["name"]: f["values"][0] for f in field_data if f.get("values")}
        return {
            "name": fields.get("full_name") or fields.get("first_name"),
            "phone_number": fields.get("phone_number"),
        }
    except (KeyError, IndexError, TypeError):
        return None

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhooks/whatsapp")
async def receive_whatsapp(request: Request):
    payload = await request.json()
    print("RAW PAYLOAD:", payload)  # temporary debug line, remove once parsing is confirmed correct
    incoming = parse_incoming_message(payload)

    if incoming is None:
        return {"status": "ignored"}

    db = SessionLocal()

    if incoming.message_id:
        already_processed = db.query(Message).filter(Message.message_id == incoming.message_id).first()
        if already_processed:
            db.close()
            return {"status": "duplicate_ignored"}

    lead = db.query(Lead).filter(Lead.phone_number == incoming.phone_number).first()
    if lead is None:
        lead = Lead(phone_number=incoming.phone_number, source="whatsapp_organic")
        db.add(lead)
        db.commit()
        db.refresh(lead)

    db.add(Message(lead_id=lead.id, sender="lead", content=incoming.content, message_id=incoming.message_id))
    db.commit()

    history = (
        db.query(Message)
        .filter(Message.lead_id == lead.id)
        .order_by(Message.created_at)
        .all()
    )
    langgraph_messages = [
        {"role": "user" if m.sender == "lead" else "assistant", "content": m.content}
        for m in history
    ]

    result = agent_graph.invoke({"messages": langgraph_messages})
    reply_text = extract_text(result["messages"][-1].content)

    db.add(Message(lead_id=lead.id, sender="agent", content=reply_text))
    db.commit()
    db.close()

    try:
        send_message(to=incoming.phone_number, text=reply_text)
    except Exception as e:
        print(f"[skipped sending - no WhatsApp credentials yet] would have sent: {reply_text}")

    return {"status": "replied", "reply": reply_text}


@app.get("/leads/{lead_id}/status")
def lead_status(lead_id: int):
    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    db.close()
    if lead is None:
        return {"error": "not found"}
    return {"id": lead.id, "status": lead.status, "tier": lead.tier, "phone_number": lead.phone_number}


@app.get("/leads")
def list_leads():
    db = SessionLocal()
    leads = db.query(Lead).order_by(Lead.id.desc()).all()

    result = []
    for lead in leads:
        last_message = (
            db.query(Message)
            .filter(Message.lead_id == lead.id)
            .order_by(Message.created_at.desc())
            .first()
        )
        result.append({
            "id": lead.id,
            "name": lead.name or "Unknown",
            "phone_number": lead.phone_number,
            "last_message": last_message.content if last_message else "No messages yet",
            "last_message_at": last_message.created_at.isoformat() if last_message else None,
        })

    db.close()
    return {"leads": result}


@app.post("/webhooks/meta-leads")
async def receive_meta_lead(request: Request):
    payload = await request.json()
    print("RAW META LEAD PAYLOAD:", payload)  # temporary debug line

    lead_data = parse_meta_lead(payload)
    if lead_data is None or not lead_data.get("phone_number"):
        return {"status": "ignored"}

    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.phone_number == lead_data["phone_number"]).first()
    if lead is None:
        lead = Lead(
            name=lead_data.get("name"),
            phone_number=lead_data["phone_number"],
            source="meta_ad",
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
    db.close()

    opener_sent_via = "template" if settings.gupshup_welcome_template_id else "free_text_fallback"

    try:
        if settings.gupshup_welcome_template_id:
            send_welcome_template(
                to=lead.phone_number,
                lead_name=lead.name,
                business_name=settings.business_name,
                template_id=settings.gupshup_welcome_template_id,
            )
        else:
            # fallback while the template is still pending approval - only works if the lead
            # has messaged you within the last 24h, which usually isn't true for a brand-new lead
            opener_text = f"Hi {lead.name or 'there'}! Thanks for your interest in {settings.business_name}. What kind of property are you looking for?"
            send_message(to=lead.phone_number, text=opener_text)
    except Exception:
        print(f"[skipped sending - {opener_sent_via} not ready yet] lead_id={lead.id}")

    return {"status": "lead_created", "lead_id": lead.id, "opener_method": opener_sent_via}