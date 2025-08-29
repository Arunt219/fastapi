import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings

SAMPLE = [
    ("PRD-0001","Wireless Mouse","2.4G ergonomic mouse",Decimal("19.99"),"USD",120,True),
    ("PRD-0002","Mechanical Keyboard","Blue switches, RGB",Decimal("79.00"),"USD",60,True),
    ("PRD-0003","USB-C Hub 7-in-1","HDMI + PD + SD/TF",Decimal("34.50"),"USD",85,True),
    ("PRD-0004","27" 4K Monitor","IPS, 60Hz, HDR10",Decimal("289.99"),"USD",15,True),
    ("PRD-0005","Webcam 1080p","Built-in mic, privacy cover",Decimal("39.95"),"USD",50,True),
    ("PRD-0006","Noise-Cancel Headphones","Over-ear, BT 5.3",Decimal("129.00"),"USD",32,True),
    ("PRD-0007","Portable SSD 1TB","USB-C, 1,000MB/s",Decimal("99.99"),"USD",40,True),
    ("PRD-0008","Laptop Stand","Aluminum, adjustable",Decimal("24.00"),"USD",70,True),
    ("PRD-0009","HDMI 2.1 Cable","2m, 8K/60",Decimal("12.49"),"USD",200,True),
    ("PRD-0010","Desk Lamp","Dimmable, touch control",Decimal("21.00"),"USD",44,True),
    ("PRD-0011","Smart Plug (2-pack)","Works with Alexa/GA",Decimal("18.99"),"USD",110,True),
    ("PRD-0012","Power Bank 20,000mAh","PD 30W",Decimal("36.90"),"USD",55,True),
    ("PRD-0013","Bluetooth Speaker","IPX7, 12h playtime",Decimal("45.00"),"USD",28,True),
    ("PRD-0014","Action Camera 4K","EIS, waterproof case",Decimal("149.00"),"USD",10,True),
    ("PRD-0015","Tripod Stand","Aluminum, 160cm",Decimal("29.50"),"USD",33,True),
    ("PRD-0016","Wireless Charger","15W fast charge",Decimal("17.99"),"USD",75,True),
    ("PRD-0017","USB-C Cable (3-pack)","1m braided",Decimal("11.49"),"USD",180,True),
    ("PRD-0018","Smartwatch","Heart-rate, GPS",Decimal("199.00"),"USD",18,True),
    ("PRD-0019","Fitness Band","Sleep tracking",Decimal("49.00"),"USD",36,True),
    ("PRD-0020","Laptop Backpack","Water-resistant, 15.6"",Decimal("42.00"),"USD",22,True)
]

async def main():
    engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        await session.execute(text("create extension if not exists pgcrypto;"))
        await session.execute(text("""
            create table if not exists public.products (
              id uuid not null default gen_random_uuid (),
              sku text not null,
              name text not null,
              description text null,
              price numeric(10, 2) not null,
              currency text not null default 'USD'::text,
              stock integer not null default 0,
              is_active boolean not null default true,
              created_at timestamptz not null default now(),
              updated_at timestamptz not null default now(),
              constraint products_pkey primary key (id),
              constraint products_sku_key unique (sku),
              constraint products_price_check check ((price >= (0)::numeric)),
              constraint products_stock_check check ((stock >= 0))
            )
        """))
        ins = text("""
            insert into public.products (sku, name, description, price, currency, stock, is_active)
            values (:sku, :name, :description, :price, :currency, :stock, :is_active)
            on conflict (sku) do nothing
        """)
        for row in SAMPLE:
            await session.execute(ins, {
                "sku": row[0], "name": row[1], "description": row[2],
                "price": row[3], "currency": row[4], "stock": row[5], "is_active": row[6]
            })
        await session.commit()
        print(f"Seeded {len(SAMPLE)} products (skipping any duplicates).")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
