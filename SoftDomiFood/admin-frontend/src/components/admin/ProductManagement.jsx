import React, { useState } from 'react';
import { Edit, Plus, Trash2, X } from 'lucide-react';

const ProductManagement = ({ products, onAddProduct, onEditProduct, onDeleteProduct }) => {
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category: 'SALCHIPAPAS',
    image: '',
    isAvailable: true,
    stock: 0
  });

  const categories = ['SALCHIPAPAS', 'BEBIDAS', 'ADICIONALES', 'COMBOS'];

  const handleOpenAdd = () => {
    setEditingProduct(null);
    setFormData({
      name: '',
      description: '',
      price: '',
      category: 'SALCHIPAPAS',
      image: '',
      isAvailable: true,
      stock: 0
    });
    setShowModal(true);
  };

  const handleOpenEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name || '',
      description: product.description || '',
      price: product.price || '',
      category: product.category || 'SALCHIPAPAS',
      image: product.image || '',
      isAvailable: product.isAvailable !== false,
      stock: product.stock !== undefined ? product.stock : 0
    });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingProduct(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const productData = {
      name: formData.name,
      description: formData.description || null,
      price: parseFloat(formData.price),
      category: formData.category,
      image: formData.image || null,
      isAvailable: formData.isAvailable,
      stock: parseInt(formData.stock) || 0
    };

    let success = false;
    if (editingProduct) {
      success = await onEditProduct(editingProduct.id, productData);
    } else {
      success = await onAddProduct(productData);
    }

    if (success) {
      handleCloseModal();
    }
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'SALCHIPAPAS': 'Salchipapas',
      'BEBIDAS': 'Bebidas',
      'ADICIONALES': 'Adicionales',
      'COMBOS': 'Combos'
    };
    return labels[category] || category;
  };

  return (
    <>
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Gestión de Productos</h2>
          <button
            onClick={handleOpenAdd}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Agregar Producto</span>
          </button>
        </div>

        {products.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No hay productos registrados</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {products.map(product => {
              const stock = product.stock !== undefined ? product.stock : 0;
              const isLowStock = stock > 0 && stock < 10;
              const isOutOfStock = stock === 0;
              
              return (
                <div 
                  key={product.id} 
                  className={`border rounded-lg p-4 ${
                    isOutOfStock 
                      ? 'border-red-300 bg-red-50' 
                      : isLowStock 
                        ? 'border-orange-300 bg-orange-50' 
                        : 'border-gray-200'
                  }`}
                >
                  <img
                    src={product.image || 'https://placehold.co/300x200/FF6B6B/FFFFFF?text=Producto'}
                    alt={product.name}
                    className="w-full h-32 object-cover rounded-lg mb-3"
                  />
                  <h3 className="font-semibold text-gray-800 mb-1">{product.name}</h3>
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2">{product.description || 'Sin descripción'}</p>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-lg font-bold text-blue-600">${parseFloat(product.price || 0).toFixed(2)}</span>
                    <span className="text-xs text-gray-500">{getCategoryLabel(product.category)}</span>
                  </div>
                  <div className="mb-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-gray-700">Stock:</span>
                      <span className={`text-sm font-bold ${
                        isOutOfStock 
                          ? 'text-red-600' 
                          : isLowStock 
                            ? 'text-orange-600' 
                            : 'text-green-600'
                      }`}>
                        {stock} unidades
                      </span>
                    </div>
                    {isLowStock && (
                      <span className="text-xs text-orange-600 font-medium">⚠️ Stock bajo</span>
                    )}
                    {isOutOfStock && (
                      <span className="text-xs text-red-600 font-medium">❌ Sin stock</span>
                    )}
                  </div>
                  <div className="flex justify-between items-center">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      product.isAvailable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {product.isAvailable ? 'Disponible' : 'No Disponible'}
                    </span>
                    <div className="flex space-x-1">
                      <button
                        onClick={() => handleOpenEdit(product)}
                        className="p-1 text-blue-500 hover:text-blue-700"
                        title="Editar"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onDeleteProduct(product.id)}
                        className="p-1 text-red-500 hover:text-red-700"
                        title="Eliminar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Modal para agregar/editar producto */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold text-gray-800">
                {editingProduct ? 'Editar Producto' : 'Agregar Producto'}
              </h3>
              <button
                onClick={handleCloseModal}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  rows="3"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Precio *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.price}
                  onChange={(e) => setFormData({...formData, price: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Categoría *
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  required
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{getCategoryLabel(cat)}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL de Imagen
                </label>
                <input
                  type="url"
                  value={formData.image}
                  onChange={(e) => setFormData({...formData, image: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  placeholder="https://..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Stock (Cantidad disponible) *
                </label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={formData.stock}
                  onChange={(e) => setFormData({...formData, stock: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Si el stock es 0, el producto no se mostrará a los clientes
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isAvailable"
                  checked={formData.isAvailable}
                  onChange={(e) => setFormData({...formData, isAvailable: e.target.checked})}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="isAvailable" className="ml-2 text-sm text-gray-700">
                  Producto disponible
                </label>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  {editingProduct ? 'Actualizar' : 'Crear'}
                </button>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default ProductManagement;
