from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from uuid import UUID

class ProductRead(BaseModel):
    id: UUID
    sku: str
    name: str
    description: Optional[str] = None
    price: Decimal
    currency: str
    stock: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    price: Decimal = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    stock: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)

class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(default=None, min_length=1, max_length=64)
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    price: Optional[Decimal] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    stock: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
