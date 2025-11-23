import { Request, Response } from 'express';

/**
 * Simula el procesamiento de un pago
 * Retorna éxito después de 2 segundos
 */
export const processPayment = async (req: Request, res: Response) => {
  try {
    const { amount, orderId } = req.body;

    // Validaciones
    if (!amount || amount <= 0) {
      return res.status(400).json({ 
        message: 'El monto debe ser mayor a 0' 
      });
    }

    if (!orderId) {
      return res.status(400).json({ 
        message: 'El ID del pedido es requerido' 
      });
    }

    // Simular procesamiento de pago (esperar 2 segundos)
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Simular diferentes resultados (95% éxito, 5% fallo para testing)
    const success = Math.random() > 0.05;

    if (success) {
      // Generar ID de transacción simulado
      const transactionId = `TXN-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;

      res.json({
        success: true,
        message: 'Pago procesado exitosamente',
        transactionId,
        amount: parseFloat(amount),
        orderId,
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(402).json({
        success: false,
        message: 'El pago fue rechazado. Por favor, verifica tu método de pago e intenta nuevamente.',
        orderId
      });
    }
  } catch (error: any) {
    console.error('Payment processing error:', error);
    res.status(500).json({ 
      message: 'Error al procesar el pago', 
      error: error.message 
    });
  }
};

