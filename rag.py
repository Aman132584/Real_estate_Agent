import voyageai
from sqlalchemy import text
from config import settings
from db import SessionLocal, Listing

vo = voyageai.Client(api_key=settings.voyage_api_key)


def embed_text(text_to_embed: str, input_type: str) -> list:
    result = vo.embed([text_to_embed], model="voyage-4", input_type=input_type)
    return result.embeddings[0]


def ingest_listings():
    db = SessionLocal()
    listings = db.query(Listing).filter(Listing.embedding.is_(None)).all()

    for listing in listings:
        content = f"{listing.title}. Located in {listing.location}. {listing.description}"
        listing.embedding = embed_text(content, input_type="document")

    db.commit()
    db.close()
    print(f"Embedded {len(listings)} listings.")


def retrieve_listings(query: str, top_k: int = 3) -> list[Listing]:
    query_embedding = embed_text(query, input_type="query")
    db = SessionLocal()

    results = (
        db.query(Listing)
        .filter(Listing.status == "available")
        .order_by(Listing.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )

    db.close()
    return results


if __name__ == "__main__":
    ingest_listings()
    matches = retrieve_listings("3 bedroom place in DHA under 4 crore")
    for m in matches:
        print(m.title, "-", m.price)