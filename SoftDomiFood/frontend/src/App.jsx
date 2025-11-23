import React from 'react';
import ClientPage from './pages/ClientPage';
import ToastContainer from './components/common/ToastContainer';
import useToast from './hooks/useToast';

function App() {
  const toast = useToast();

  return (
    <div className="min-h-screen bg-gray-50">
      <ToastContainer toasts={toast.toasts} removeToast={toast.removeToast} />
      <ClientPage 
        switchToAdmin={() => {
          // Redirigir a la URL del panel de administración con parámetro para forzar login
          // Esto asegura que siempre se muestre el login de admin, incluso si hay un token
          window.location.href = 'http://localhost:3001?forceLogin=true';
        }} 
        toast={toast}
        adminUser={null}
        isAdminView={false}
      />
    </div>
  );
}

export default App;
                         