from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
import asyncio

router = APIRouter()

class PaymentMethodEnum(str, Enum):
    CASH = "CASH"
    CARD = "CARD"

class PaymentRequest(BaseModel):
    amount: float
    orderId: str
    paymentMethod: PaymentMethodEnum

@router.post("/process")
async def process_payment(request: PaymentRequest):
    """
    Procesar pago según el método seleccionado
    - CASH: Pago en efectivo (se registra, no requiere validación)
    - CARD: Pago con datáfono/tarjeta (simulación de validación)
    """
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    
    if request.paymentMethod == PaymentMethodEnum.CASH:
        # Pago en efectivo - siempre exitoso
        return {
            "success": True,
            "message": "Payment method registered: Cash on delivery",
            "transactionId": f"CASH-{int(asyncio.get_event_loop().time() * 1000)}",
            "amount": request.amount,
            "orderId": request.orderId,
            "paymentMethod": "CASH"
        }
    
    elif request.paymentMethod == PaymentMethodEnum.CARD:
        # Pago con datáfono - simular procesamiento
        await asyncio.sleep(2)
        
        # Simular aprobación (95% éxito)
        import random
        success = random.random() > 0.05
        
        if success:
            transaction_id = f"CARD-{int(asyncio.get_event_loop().time() * 1000)}-{random.randint(1000, 9999)}"
            return {
                "success": True,
                "message": "Card payment processed successfully",
                "transactionId": transaction_id,
                "amount": request.amount,
                "orderId": request.orderId,
                "paymentMethod": "CARD"
            }
        else:
            raise HTTPException(
                status_code=402,
                detail="Card payment was rejected. Please verify your card and try again."
            )

