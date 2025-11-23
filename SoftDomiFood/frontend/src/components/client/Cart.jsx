import React from 'react';
import { Trash2 } from 'lucide-react';

const Cart = ({ cart, onUpdateQuantity, onRemoveFromCart, totalPrice }) => {
  if (cart.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Carrito</h3>
        <p className="text-gray-500 text-center py-8">Tu carrito está vacío</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">Carrito</h3>

      <div className="space-y-3 mb-6 max-h-64 overflow-y-auto">
        {cart.map(item => (
          <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <h4 className="font-medium text-gray-800">{item.name}</h4>
              <p className="text-sm text-gray-600">${item.price} x {item.quantity}</p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
                className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300"
              >
                -
              </button>
              <span className="w-8 text-center">{item.quantity}</span>
              <button
                onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300"
              >
                +
              </button>
              <button
                onClick={() => onRemoveFromCart(item.id)}
                className="ml-2 text-red-500 hover:text-red-700"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t pt-4">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-gray-800">Total:</span>
          <span className="text-2xl font-bold text-orange-600">${totalPrice.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};

export default Cart;
