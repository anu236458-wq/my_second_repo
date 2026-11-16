import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

const DEFAULT_USER = {
  id: 1,
  name: 'Admin',
  email: 'admin@apex.com',
  phone: '+919876543210',
  role: 'ADMIN'
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(DEFAULT_USER);
  const [assignedBatches, setAssignedBatches] = useState([]);
  const [loading] = useState(false);

  const login = async () => DEFAULT_USER;
  const logout = () => {};

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAdmin: true,
        isTeacher: false,
        assignedBatches
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
