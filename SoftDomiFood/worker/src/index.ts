import amqp from 'amqplib';
import { PrismaClient } from '@prisma/client';
import dotenv from 'dotenv';

dotenv.config();

const prisma = new PrismaClient();
// Usar el nombre del servicio de Docker Compose para la conexión
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://admin:admin123@rabbitmq:5672/';
const QUEUE_NAME = 'order_queue';

interface OrderMessage {
  orderId: string;
  userId: string;
  addressId: string;
  items: Array<{
    productId: string;
    quantity: number;
    price: number;
  }>;
  total: number;
  notes?: string;
}

async function processOrder(message: OrderMessage) {
  console.log(`📦 Procesando pedido: ${message.orderId}`);
  
  try {
    // Simular tiempo de procesamiento/preparación (5 segundos)
    console.log(`⏳ Preparando pedido ${message.orderId}...`);
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Actualizar estado del pedido a PREPARING
    await prisma.order.update({
      where: { id: message.orderId },
      data: { status: 'PREPARING' }
    });
    
    console.log(`✅ Pedido ${message.orderId} actualizado a PREPARING`);
  } catch (error: any) {
    console.error(`❌ Error procesando pedido ${message.orderId}:`, error);
    throw error;
  }
}

let connection: amqp.Connection | null = null;
let channel: amqp.Channel | null = null;
let isProcessing = false;

async function startConsumer() {
  try {
    console.log('🔌 Conectando a RabbitMQ...');
    // Ocultar contraseña en logs
    const safeUrl = RABBITMQ_URL.replace(/:[^:@]+@/, ':****@');
    console.log(`📍 URL de conexión: ${safeUrl}`);
    
    connection = await amqp.connect(RABBITMQ_URL);
    channel = await connection.createChannel();
    
    // Manejar errores de conexión
    connection.on('error', (err) => {
      console.error('❌ Error de conexión RabbitMQ:', err);
      connection = null;
      channel = null;
      if (!isProcessing) {
        console.log('🔄 Reintentando conexión en 5 segundos...');
        setTimeout(startConsumer, 5000);
      }
    });
    
    connection.on('close', () => {
      console.warn('⚠️  Conexión RabbitMQ cerrada');
      connection = null;
      channel = null;
      if (!isProcessing) {
        console.log('🔄 Reintentando conexión en 5 segundos...');
        setTimeout(startConsumer, 5000);
      }
    });
    
    // Asegurar que la cola existe
    await channel.assertQueue(QUEUE_NAME, { durable: true });
    console.log(`✅ Conectado a RabbitMQ. Esperando mensajes en cola: ${QUEUE_NAME}`);
    
    // Configurar prefetch (procesar un mensaje a la vez)
    channel.prefetch(1);
    
    // Consumir mensajes
    channel.consume(QUEUE_NAME, async (msg) => {
      if (!msg || !channel) return;
      
      isProcessing = true;
      try {
        const orderData: OrderMessage = JSON.parse(msg.content.toString());
        console.log(`📨 Mensaje recibido: Pedido ${orderData.orderId}`);
        
        // Procesar pedido
        await processOrder(orderData);
        
        // Confirmar procesamiento
        channel.ack(msg);
        console.log(`✅ Mensaje procesado y confirmado: ${orderData.orderId}`);
      } catch (error: any) {
        console.error('❌ Error procesando mensaje:', error);
        // Rechazar mensaje y no reencolar (para evitar loops infinitos)
        try {
          channel.nack(msg, false, false);
        } catch (nackError) {
          console.error('❌ Error al rechazar mensaje:', nackError);
        }
      } finally {
        isProcessing = false;
      }
    }, {
      noAck: false // Requerir confirmación manual
    });
    
    console.log('👂 Worker escuchando mensajes...');
    
    // Manejar cierre graceful
    process.on('SIGINT', async () => {
      console.log('🛑 Cerrando conexión...');
      isProcessing = true;
      if (channel) {
        try {
          await channel.close();
        } catch (e) {
          console.error('Error cerrando canal:', e);
        }
      }
      if (connection) {
        try {
          await connection.close();
        } catch (e) {
          console.error('Error cerrando conexión:', e);
        }
      }
      await prisma.$disconnect();
      process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
      console.log('🛑 Recibida señal SIGTERM, cerrando...');
      isProcessing = true;
      if (channel) {
        try {
          await channel.close();
        } catch (e) {
          console.error('Error cerrando canal:', e);
        }
      }
      if (connection) {
        try {
          await connection.close();
        } catch (e) {
          console.error('Error cerrando conexión:', e);
        }
      }
      await prisma.$disconnect();
      process.exit(0);
    });
    
  } catch (error: any) {
    console.error('❌ Error en consumer:', error);
    const safeUrl = RABBITMQ_URL.replace(/:[^:@]+@/, ':****@');
    console.error(`📍 URL intentada: ${safeUrl}`);
    if (error.code === 'ECONNREFUSED') {
      console.error('💡 Verifica que RabbitMQ esté corriendo y accesible en la red Docker');
      console.error('💡 Asegúrate de usar el nombre del servicio "rabbitmq" en lugar de una IP');
    }
    // Reintentar después de 5 segundos
    if (!isProcessing) {
      console.log('🔄 Reintentando conexión en 5 segundos...');
      setTimeout(startConsumer, 5000);
    }
  }
}

// Iniciar consumer
startConsumer();

