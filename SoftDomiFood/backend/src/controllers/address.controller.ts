import { Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { AuthRequest } from '../middleware/auth.middleware';

const prisma = new PrismaClient();

export const createAddress = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;
    const { street, city, state, zipCode, country, isDefault, instructions } = req.body;

    // Si es la dirección por defecto, quitar el default de las demás
    if (isDefault) {
      await prisma.address.updateMany({
        where: { userId, isDefault: true },
        data: { isDefault: false }
      });
    }

    const address = await prisma.address.create({
      data: {
        userId,
        street,
        city,
        state,
        zipCode,
        country: country || 'Colombia',
        isDefault: isDefault || false,
        instructions
      }
    });

    res.status(201).json({ message: 'Address created successfully', address });
  } catch (error: any) {
    console.error('Create address error:', error);
    res.status(500).json({ message: 'Error creating address', error: error.message });
  }
};

export const getAddresses = async (req: AuthRequest, res: Response) => {
  try {
    const userId = req.userId!;

    const addresses = await prisma.address.findMany({
      where: { userId },
      orderBy: [
        { isDefault: 'desc' },
        { createdAt: 'desc' }
      ]
    });

    res.json({ addresses });
  } catch (error: any) {
    console.error('Get addresses error:', error);
    res.status(500).json({ message: 'Error fetching addresses', error: error.message });
  }
};

export const updateAddress = async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;
    const userId = req.userId!;
    const { street, city, state, zipCode, country, isDefault, instructions } = req.body;

    // Verificar que la dirección pertenece al usuario
    const existingAddress = await prisma.address.findFirst({
      where: { id, userId }
    });

    if (!existingAddress) {
      return res.status(404).json({ message: 'Address not found' });
    }

    // Si se está marcando como default, quitar el default de las demás
    if (isDefault) {
      await prisma.address.updateMany({
        where: { userId, isDefault: true, id: { not: id } },
        data: { isDefault: false }
      });
    }

    const address = await prisma.address.update({
      where: { id },
      data: {
        ...(street && { street }),
        ...(city && { city }),
        ...(state && { state }),
        ...(zipCode && { zipCode }),
        ...(country && { country }),
        ...(isDefault !== undefined && { isDefault }),
        ...(instructions !== undefined && { instructions })
      }
    });

    res.json({ message: 'Address updated successfully', address });
  } catch (error: any) {
    console.error('Update address error:', error);
    res.status(500).json({ message: 'Error updating address', error: error.message });
  }
};

export const deleteAddress = async (req: AuthRequest, res: Response) => {
  try {
    const { id } = req.params;
    const userId = req.userId!;

    // Verificar que la dirección pertenece al usuario
    const address = await prisma.address.findFirst({
      where: { id, userId }
    });

    if (!address) {
      return res.status(404).json({ message: 'Address not found' });
    }

    await prisma.address.delete({
      where: { id }
    });

    res.json({ message: 'Address deleted successfully' });
  } catch (error: any) {
    console.error('Delete address error:', error);
    res.status(500).json({ message: 'Error deleting address', error: error.message });
  }
};


