import React from 'react';
import { MapPin, Clock, Package, CheckCircle, X, User, CreditCard, DollarSign } from 'lucide-react';

const OrderManagement = ({ orders, onStatusChange }) => {
  const getStatusColor = (status) => {
    const statusLower = status.toLowerCase();
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
    const statusLower = status.toLowerCase();
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

  const getPaymentIcon = (method) => {
    switch (method) {
      case 'CARD': return <CreditCard className="w-4 h-4" />;
      case 'CASH': return <DollarSign className="w-4 h-4" />;
      default: return <DollarSign className="w-4 h-4" />;
    }
  };

  const getPaymentColor = (method) => {
    switch (method) {
      case 'CARD': return 'bg-blue-100 text-blue-800';
      case 'CASH': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Pedidos Recientes</h2>
        <div className="flex space-x-2">
          <select className="p-2 border border-gray-300 rounded-lg text-sm">
            <option>Todos los estados</option>
            <option>Pendiente</option>
            <option>Preparando</option>
            <option>Completado</option>
            <option>Cancelado</option>
          </select>
        </div>
      </div>

      {orders.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No hay pedidos registrados</p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map(order => {
            const orderDate = order.createdAt ? new Date(order.createdAt).toLocaleDateString('es-ES') : 'N/A';
            const customerName = order.customer_name || 'Cliente';
            const customerPhone = order.customer_phone || 'N/A';
            const customerEmail = order.customer_email || 'N/A';
            const address = order.delivery_street 
              ? `${order.delivery_street}, ${order.delivery_city}, ${order.delivery_state}`
              : 'Dirección no disponible';
            const items = order.items || [];
            const status = (order.status || 'PENDING').toLowerCase();

            return (
              <div key={order.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-800">Pedido #{order.id.substring(0, 8)}</h3>
                    <div className="flex items-center space-x-4 mt-1 flex-wrap">
                      <div className="flex items-center space-x-1">
                        <User className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-600">{customerName}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-sm text-gray-600">Tel: {customerPhone}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-sm text-gray-600">Email: {customerEmail}</span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600">Fecha: {orderDate}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPaymentColor(order.paymentMethod || 'CASH')}`}>
                      {getPaymentIcon(order.paymentMethod || 'CASH')}
                      <span className="ml-1">{(order.paymentMethod || 'CASH') === 'CARD' ? 'Tarjeta' : 'Efectivo'}</span>
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                      {getStatusIcon(status)}
                      <span className="ml-1 capitalize">{status}</span>
                    </span>
                  </div>
                </div>

                <div className="mb-3">
                  <p className="text-sm text-gray-600 mb-2">Productos:</p>
                  <div className="text-sm text-gray-700 space-y-1">
                    {items.length > 0 ? (
                      items.map((item, index) => (
                        <div key={index} className="flex justify-between pl-4">
                          <span>{item.quantity}x {item.product_name || 'Producto'}</span>
                          <span>${((item.price || 0) * (item.quantity || 0)).toFixed(2)}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 pl-4">No hay productos en este pedido</p>
                    )}
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <p className="font-semibold text-gray-800">Total: ${(parseFloat(order.total) || 0).toFixed(2)}</p>
                  <p className="text-sm text-gray-600">
                    <MapPin className="inline w-4 h-4 mr-1" />
                    {address}
                  </p>
                </div>

                <div className="flex space-x-2 mt-4">
                  {status !== 'delivered' && status !== 'cancelled' && (
                    <>
                      {status === 'pending' && (
                        <button
                          onClick={() => onStatusChange(order.id, 'PREPARING')}
                          className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                        >
                          Preparar
                        </button>
                      )}
                      {status === 'preparing' && (
                        <button
                          onClick={() => onStatusChange(order.id, 'READY')}
                          className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition-colors"
                        >
                          Listo
                        </button>
                      )}
                      {status === 'ready' && (
                        <button
                          onClick={() => onStatusChange(order.id, 'DELIVERED')}
                          className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                        >
                          Entregado
                        </button>
                      )}
                      <button
                        onClick={() => onStatusChange(order.id, 'CANCELLED')}
                        className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                      >
                        Cancelar
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default OrderManagement;
