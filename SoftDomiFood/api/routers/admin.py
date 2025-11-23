from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from services.database_service import get_all_orders, update_order_status, create_product, update_product, get_all_customers_with_addresses
from routers.auth import get_current_user

router = APIRouter()

class UpdateStatusRequest(BaseModel):
    status: str

class CreateProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image: Optional[str] = None
    isAvailable: bool = True

class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image: Optional[str] = None
    isAvailable: Optional[bool] = None

@router.get("/orders")
async def get_all_orders_admin(current_user: dict = Depends(get_current_user)):
    """Obtener todos los pedidos (solo admin)"""
    # El payload del token tiene 'role' directamente
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    orders = await get_all_orders()
    return {"orders": orders}

@router.patch("/orders/{order_id}/status")
async def update_order_status_admin(
    order_id: str,
    request: UpdateStatusRequest,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar estado de pedido (solo admin)"""
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    valid_statuses = ["PENDING", "CONFIRMED", "PREPARING", "READY", "ON_DELIVERY", "DELIVERED", "CANCELLED"]
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order = await update_order_status(order_id, request.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "message": "Order status updated successfully",
        "order": order
    }

@router.post("/products")
async def create_new_product(
    request: CreateProductRequest,
    current_user: dict = Depends(get_current_user)
):
    """Crear nuevo producto (solo admin)"""
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validar categoría
    valid_categories = ["SALCHIPAPAS", "BEBIDAS", "ADICIONALES", "COMBOS"]
    if request.category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    product = await create_product(
        name=request.name,
        description=request.description,
        price=request.price,
        category=request.category,
        image=request.image,
        is_available=request.isAvailable
    )
    
    if not product:
        raise HTTPException(status_code=500, detail="Error creating product")
    
    return {
        "message": "Product created successfully",
        "product": product
    }

@router.put("/products/{product_id}")
async def update_existing_product(
    product_id: str,
    request: UpdateProductRequest,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar producto existente (solo admin)"""
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validar categoría si se proporciona
    if request.category is not None:
        valid_categories = ["SALCHIPAPAS", "BEBIDAS", "ADICIONALES", "COMBOS"]
        if request.category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    product = await update_product(
        product_id=product_id,
        name=request.name,
        description=request.description,
        price=request.price,
        category=request.category,
        image=request.image,
        is_available=request.isAvailable
    )
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "message": "Product updated successfully",
        "product": product
    }

@router.get("/customers")
async def get_all_customers(current_user: dict = Depends(get_current_user)):
    """Obtener todos los clientes con sus direcciones (solo admin)"""
    user_role = current_user.get("role")
    if user_role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    customers = await get_all_customers_with_addresses()
    return {"customers": customers}

