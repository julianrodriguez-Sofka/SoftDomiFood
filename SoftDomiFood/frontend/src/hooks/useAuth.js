import { useState } from 'react';

const useAuth = () => {
  const [user, setUser] = useState(null);

  const login = (email, password) => {
    // Simulación de login
    setUser({ name: 'Usuario Demo', email });
    return true;
  };

  const logout = () => {
    setUser(null);
  };

  const register = (name, email, password) => {
    // Simulación de registro
    setUser({ name, email });
    return true;
  };

  return { user, login, logout, register };
};

export default useAuth;
