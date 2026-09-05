from fastapi import FastAPI, Request, Response
from db import SessionLocal, Lead, Message
from agent import app as agent_graph
from whatsapp import verify_webhook, parse_incoming_message, send_message

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/webhooks/whatsapp")
def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    result = verify_webhook(mode, token, challenge)
    if result is None:
        return Response(status_code=403)
    return Response(content=result, media_type="text/plain")


@app.post("/webhooks/whatsapp")
async def receive_whatsapp(request: Request):
    payload = await request.json()
    incoming = parse_incoming_message(payload)

    if incoming is None:
        return {"status": "ignored"}

    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.phone_number == incoming.phone_number).first()
    if lead is None:
        lead = Lead(phone_number=incoming.phone_number, source="whatsapp_organic")
        db.add(lead)
        db.commit()
        db.refresh(lead)

    db.add(Message(lead_id=lead.id, sender="lead", content=incoming.content))
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
    reply_text = result["messages"][-1].content

    db.add(Message(lead_id=lead.id, sender="agent", content=reply_text))
    db.commit()
    db.close()

    send_message(to=incoming.phone_number, text=reply_text)

    return {"status": "replied"}


@app.get("/leads/{lead_id}/status")
def lead_status(lead_id: int):
    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    db.close()
    if lead is None:
        return {"error": "not found"}
    return {"id": lead.id, "status": lead.status, "tier": lead.tier, "phone_number": lead.phone_number}