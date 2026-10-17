import React from 'react';
import { NavLink } from 'react-router-dom';
import { Shield, LayoutDashboard, Search, History } from 'lucide-react';

export default function Sidebar() {
  return (
    <div className="sidebar">
      <div className="logo" style={{ padding: '0 1rem', marginBottom: '2rem' }}>
        <Shield className="logo-icon" size={28} />
        PhishGuard
      </div>
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <NavLink to="/" className={({isActive}) => `sidebar-link ${isActive ? 'active' : ''}`} end>
          <LayoutDashboard size={20} />
          Tableau de bord
        </NavLink>
        <NavLink to="/scanner" className={({isActive}) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <Search size={20} />
          Scanner (IA)
        </NavLink>
        <NavLink to="/history" className={({isActive}) => `sidebar-link ${isActive ? 'active' : ''}`}>
          <History size={20} />
          Historique
        </NavLink>
      </nav>
    </div>
  );
}
