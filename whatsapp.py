# # import httpx
# # from typing import Optional
# # from config import settings
# # from schema import IncomingMessage

# # # : confirm this is still the current Graph API version before going live
# # GRAPH_API_URL = f"https://graph.facebook.com/v21.0/{settings.whatsapp_phone_number_id}/messages"


# # def send_message(to: str, text: str) -> dict:
# #     headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
# #     payload = {
# #         "messaging_product": "whatsapp",
# #         "to": to,
# #         "type": "text",
# #         "text": {"body": text},
# #     }
# #     response = httpx.post(GRAPH_API_URL, headers=headers, json=payload)
# #     response.raise_for_status()
# #     return response.json()


# # #  template_name must match a template you created and got approved in Meta's dashboard
# # def send_template_message(to: str, template_name: str, language_code: str = "en") -> dict:
# #     headers = {"Authorization": f"Bearer {settings.whatsapp_token}"}
# #     payload = {
# #         "messaging_product": "whatsapp",
# #         "to": to,
# #         "type": "template",
# #         "template": {"name": template_name, "language": {"code": language_code}},
# #     }
# #     response = httpx.post(GRAPH_API_URL, headers=headers, json=payload)
# #     response.raise_for_status()
# #     return response.json()


# # def verify_webhook(mode: str, token: str, challenge: str) -> Optional[str]:
# #     if mode == "subscribe" and token == settings.whatsapp_verify_token:
# #         return challenge
# #     return None


# # def parse_incoming_message(payload: dict) -> Optional[IncomingMessage]:
# #     try:
# #         value = payload["entry"][0]["changes"][0]["value"]
# #         messages = value.get("messages")
# #         if not messages:
# #             return None  # this was a status update, not a real message

# #         message = messages[0]
# #         if message["type"] != "text":
# #             return None  # skip images, audio, etc. for now

# #         return IncomingMessage(
# #             phone_number=message["from"],
# #             content=message["text"]["body"],
# #         )
# #     except (KeyError, IndexError):
# #         return None

# import httpx
# from typing import Optional
# from config import settings
# from schema import IncomingMessage

# GUPSHUP_URL = "https://api.gupshup.io/wa/api/v1/msg"


# def send_message(to: str, text: str) -> dict:
#     headers = {
#         "apikey": settings.gupshup_api_key,
#         "Content-Type": "application/x-www-form-urlencoded",
#     }
#     data = {
#         "channel": "whatsapp",
#         "source": settings.gupshup_source_number,
#         "destination": to,
#         "src.name": settings.gupshup_app_name,
#         "message": '{"type":"text","text":"' + text.replace('"', '\\"') + '"}',
#     }
#     response = httpx.post(GUPSHUP_URL, headers=headers, data=data)
#     response.raise_for_status()
#     return response.json()


# def parse_incoming_message(payload: dict) -> Optional[IncomingMessage]:
#     try:
#         if payload.get("type") != "message":
#             return None  # not an inbound text message (could be a status event)

#         message = payload.get("payload", {})
#         if message.get("type") != "text":
#             return None  # skip images, audio, etc. for now

#         return IncomingMessage(
#             phone_number=payload.get("source", ""),
#             content=message.get("payload", {}).get("text", ""),
#         )
#     except (KeyError, AttributeError):
#         return None

# import httpx
# from typing import Optional
# from config import settings
# from schema import IncomingMessage

# GUPSHUP_URL = "https://api.gupshup.io/wa/api/v1/msg"


# def send_message(to: str, text: str) -> dict:
#     headers = {
#         "apikey": settings.gupshup_api_key,
#         "Content-Type": "application/x-www-form-urlencoded",
#     }
#     data = {
#         "channel": "whatsapp",
#         "source": settings.gupshup_source_number,
#         "destination": to,
#         "src.name": settings.gupshup_app_name,
#         "message": '{"isHSM":"false","type":"text","text":"' + text.replace('"', '\\"') + '"}',
#     }
#     response = httpx.post(GUPSHUP_URL, headers=headers, data=data)
#     response.raise_for_status()
#     return response.json()


# def parse_incoming_message(payload: dict) -> Optional[IncomingMessage]:
#     try:
#         if payload.get("type") != "message":
#             return None  # not an inbound text message (could be a status event)

#         message = payload.get("payload", {})
#         if message.get("type") != "text":
#             return None  # skip images, audio, etc. for now

#         return IncomingMessage(
#             phone_number=message.get("source", ""),
#             content=message.get("payload", {}).get("text", ""),
#         )
#     except (KeyError, AttributeError):
#         return None

import json
import httpx
from typing import Optional
from config import settings
from schema import IncomingMessage

GUPSHUP_URL = "https://api.gupshup.io/wa/api/v1/msg"


def send_message(to: str, text: str) -> dict:
    headers = {
        "apikey": settings.gupshup_api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "channel": "whatsapp",
        "source": settings.gupshup_source_number,
        "destination": to,
        "src.name": settings.gupshup_app_name,
        "message": json.dumps({"isHSM": "false", "type": "text", "text": text}),
    }
    response = httpx.post(GUPSHUP_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()


def send_welcome_template(to: str, lead_name: str, business_name: str, template_id: str) -> dict:
    """Sends the approved 'real_estate_lead_welcome' template - required for a lead's first-ever
    contact, since a free-text session window doesn't exist yet for a brand-new lead.
    template_id comes from Gupshup's Templates tab once the template is approved."""
    headers = {
        "apikey": settings.gupshup_api_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = [lead_name or "there", business_name]
    message = json.dumps({"isHSM": "true", "type": "text", "id": template_id, "params": params})
    data = {
        "channel": "whatsapp",
        "source": settings.gupshup_source_number,
        "destination": to,
        "src.name": settings.gupshup_app_name,
        "message": message,
    }
    response = httpx.post(GUPSHUP_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()


def parse_incoming_message(payload: dict) -> Optional[IncomingMessage]:
    try:
        if payload.get("type") != "message":
            return None  # not an inbound text message (could be a status event)

        message = payload.get("payload", {})
        if message.get("type") != "text":
            return None  # skip images, audio, etc. for now

        return IncomingMessage(
            phone_number=message.get("source", ""),
            content=message.get("payload", {}).get("text", ""),
            message_id=message.get("id"),
        )
    except (KeyError, AttributeError):
        return None