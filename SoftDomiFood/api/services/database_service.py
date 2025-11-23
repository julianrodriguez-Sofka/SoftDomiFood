import asyncpg
import os
import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional

DATABASE_URL = os.getenv("DATABASE_URL", "")

async def get_connection():
    """Obtener conexión a PostgreSQL"""
    return await asyncpg.connect(DATABASE_URL)

def convert_uuid_to_str(data: Any) -> Any:
    """Convertir UUIDs y fechas a strings en diccionarios o listas"""
    if isinstance(data, dict):
        return {k: convert_value(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_uuid_to_str(item) for item in data]
    else:
        return convert_value(data)

def convert_value(value: Any) -> Any:
    """Convertir un valor individual (UUID, fecha, etc.) a string si es necesario"""
    if isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, dict):
        return convert_uuid_to_str(value)
    elif isinstance(value, list):
        return [convert_uuid_to_str(item) for item in value]
    return value

async def get_products(category: Optional[str] = None, available: Optional[bool] = None) -> List[Dict[str, Any]]:
    """Obtener lista de productos"""
    conn = await get_connection()
    try:
        query = "SELECT id, name, description, price, image, category, \"isAvailable\", \"createdAt\" FROM products WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = $1"
            params.append(category)
        
        if available is not None:
            param_index = len(params) + 1
            query += f" AND \"isAvailable\" = ${param_index}"
            params.append(available)
        
        query += " ORDER BY \"createdAt\" DESC"
        
        rows = await conn.fetch(query, *params)
        return [convert_uuid_to_str(dict(row)) for row in rows]
    finally:
        await conn.close()

