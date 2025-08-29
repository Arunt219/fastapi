from typing import Optional, Sequence
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from app.repositories.product_repo import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.product import Product

class NotFoundError(Exception):
    pass

class DuplicateError(Exception):
    pass

def _is_unique_violation(err: IntegrityError) -> bool:
    # asyncpg UniqueViolation SQLSTATE = '23505'
    try:
        return getattr(err.orig, 'sqlstate', None) == '23505'
    except Exception:
        return False

class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def list_products(self, *, search: Optional[str], min_price: Optional[Decimal], max_price: Optional[Decimal],
                            is_active: Optional[bool], sort_by: str, sort_order: str, limit: int, offset: int) -> Sequence[Product]:
        return await self.repo.list(search=search, min_price=min_price, max_price=max_price,
                                    is_active=is_active, sort_by=sort_by, sort_order=sort_order,
                                    limit=limit, offset=offset)

    async def get_product(self, product_id: str) -> Product:
        p = await self.repo.get_by_id(product_id)
        if not p:
            raise NotFoundError("Product not found")
        return p

    async def get_product_by_sku(self, sku: str) -> Product:
        p = await self.repo.get_by_sku(sku)
        if not p:
            raise NotFoundError("Product not found")
        return p

    async def create_product(self, data: ProductCreate) -> Product:
        try:
            return await self.repo.create(**data.model_dump())
        except IntegrityError as e:
            if _is_unique_violation(e):
                raise DuplicateError("SKU already exists")
            raise

    async def update_product(self, product_id: str, data: ProductUpdate) -> Product:
        fields = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
        p = await self.repo.update(product_id, **fields)
        if not p:
            raise NotFoundError("Product not found")
        return p

    async def delete_product(self, product_id: str) -> None:
        ok = await self.repo.delete(product_id)
        if not ok:
            raise NotFoundError("Product not found")
