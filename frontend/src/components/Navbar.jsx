/**
 * Navbar — Sidebar navigation with icons, active state, and branding.
 */
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, FileWarning, BarChart3, Video, Bot, Shield
} from 'lucide-react';
import './Navbar.css';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/violations', icon: FileWarning, label: 'Violations' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/live-feed', icon: Video, label: 'Live Feed' },
  { to: '/assistant', icon: Bot, label: 'AI Assistant' },
];

export default function Navbar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Shield size={24} />
        </div>
        <div>
          <h1>TrafficAI</h1>
          <span>E-Challan System</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `nav-link ${isActive ? 'active' : ''}`
            }
            end={item.to === '/'}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot"></span>
          System Online
        </div>
      </div>
    </aside>
  );
}
