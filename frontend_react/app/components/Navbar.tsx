'use client';

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import LoginModal from './LoginModal';

export default function Navbar() {
  const { isLoggedIn, logout } = useAuth();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <span className="text-xl font-semibold">TailorMade</span>
          </div>
          
          <div className="flex items-center">
            {isLoggedIn ? (
              <button
                onClick={logout}
                className="ml-4 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            ) : (
              <button
                onClick={() => setIsLoginModalOpen(true)}
                className="ml-4 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Login
              </button>
            )}
          </div>
        </div>
      </div>
      
      <LoginModal 
        isOpen={isLoginModalOpen} 
        onClose={() => setIsLoginModalOpen(false)} 
      />
    </nav>
  );
} 