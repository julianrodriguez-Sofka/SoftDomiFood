import React, { useState } from 'react';
import { ShoppingCart, User, LogOut, ChevronDown } from 'lucide-react';

const ClientLayout = ({ children, user, cartCount, onLogin, onCartClick, onLogout, activeTab, setActiveTab }) => {
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50">
      {/* Header */}
      <header className="bg-white shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <img 
                src="/logo.svg" 
                alt="SoftDomiFood Logo" 
                className="w-10 h-10 flex-shrink-0"
              />
              <h1 className="text-2xl font-bold text-gray-800">SoftDomiFood</h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* Navigation Tabs */}
              {user && (
                <div className="flex space-x-2 border-b border-gray-200">
                  <button
                    onClick={() => setActiveTab('menu')}
                    className={`px-4 py-2 text-sm font-medium transition-colors ${
                      activeTab === 'menu'
                        ? 'text-orange-600 border-b-2 border-orange-600'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    Menú
                  </button>
                  <button
                    onClick={() => setActiveTab('orders')}
                    className={`px-4 py-2 text-sm font-medium transition-colors ${
                      activeTab === 'orders'
                        ? 'text-orange-600 border-b-2 border-orange-600'
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                  >
                    Mis Pedidos
                  </button>
                </div>
              )}

              {/* User Menu */}
              {user ? (
                <div className="relative">
                  <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="flex items-center space-x-2 bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors"
                  >
                    <User className="w-4 h-4" />
                    <span>{user.name}</span>
                    <ChevronDown className="w-4 h-4" />
                  </button>
                  {showUserMenu && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                      <button
                        onClick={() => {
                          setShowUserMenu(false);
                          onLogout();
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Cerrar Sesión</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <button
                  onClick={onLogin}
                  className="flex items-center space-x-2 bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors"
                >
                  <User className="w-4 h-4" />
                  <span>Iniciar Sesión</span>
                </button>
              )}

              <div className="relative">
                <button
                  onClick={onCartClick}
                  className="bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors relative"
                  aria-label="Abrir carrito"
                >
                  <ShoppingCart className="w-5 h-5" />
                  {cartCount > 0 && (
                    <span className="absolute -top-2 -right-2 bg-yellow-400 text-black text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                      {cartCount}
                    </span>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

export default ClientLayout;
