import { Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { AuthRequest } from '../middleware/auth.middleware';

const prisma = new PrismaClient();

export const createOrder = async (req: AuthRequest, res: Response) => {
  try {
    const { addressId, items, notes } = req.body;
    const userId = req.userId!;

    // Validar que el address pertenece al usuario
    const address = await prisma.address.findFirst({
      where: { id: addressId, userId }
    });

    if (!address) {
      return res.status(404).json({ message: 'Address not found' });
    }

    // Calcular total y validar productos
    let total = 0;
    const orderItems = [];

    for (const item of items) {
      const product = await prisma.product.findUnique({
        where: { id: item.productId }
      });

      if (!product) {
        return res.status(404).json({ message: `Product ${item.productId} not found` });
      }

      if (!product.isAvailable) {
        return res.status(400).json({ message: `Product ${product.name} is not available` });
      }

      const itemTotal = product.price * item.quantity;
      total += itemTotal;

      orderItems.push({
        productId: product.id,
        quantity: item.quantity,
        price: product.price,
        notes: item.notes
      });
    }

    // Crear orden con items
    const order = await prisma.order.create({
      data: {
        userId,
        addressId,
        total,
        notes,
        items: {
          create: orderItems
        }
      },
      include: {
        items: {
          include: {
            product: true
          }
        },
        address: true
      }
    });

    res.status(201).json({ message: 'Order created successfully', order });
  } catch (error: any) {
    console.error('Create order error:', error);
    res.status(500).json({ message: 'Error creating order', error: error.message });
  }
};

export const getOrders = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const isAdmin = req.userRole === 'ADMIN';

    const where = isAdmin ? {} : { userId };

    const orders = await prisma.order.findMany({
      where,
      include: {
        items: {
          include: {
            product: true
          }
        },
        address: true,
        user: {
          select: {
            id: true,
            name: true,
            email: true,
            phone: true
          }
        }
      },
      orderBy: { createdAt: 'desc' }
    });

    res.json({ orders });
  } catch (error: any) {
    console.error('Get orders error:', error);
    res.status(500).json({ message: 'Error fetching orders', error: error.message });
  }
};

export const getOrderById = async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;
    const userId = req.userId!;
    const isAdmin = req.userRole === 'ADMIN';

    const where: any = { id };
    if (!isAdmin) {
      where.userId = userId;
    }

    const order = await prisma.order.findFirst({
      where,
      include: {
        items: {
          include: {
            product: true
          }
        },
        address: true,
        user: {
          select: {
            id: true,
            name: true,
            email: true,
            phone: true
          }
        }
      }
    });

    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }

    res.json({ order });
  } catch (error: any) {
    console.error('Get order error:', error);
    res.status(500).json({ message: 'Error fetching order', error: error.message });
  }
};

export const updateOrderStatus = async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    const validStatuses = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'ON_DELIVERY', 'DELIVERED', 'CANCELLED'];
    
    if (!validStatuses.includes(status)) {
      return res.status(400).json({ message: 'Invalid status' });
    }

    const order = await prisma.order.update({
      where: { id },
      data: { status },
      include: {
        items: {
          include: {
            product: true
          }
        },
        address: true
      }
    });

    res.json({ message: 'Order status updated successfully', order });
  } catch (error: any) {
    console.error('Update order status error:', error);
    res.status(500).json({ message: 'Error updating order status', error: error.message });
  }
};


