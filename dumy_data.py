
from db import SessionLocal, Listing

db = SessionLocal()

real_listings = [
    Listing(
        title="3 Marla Residential Plot - City Life Homes",
        location="3-KM Link Bedian Road, Sua Asal, Main Ferozpur Road, Lahore",
        price=1800000,
        bedrooms=0,
        description=(
            "3 Marla residential plot in City Life Homes with 4-year easy payment plan. "
            "Down payment: PKR 600,000 | Monthly installment: PKR 25,000 | Total price: PKR 1,800,000. "
        ),
    ),
    Listing(
        title="5 Marla Residential Plot - City Life Homes",
        location="3-KM Link Bedian Road, Sua Asal, Main Ferozpur Road, Lahore",
        price=2750000,
        bedrooms=0,
        description=(
            "5 Marla residential plot in City Life Homes with 4-year easy payment plan. "
            "Down payment: PKR 1,000,000 | Monthly installment: PKR 35,000 | Total price: PKR 2,750,000. "
            "Registry/Intiqal prominent. Possession at 50% payment, plots available on ground. "

        ),
    ),
]

db.add_all(real_listings)
db.commit()
db.close()
print(f"Added {len(real_listings)} real listings.")