async def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Obtener producto por ID"""
    conn = await get_connection()
    try:
        row = await conn.fetchrow(
            'SELECT id, name, description, price, image, category, "isAvailable" FROM products WHERE id = $1',
            product_id
        )
        return convert_uuid_to_str(dict(row)) if row else None
    finally:
        await conn.close()

async def create_order(user_id: str, address_id: str, items: List[Dict], total: float, payment_method: str = "CASH", notes: Optional[str] = None) -> Dict[str, Any]:
    """Crear pedido en la base de datos"""
    conn = await get_connection()
    try:
        async with conn.transaction():
            # Crear orden
            order_id = await conn.fetchval(
                """
                INSERT INTO orders (id, "userId", "addressId", status, total, "paymentMethod", notes, "createdAt", "updatedAt")
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, NOW(), NOW())
                RETURNING id
                """,
                user_id, address_id, "PENDING", total, payment_method, notes
            )
            
            # Crear items de la orden
            for item in items:
                await conn.execute(
                    """
                    INSERT INTO order_items (id, "orderId", "productId", quantity, price, "createdAt")
                    VALUES (gen_random_uuid(), $1, $2, $3, $4, NOW())
                    """,
                    order_id, item["productId"], item["quantity"], item["price"]
                )
            
            # Obtener orden completa con items
            order = await conn.fetchrow(
                """
                SELECT id, "userId", "addressId", status, total, "paymentMethod", notes, "createdAt", "updatedAt"
                FROM orders WHERE id = $1
                """,
                order_id
            )
            
            if not order:
                return None
            
            order_dict = convert_uuid_to_str(dict(order))
            
            # Agregar items a la orden
            order_items = await conn.fetch(
                """
                SELECT "productId", quantity, price
                FROM order_items
                WHERE "orderId" = $1
                """,
                order_id
            )
            # Convertir items y asegurar formato consistente
            items_list = []
            for item in order_items:
                item_dict = convert_uuid_to_str(dict(item))
                # Asegurar que productId esté presente (puede venir como product_id)
                if 'productId' not in item_dict and 'product_id' in item_dict:
                    item_dict['productId'] = item_dict.pop('product_id')
                items_list.append(item_dict)
            order_dict['items'] = items_list
            
            return order_dict
    finally:
        await conn.close()

async def get_order_status(order_id: str) -> Optional[Dict[str, Any]]:
    """Obtener estado de un pedido"""
    conn = await get_connection()
    try:
        order = await conn.fetchrow(
            """
            SELECT id, status, total, "paymentMethod", "createdAt", "updatedAt"
            FROM orders WHERE id = $1
            """,
            order_id
        )
        return convert_uuid_to_str(dict(order)) if order else None
    finally:
        await conn.close()

async def get_user_orders(user_id: str) -> List[Dict[str, Any]]:
    """Obtener todas las órdenes de un usuario específico"""
    conn = await get_connection()
    try:
        orders = await conn.fetch(
            """
            SELECT 
                o.id, 
                o.status, 
                o.total, 
                o."paymentMethod", 
                o.notes,
                o."createdAt", 
                o."updatedAt",
                o."addressId"
            FROM orders o
            WHERE o."userId" = $1
            ORDER BY o."createdAt" DESC
            """,
            user_id
        )
        
        orders_list = [convert_uuid_to_str(dict(row)) for row in orders]
        
        # Para cada orden, obtener sus items
        for order in orders_list:
            items = await conn.fetch(
                """
                SELECT 
                    oi.id,
                    oi.quantity,
                    oi.price,
                    p.id as product_id,
                    p.name as product_name,
                    p.description as product_description,
                    p.category as product_category
                FROM order_items oi
                JOIN products p ON oi."productId" = p.id
                WHERE oi."orderId" = $1
                ORDER BY oi."createdAt"
                """,
                order['id']
            )
            order['items'] = [convert_uuid_to_str(dict(item)) for item in items]
        
        return orders_list
    finally:
        await conn.close()

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por email"""
    conn = await get_connection()
    try:
        user = await conn.fetchrow(
            'SELECT id, email, password, name, phone, role FROM users WHERE email = $1',
            email
        )
        return convert_uuid_to_str(dict(user)) if user else None
    finally:
        await conn.close()

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por ID"""
    conn = await get_connection()
    try:
        user = await conn.fetchrow(
            'SELECT id, email, name, phone, role FROM users WHERE id = $1',
            user_id
        )
        return convert_uuid_to_str(dict(user)) if user else None
    finally:
        await conn.close()

async def create_user(email: str, hashed_password: str, name: str, phone: Optional[str] = None) -> Dict[str, Any]:
    """Crear nuevo usuario"""
    conn = await get_connection()
    try:
        user_id = await conn.fetchval(
            """
            INSERT INTO users (id, email, password, name, phone, role, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, NOW(), NOW())
            RETURNING id
            """,
            email, hashed_password, name, phone, "CUSTOMER"
        )
        
        user = await conn.fetchrow(
            'SELECT id, email, name, phone, role FROM users WHERE id = $1',
            user_id
        )
        return convert_uuid_to_str(dict(user)) if user else None
    finally:
        await conn.close()

async def get_all_orders() -> List[Dict[str, Any]]:
    """Obtener todos los pedidos con información completa del cliente, dirección y productos (admin)"""
    conn = await get_connection()
    try:
        # Obtener órdenes con información del cliente y dirección
        orders = await conn.fetch(
            """
            SELECT 
                o.id, 
                o.status, 
                o.total, 
                o."paymentMethod", 
                o.notes,
                o."createdAt", 
                o."updatedAt",
                -- Datos del cliente
                u.id as customer_id,
                u.name as customer_name, 
                u.email as customer_email,
                u.phone as customer_phone,
                -- Datos de dirección de entrega
                a.street as delivery_street,
                a.city as delivery_city,
                a.state as delivery_state,
                a."zipCode" as delivery_zipcode,
                a.country as delivery_country,
                a.instructions as delivery_instructions
            FROM orders o
            JOIN users u ON o."userId" = u.id
            JOIN addresses a ON o."addressId" = a.id
            ORDER BY o."createdAt" DESC
            """
        )
        
        # Convertir a lista de diccionarios y agregar items
        orders_list = [convert_uuid_to_str(dict(row)) for row in orders]
        
        # Para cada orden, obtener sus items con información del producto
        for order in orders_list:
            items = await conn.fetch(
                """
                SELECT 
                    oi.id,
                    oi.quantity,
                    oi.price,
                    p.id as product_id,
                    p.name as product_name,
                    p.description as product_description,
                    p.category as product_category
                FROM order_items oi
                JOIN products p ON oi."productId" = p.id
                WHERE oi."orderId" = $1
                ORDER BY oi."createdAt"
                """,
                order['id']
            )
            order['items'] = [convert_uuid_to_str(dict(item)) for item in items]
        
        return orders_list
    finally:
        await conn.close()

async def update_order_status(order_id: str, status: str) -> Optional[Dict[str, Any]]:
    """Actualizar estado de un pedido"""
    conn = await get_connection()
    try:
        order = await conn.fetchrow(
            """
            UPDATE orders SET status = $1, "updatedAt" = NOW()
            WHERE id = $2
            RETURNING id, status, total, "paymentMethod", "createdAt", "updatedAt"
            """,
            status, order_id
        )
        return convert_uuid_to_str(dict(order)) if order else None
    finally:
        await conn.close()

async def create_address(user_id: str, street: str, city: str, state: str, zip_code: str, country: str = "Colombia", is_default: bool = False, instructions: Optional[str] = None) -> Dict[str, Any]:
    """Crear nueva dirección"""
    conn = await get_connection()
    try:
        # Primero, si is_default es True, desmarcar cualquier otra dirección como predeterminada
        if is_default:
            await conn.execute(
                'UPDATE addresses SET "isDefault" = false WHERE "userId" = $1',
                user_id
            )
            
        # Insertar la nueva dirección
        address_id = await conn.fetchval(
            """
            INSERT INTO addresses (id, "userId", street, city, state, "zipCode", country, "isDefault", instructions, "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
            RETURNING id
            """,
            user_id, street, city, state, zip_code, country, is_default, instructions
        )
        
        # Obtener la dirección recién creada
        address = await conn.fetchrow(
            'SELECT id, "userId", street, city, state, "zipCode", country, "isDefault", instructions FROM addresses WHERE id = $1',
            address_id
        )
        return convert_uuid_to_str(dict(address)) if address else None
    finally:
        await conn.close()

async def get_user_addresses(user_id: str) -> List[Dict[str, Any]]:
    """Obtener direcciones de un usuario"""
    conn = await get_connection()
    try:
        addresses = await conn.fetch(
            """
            SELECT id, "userId", street, city, state, "zipCode", country, "isDefault", instructions, "createdAt", "updatedAt"
            FROM addresses WHERE "userId" = $1
            ORDER BY "isDefault" DESC, "createdAt" DESC
            """,
            user_id
        )
        return [convert_uuid_to_str(dict(row)) for row in addresses]
    finally:
        await conn.close()

async def get_address_by_id(address_id: str) -> Optional[Dict[str, Any]]:
    """Obtener dirección por ID"""
    conn = await get_connection()
    try:
        address = await conn.fetchrow(
            'SELECT id, "userId", street, city, state, "zipCode", country, "isDefault", instructions FROM addresses WHERE id = $1',
            address_id
        )
        return convert_uuid_to_str(dict(address)) if address else None
    finally:
        await conn.close()

async def create_product(name: str, description: Optional[str], price: float, category: str, image: Optional[str] = None, is_available: bool = True) -> Dict[str, Any]:
    """Crear nuevo producto"""
    conn = await get_connection()
    try:
        product_id = await conn.fetchval(
            """
            INSERT INTO products (id, name, description, price, image, category, "isAvailable", "createdAt", "updatedAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6, NOW(), NOW())
            RETURNING id
            """,
            name, description, price, image, category, is_available
        )
        
        product = await conn.fetchrow(
            'SELECT id, name, description, price, image, category, "isAvailable", "createdAt", "updatedAt" FROM products WHERE id = $1',
            product_id
        )
        return convert_uuid_to_str(dict(product)) if product else None
    finally:
        await conn.close()

async def update_product(product_id: str, name: Optional[str] = None, description: Optional[str] = None, price: Optional[float] = None, category: Optional[str] = None, image: Optional[str] = None, is_available: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    """Actualizar producto existente"""
    conn = await get_connection()
    try:
        # Obtener producto actual
        current_product = await conn.fetchrow(
            'SELECT name, description, price, category, image, "isAvailable" FROM products WHERE id = $1',
            product_id
        )
        
        if not current_product:
            return None
        
        # Usar valores actuales si no se proporcionan nuevos
        updated_name = name if name is not None else current_product['name']
        updated_description = description if description is not None else current_product['description']
        updated_price = price if price is not None else current_product['price']
        updated_category = category if category is not None else current_product['category']
        updated_image = image if image is not None else current_product['image']
        updated_available = is_available if is_available is not None else current_product['isAvailable']
        
        # Actualizar producto
        product = await conn.fetchrow(
            """
            UPDATE products 
            SET name = $1, description = $2, price = $3, category = $4, image = $5, "isAvailable" = $6, "updatedAt" = NOW()
            WHERE id = $7
            RETURNING id, name, description, price, image, category, "isAvailable", "createdAt", "updatedAt"
            """,
            updated_name, updated_description, updated_price, updated_category, updated_image, updated_available, product_id
        )
        
        return convert_uuid_to_str(dict(product)) if product else None
    finally:
        await conn.close()

async def get_all_customers_with_addresses() -> List[Dict[str, Any]]:
    """Obtener todos los clientes (CUSTOMER role) con sus direcciones (admin)"""
    conn = await get_connection()
    try:
        # Obtener todos los usuarios con rol CUSTOMER
        customers = await conn.fetch(
            """
            SELECT 
                u.id,
                u.email,
                u.name,
                u.phone,
                u.role,
                u."createdAt",
                u."updatedAt"
            FROM users u
            WHERE u.role = 'CUSTOMER'
            ORDER BY u."createdAt" DESC
            """
        )
        
        customers_list = [convert_uuid_to_str(dict(row)) for row in customers]
        
        # Para cada cliente, obtener sus direcciones
        for customer in customers_list:
            addresses = await conn.fetch(
                """
                SELECT 
                    id,
                    "userId",
                    street,
                    city,
                    state,
                    "zipCode",
                    country,
                    "isDefault",
                    instructions,
                    "createdAt",
                    "updatedAt"
                FROM addresses
                WHERE "userId" = $1
                ORDER BY "isDefault" DESC, "createdAt" DESC
                """,
                customer['id']
            )
            customer['addresses'] = [convert_uuid_to_str(dict(addr)) for addr in addresses]
        
        return customers_list
    finally:
        await conn.close()

