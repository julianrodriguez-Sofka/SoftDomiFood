import { Router } from 'express';
import { processPayment } from '../controllers/payment.controller';
import { authenticate } from '../middleware/auth.middleware';

const router = Router();

// Todas las rutas requieren autenticación
router.use(authenticate);

// Procesar pago
router.post('/', processPayment);

export default router;

