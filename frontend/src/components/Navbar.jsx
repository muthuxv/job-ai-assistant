import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Briefcase, Home, Upload } from 'lucide-react';
import { Settings } from 'lucide-react';

const Navbar = ({ hasCV }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/new', icon: Briefcase, label: 'Nouvelle candidature' },
    { path: '/upload-cv', icon: Upload, label: 'Mon CV', highlight: !hasCV },
    { path: '/settings', icon: Settings, label: 'Paramètres' },
  ];

  return (
    <nav className="navbar-glass rounded-2xl mb-8 sticky top-4 z-50">
      <div className="flex items-center justify-between px-6 py-4">
        
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div 
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #a855f7, #06b6d4)' }}
          >
            <Briefcase className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold neon-gradient-text">Job AI Assistant</h1>
            <p className="text-xs" style={{ color: 'rgba(148,163,184,0.7)' }}>
              Votre coach IA pour décrocher le job
            </p>
          </div>
        </Link>

        {/* Nav Items */}
        <div className="flex items-center gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className="relative flex items-center gap-2 px-4 py-2 rounded-xl transition-all duration-300"
                style={{
                  background: isActive ? 'rgba(168, 85, 247, 0.2)' : 'transparent',
                  border: isActive ? '1px solid rgba(168, 85, 247, 0.4)' : '1px solid transparent',
                  color: isActive ? '#a855f7' : 'rgba(148, 163, 184, 0.8)',
                  boxShadow: isActive ? '0 0 15px rgba(168, 85, 247, 0.2)' : 'none',
                }}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium">{item.label}</span>
                {item.highlight && (
                  <span 
                    className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full animate-pulse"
                    style={{ background: '#ec4899', boxShadow: '0 0 8px #ec4899' }}
                  />
                )}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;