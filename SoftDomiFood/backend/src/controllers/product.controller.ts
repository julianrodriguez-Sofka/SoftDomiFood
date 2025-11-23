import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export const getProducts = async (req: Request, res: Response) => {
  try {
    const { category, available } = req.query;

    const where: any = {};
    
    if (category) {
      where.category = category;
    }
    
    if (available !== undefined) {
      where.isAvailable = available === 'true';
    }

    const products = await prisma.product.findMany({
      where,
      orderBy: { createdAt: 'desc' }
    });

    res.json({ products });
  } catch (error: any) {
    console.error('Get products error:', error);
    res.status(500).json({ message: 'Error fetching products', error: error.message });
  }
};

export const getProductById = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const product = await prisma.product.findUnique({
      where: { id }
    });

    if (!product) {
      return res.status(404).json({ message: 'Product not found' });
    }

    res.json({ product });
  } catch (error: any) {
    console.error('Get product error:', error);
    res.status(500).json({ message: 'Error fetching product', error: error.message });
  }
};

export const createProduct = async (req: Request, res: Response) => {
  try {
    const { name, description, price, image, category, isAvailable } = req.body;

    const product = await prisma.product.create({
      data: {
        name,
        description,
        price: parseFloat(price),
        image,
        category,
        isAvailable: isAvailable !== undefined ? isAvailable : true
      }
    });

    res.status(201).json({ message: 'Product created successfully', product });
  } catch (error: any) {
    console.error('Create product error:', error);
    res.status(500).json({ message: 'Error creating product', error: error.message });
  }
};

export const updateProduct = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { name, description, price, image, category, isAvailable } = req.body;

    const product = await prisma.product.update({
      where: { id },
      data: {
        ...(name && { name }),
        ...(description !== undefined && { description }),
        ...(price && { price: parseFloat(price) }),
        ...(image !== undefined && { image }),
        ...(category && { category }),
        ...(isAvailable !== undefined && { isAvailable })
      }
    });

    res.json({ message: 'Product updated successfully', product });
  } catch (error: any) {
    console.error('Update product error:', error);
    res.status(500).json({ message: 'Error updating product', error: error.message });
  }
};

export const deleteProduct = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    await prisma.product.delete({
      where: { id }
    });

    res.json({ message: 'Product deleted successfully' });
  } catch (error: any) {
    console.error('Delete product error:', error);
    res.status(500).json({ message: 'Error deleting product', error: error.message });
  }
};


