from typing import Optional, Sequence
from decimal import Decimal
from sqlalchemy import select, update, delete, asc, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.product import Product

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, *, search: Optional[str], min_price: Optional[Decimal], max_price: Optional[Decimal],
                   is_active: Optional[bool], sort_by: str, sort_order: str, limit: int, offset: int) -> Sequence[Product]:
        stmt = select(Product)
        if search:
            p = f"%{search.lower()}%"
            stmt = stmt.where(
                func.lower(Product.sku).like(p) |
                func.lower(Product.name).like(p) |
                func.lower(Product.description).like(p)
            )
        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)
        if is_active is not None:
            stmt = stmt.where(Product.is_active == is_active)

        sort_column = {
            "created_at": Product.created_at,
            "updated_at": Product.updated_at,
            "price": Product.price,
            "name": Product.name,
            "stock": Product.stock,
            "sku": Product.sku
        }.get(sort_by, Product.created_at)

        stmt = stmt.order_by(desc(sort_column) if sort_order == "desc" else asc(sort_column)).limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        res = await self.session.execute(select(Product).where(Product.id == product_id))
        return res.scalars().first()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        res = await self.session.execute(select(Product).where(Product.sku == sku))
        return res.scalars().first()

    async def create(self, **fields) -> Product:
        product = Product(**fields)
        self.session.add(product)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise
        await self.session.refresh(product)
        return product

    async def update(self, product_id: str, **fields) -> Optional[Product]:
        if not fields:
            return await self.get_by_id(product_id)
        stmt = update(Product).where(Product.id == product_id).values(**fields).returning(Product)
        res = await self.session.execute(stmt)
        await self.session.commit()
        row = res.fetchone()
        return row[0] if row else None

    async def delete(self, product_id: str) -> bool:
        res = await self.session.execute(delete(Product).where(Product.id == product_id))
        await self.session.commit()
        return res.rowcount > 0
