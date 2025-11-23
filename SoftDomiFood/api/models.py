from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    DELIVERY = "DELIVERY"

class ProductCategory(str, enum.Enum):
    SALCHIPAPAS = "SALCHIPAPAS"
    BEBIDAS = "BEBIDAS"
    ADICIONALES = "ADICIONALES"
    COMBOS = "COMBOS"

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    ON_DELIVERY = "ON_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

# Nota: Estas son solo para referencia. La BD real usa Prisma.
# Usamos SQLAlchemy solo para queries directas cuando sea necesario.

