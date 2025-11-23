import React, { useState, useEffect } from 'react';
import { Clock, Package, CheckCircle, X, MapPin, DollarSign, CreditCard } from 'lucide-react';
import { ordersAPI } from '../../utils/api';

const MyOrders = ({ user, toast }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadOrders();
      // Recargar órdenes cada 10 segundos para ver actualizaciones
      const interval = setInterval(loadOrders, 10000);
      return () => clearInterval(interval);
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadOrders = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const data = await ordersAPI.getAll();
      const ordersList = data.orders || data || [];
      setOrders(ordersList);
    } catch (error) {
      console.error('Error loading orders:', error);
      toast.error('Error al cargar tus pedidos');
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const statusLower = status?.toLowerCase();
    switch (statusLower) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'preparing': return 'bg-blue-100 text-blue-800';
      case 'ready': return 'bg-green-100 text-green-800';
      case 'on_delivery': return 'bg-purple-100 text-purple-800';
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    const statusLower = status?.toLowerCase();
    switch (statusLower) {
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'confirmed': return <Clock className="w-4 h-4" />;
      case 'preparing': return <Package className="w-4 h-4" />;
      case 'ready': return <CheckCircle className="w-4 h-4" />;
      case 'on_delivery': return <Package className="w-4 h-4" />;
      case 'delivered': return <CheckCircle className="w-4 h-4" />;
      case 'cancelled': return <X className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getStatusText = (status) => {
    const statusLower = status?.toLowerCase();
    const statusMap = {
      'pending': 'Pendiente',
      'confirmed': 'Confirmado',
      'preparing': 'En Preparación',
      'ready': 'Listo',
      'on_delivery': 'En Camino',
      'delivered': 'Entregado',
      'cancelled': 'Cancelado'
    };
    return statusMap[statusLower] || status;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando tus pedidos...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Mis Pedidos</h2>
        <button
          onClick={loadOrders}
          className="text-sm text-orange-600 hover:text-orange-700 font-medium"
        >
          Actualizar
        </button>
      </div>

      {orders.length === 0 ? (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No tienes pedidos aún</p>
          <p className="text-gray-400 text-sm mt-2">Realiza tu primer pedido desde el menú</p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => {
            const status = (order.status || 'PENDING').toLowerCase();
            const items = order.items || [];
            
            return (
              <div
                key={order.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-800">
                      Pedido #{order.id.substring(0, 8)}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      Fecha: {formatDate(order.createdAt)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                      {getStatusIcon(status)}
                      <span className="ml-1">{getStatusText(status)}</span>
                    </span>
                    {order.paymentMethod && (
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        order.paymentMethod === 'CARD' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {order.paymentMethod === 'CARD' ? (
                          <CreditCard className="w-3 h-3 mr-1" />
                        ) : (
                          <DollarSign className="w-3 h-3 mr-1" />
                        )}
                        {order.paymentMethod === 'CARD' ? 'Tarjeta' : 'Efectivo'}
                      </span>
                    )}
                  </div>
                </div>

                <div className="mb-3">
                  <p className="text-sm font-medium text-gray-700 mb-2">Productos:</p>
                  <div className="text-sm text-gray-600 space-y-1">
                    {items.length > 0 ? (
                      items.map((item, index) => (
                        <div key={index} className="flex justify-between pl-4">
                          <span>
                            {item.quantity}x {item.product_name || item.productName || 'Producto'}
                          </span>
                          <span className="font-medium">
                            ${((item.price || 0) * (item.quantity || 0)).toFixed(2)}
                          </span>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 pl-4">No hay productos en este pedido</p>
                    )}
                  </div>
                </div>

                <div className="flex justify-between items-center pt-3 border-t border-gray-200">
                  <div className="flex items-center text-sm text-gray-600">
                    <MapPin className="w-4 h-4 mr-1" />
                    <span>Dirección de entrega registrada</span>
                  </div>
                  <p className="font-bold text-lg text-gray-800">
                    Total: ${(parseFloat(order.total) || 0).toFixed(2)}
                  </p>
                </div>

                {order.notes && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Notas:</span> {order.notes}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MyOrders;

