import React from 'react';
import { X, Trash2 } from 'lucide-react';

const CartSidebar = ({ isOpen, onClose, cart, onUpdateQuantity, onRemoveFromCart, totalPrice }) => {
  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className={`fixed inset-0 bg-black z-50 transition-opacity duration-300 ${
            isOpen ? 'bg-opacity-50 opacity-100' : 'bg-opacity-0 opacity-0'
          }`}
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div
        className={`fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out overflow-y-auto ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Carrito de Compras</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              aria-label="Cerrar carrito"
            >
              <X className="w-6 h-6 text-gray-600" />
            </button>
          </div>

          {/* Cart Content */}
          {cart.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <svg
                  className="w-12 h-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                  />
                </svg>
              </div>
              <p className="text-gray-500 text-lg font-medium">Tu carrito está vacío</p>
              <p className="text-gray-400 text-sm mt-2">Agrega productos para comenzar</p>
            </div>
          ) : (
            <>
              {/* Cart Items */}
              <div className="space-y-4 mb-6 max-h-[calc(100vh-300px)] overflow-y-auto">
                {cart.map(item => (
                  <div
                    key={item.id}
                    className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-gray-800 mb-1">{item.name}</h4>
                      <p className="text-sm text-gray-600 mb-2">
                        ${item.price.toFixed(2)} c/u
                      </p>
                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
                          className="w-8 h-8 rounded-full bg-white border border-gray-300 flex items-center justify-center hover:bg-gray-200 transition-colors font-semibold"
                          aria-label="Disminuir cantidad"
                        >
                          -
                        </button>
                        <span className="w-8 text-center font-semibold text-gray-800">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                          className="w-8 h-8 rounded-full bg-white border border-gray-300 flex items-center justify-center hover:bg-gray-200 transition-colors font-semibold"
                          aria-label="Aumentar cantidad"
                        >
                          +
                        </button>
                        <span className="text-sm text-gray-600 ml-2">
                          = ${(item.price * item.quantity).toFixed(2)}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => onRemoveFromCart(item.id)}
                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-full transition-colors"
                      aria-label="Eliminar producto"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                ))}
              </div>

              {/* Total */}
              <div className="border-t-2 border-gray-200 pt-4 mb-4">
                <div className="flex justify-between items-center">
                  <span className="text-xl font-semibold text-gray-800">Total:</span>
                  <span className="text-3xl font-bold text-orange-600">
                    ${totalPrice.toFixed(2)}
                  </span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
};

export default CartSidebar;

