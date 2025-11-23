from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from routers.auth import get_current_user
from services.database_service import create_order, get_order_status, get_all_orders, get_user_orders, get_user_orders
from services.rabbitmq import publish_order

router = APIRouter()

class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"

class OrderItem(BaseModel):
    productId: str
    quantity: int
    price: Optional[float] = None  # Opcional, se calculará si no se envía

class CreateOrderRequest(BaseModel):
    addressId: str
    items: List[OrderItem]
    total: Optional[float] = None  # Opcional, se calculará si no se envía
    paymentMethod: PaymentMethod = PaymentMethod.CASH
    notes: Optional[str] = None

@router.post("/")
async def create_new_order(
    order_data: CreateOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """Crear nuevo pedido - Solo usuarios autenticados"""
    try:
        # Validar que el usuario esté autenticado
        if not current_user or not current_user.get("userId"):
            raise HTTPException(status_code=401, detail="Usuario no autenticado")
        
        # Validar que haya items
        if not order_data.items or len(order_data.items) == 0:
            raise HTTPException(status_code=422, detail="El pedido debe contener al menos un producto")
        
        # Validar que haya dirección
        if not order_data.addressId:
            raise HTTPException(status_code=422, detail="Debe seleccionar una dirección de entrega")
        
        # Importar función para obtener productos
        from services.database_service import get_product_by_id
        
        # Validar items y calcular precios si no se enviaron
        validated_items = []
        calculated_total = 0.0
        
        for item in order_data.items:
            if item.quantity <= 0:
                raise HTTPException(status_code=422, detail=f"La cantidad del producto {item.productId} debe ser mayor a 0")
            
            # Obtener producto para validar y obtener precio
            product = await get_product_by_id(item.productId)
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto {item.productId} no encontrado")
            
            if not product.get("isAvailable", True):
                raise HTTPException(status_code=400, detail=f"El producto {product.get('name')} no está disponible")
            
            # Usar precio del producto si no se envió
            item_price = item.price if item.price is not None else product.get("price", 0)
            item_total = item_price * item.quantity
            calculated_total += item_total
            
            validated_items.append({
                "productId": item.productId,
                "quantity": item.quantity,
                "price": item_price
            })
        
        # Usar total calculado si no se envió
        final_total = order_data.total if order_data.total is not None else calculated_total
        
        if final_total <= 0:
            raise HTTPException(status_code=422, detail="El total del pedido debe ser mayor a 0")
        
        # Crear orden en la base de datos
        order = await create_order(
            user_id=current_user["userId"],
            address_id=order_data.addressId,
            items=validated_items,
            total=final_total,
            payment_method=order_data.paymentMethod.value,
            notes=order_data.notes
        )
        
        if not order:
            raise HTTPException(status_code=500, detail="Error creating order")
        
        # Publicar orden a RabbitMQ
        try:
            await publish_order(order)
        except Exception as mq_error:
            # Log el error pero no fallar la creación de la orden
            print(f"⚠️  Error publicando a RabbitMQ: {mq_error}")
            print("   La orden se creó pero no se publicó a la cola")
        
        return {"order": order, "message": "Order created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener estado de un pedido"""
    order = await get_order_status(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order": order}

@router.get("/")
async def get_orders(
    current_user: dict = Depends(get_current_user)
):
    """Obtener todos los pedidos del usuario autenticado"""
    # Validar que el usuario esté autenticado
    if not current_user or not current_user.get("userId"):
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    
    # Solo devolver órdenes del usuario actual
    orders = await get_user_orders(current_user["userId"])
    return {"orders": orders}
