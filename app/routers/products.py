from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.repositories.product_repo import ProductRepository
from app.services.product_service import ProductService, NotFoundError, DuplicateError
from app.schemas.product import ProductRead, ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

def get_service(session: AsyncSession = Depends(get_session)) -> ProductService:
    repo = ProductRepository(session)
    return ProductService(repo)

@router.get("/", response_model=List[ProductRead])
async def list_products(
    search: Optional[str] = None,
    min_price: Optional[Decimal] = Query(default=None, ge=0),
    max_price: Optional[Decimal] = Query(default=None, ge=0),
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|price|name|stock|sku)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: ProductService = Depends(get_service),
):
    items = await svc.list_products(search=search, min_price=min_price, max_price=max_price,
                                    is_active=is_active, sort_by=sort_by, sort_order=sort_order,
                                    limit=limit, offset=offset)
    return items

@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: str, svc: ProductService = Depends(get_service)):
    try:
        return await svc.get_product(product_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/sku/{sku}", response_model=ProductRead)
async def get_product_by_sku(sku: str, svc: ProductService = Depends(get_service)):
    try:
        return await svc.get_product_by_sku(sku)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate, svc: ProductService = Depends(get_service)):
    try:
        return await svc.create_product(payload)
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(product_id: str, payload: ProductUpdate, svc: ProductService = Depends(get_service)):
    try:
        return await svc.update_product(product_id, payload)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, svc: ProductService = Depends(get_service)):
    try:
        await svc.delete_product(product_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
