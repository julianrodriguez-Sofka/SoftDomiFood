from fastapi import APIRouter, Query
from typing import Optional
from services.database_service import get_products, get_product_by_id

router = APIRouter()

@router.get("/")
async def get_products_list(
    category: Optional[str] = Query(None),
    available: Optional[bool] = Query(None),
    include_out_of_stock: bool = Query(False, description="Incluir productos sin stock (solo para admin)")
):
    """Obtener lista de productos. Por defecto solo muestra productos con stock > 0"""
    products = await get_products(category=category, available=available, include_out_of_stock=include_out_of_stock)
    return {"products": products}

@router.get("/{product_id}")
async def get_product(product_id: str):
    """Obtener producto por ID"""
    product = await get_product_by_id(product_id)
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}

