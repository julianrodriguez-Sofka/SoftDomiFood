import React, { useState, useEffect } from 'react';
import AdminPage from './pages/AdminPage';
import AdminLogin from './pages/AdminLogin';
import ToastContainer from './components/common/ToastContainer';
import useToast from './hooks/useToast';

function App() {
  const [adminUser, setAdminUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const toast = useToast();

  useEffect(() => {
    // Verificar si hay un admin autenticado al cargar
    // SOLO verificar adminToken, nunca clientToken
    const adminToken = localStorage.getItem('adminToken');
    const savedAdmin = localStorage.getItem('adminUser');
    
    // Verificar que NO haya un parámetro que fuerce el login
    const urlParams = new URLSearchParams(window.location.search);
    const forceLogin = urlParams.get('forceLogin') === 'true';
    
    if (forceLogin) {
      // Si se fuerza el login, limpiar tokens y mostrar login
      localStorage.removeItem('adminToken');
      localStorage.removeItem('adminUser');
      setIsAuthenticated(false);
      // Limpiar el parámetro de la URL
      window.history.replaceState({}, document.title, window.location.pathname);
      return;
    }
    
    if (adminToken && savedAdmin) {
      try {
        const user = JSON.parse(savedAdmin);
        if (user.role === 'ADMIN') {
          setAdminUser(user);
          setIsAuthenticated(true);
        } else {
          // Si no es admin, limpiar
          localStorage.removeItem('adminUser');
          localStorage.removeItem('adminToken');
          setIsAuthenticated(false);
        }
      } catch (e) {
        localStorage.removeItem('adminUser');
        localStorage.removeItem('adminToken');
        setIsAuthenticated(false);
      }
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  const handleAdminLoginSuccess = (user) => {
    setAdminUser(user);
    setIsAuthenticated(true);
  };

  const handleAdminLogout = () => {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminUser');
    setAdminUser(null);
    setIsAuthenticated(false);
  };

  const handleSwitchToClient = () => {
    // Limpiar cualquier token de cliente antes de redirigir
    // Esto asegura que el admin vea la web del cliente sin sesión de cliente
    localStorage.removeItem('clientToken');
    localStorage.removeItem('clientUser');
    localStorage.removeItem('token'); // Token genérico también
    
    // Redirigir a la URL del cliente con parámetro para forzar sin sesión
    // Esto asegura que el frontend del cliente no intente restaurar ninguna sesión
    window.location.href = 'http://localhost:3000?noSession=true';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <ToastContainer toasts={toast.toasts} removeToast={toast.removeToast} />
      {!isAuthenticated ? (
        <AdminLogin onLoginSuccess={handleAdminLoginSuccess} toast={toast} />
      ) : (
        <AdminPage 
          switchToClient={handleSwitchToClient}
          adminUser={adminUser}
          onLogout={handleAdminLogout}
          toast={toast}
        />
      )}
    </div>
  );
}

export default App;

