# FastAPI + Supabase Products API (Windows-friendly)

A complete scaffold using **FastAPI**, **SQLAlchemy (async)** and **Supabase** with a `products` table.

## 1) Setup (PowerShell)
```powershell
# go into the folder you unzipped this project to
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) Configure database
Edit **.env** and put your **Session pooler** connection string (port 6543). Example:
```
DATABASE_URL=postgresql+asyncpg://postgres.<project-ref>:<url-encoded-password>@aws-1-us-east-2.pooler.supabase.com:6543/postgres
```
> If you see SSL errors at runtime, add `?sslmode=require` at the end.

## 3) Create table & extension in Supabase (SQL editor)
If you haven't created the table yet, run:
```sql
create extension if not exists pgcrypto;
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
);
```

## 4) (Optional) Seed example data
```powershell
python -m scripts.seed_products
```

## 5) Run the API
```powershell
uvicorn app.main:app --reload --env-file .\.env
```
Open http://127.0.0.1:8000/docs

### Endpoints
- `GET /products` (filters, sorting, pagination)
- `GET /products/{id}`
- `GET /products/sku/{sku}`
- `POST /products`
- `PATCH /products/{id}`
- `DELETE /products/{id}`

## Notes
- If you **have to** use the *Transaction pooler* (not recommended), edit `app/core/database.py` and add:
  ```python
  connect_args={"statement_cache_size": 0}
  ```
  to `create_async_engine(...)` to avoid prepared statement issues.
