# from typing import Optional
# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     # database
#     database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/real_estate_agent"

#     # anthropic / claude
#     anthropic_api_key: Optional[str] = None

#     # google gemini (alternative to claude while testing)
#     google_api_key: Optional[str] = None

#     # voyage ai (embeddings for rag)
#     voyage_api_key: Optional[str] = None

#     # whatsapp cloud api - optional for now, needed only once you wire up whatsapp
#     whatsapp_token: Optional[str] = None
#     whatsapp_phone_number_id: Optional[str] = None
#     whatsapp_verify_token: Optional[str] = None

#     # gupshup (whatsapp)
#     gupshup_api_key: Optional[str] = None
#     gupshup_source_number: Optional[str] = None
#     gupshup_app_name: Optional[str] = None

#     # app
#     app_env: str = "development"

#     class Config:
#         env_file = ".env"


# settings = Settings()


from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # database
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/real_estate_agent"

    # anthropic / claude
    anthropic_api_key: Optional[str] = None

    # google gemini (alternative to claude while testing)
    google_api_key: Optional[str] = None

    # voyage ai (embeddings for rag)
    voyage_api_key: Optional[str] = None

    # whatsapp cloud api - optional for now, needed only once you wire up whatsapp
    whatsapp_token: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_verify_token: Optional[str] = None

    # gupshup (whatsapp)
    gupshup_api_key: Optional[str] = None
    gupshup_source_number: Optional[str] = None
    gupshup_app_name: Optional[str] = None
    gupshup_welcome_template_id: Optional[str] = None

    # per-client branding - this is what makes the welcome template reusable across clients
    business_name: str = "our real estate team"

    # app
    app_env: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()