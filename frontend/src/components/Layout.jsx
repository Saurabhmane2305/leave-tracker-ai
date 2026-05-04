import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
 
const NAV = {
  employee: [
    { key: 'dashboard', label: 'Dashboard', icon: '📊' },
    { key: 'apply', label: 'Apply Leave', icon: '✏️' },
    { key: 'history', label: 'My Leaves', icon: '📋' },
    { key: 'chat', label: 'AI Assistant', icon: '🤖' },
  ],
  manager: [
    { key: 'dashboard', label: 'Dashboard', icon: '📊' },
    { key: 'pending', label: 'Pending Approvals', icon: '⏳' },
    { key: 'calendar', label: 'Team Calendar', icon: '📅' },
    { key: 'chat', label: 'AI Assistant', icon: '🤖' },
  ],
  super_admin: [
    { key: 'dashboard', label: 'Dashboard', icon: '📊' },
    { key: 'admin-leaves', label: 'All Leaves', icon: '📋' },
    { key: 'admin-users', label: 'Users', icon: '👥' },
    { key: 'calendar', label: 'Calendar', icon: '📅' },
  ],
};
 
export default function Layout({ page, setPage, children }) {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const navItems = NAV[user?.role] || NAV.employee;
 
  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <span className="logo-icon">🗓</span>
          <span className="sidebar-title">LeaveTrack</span>
          <button className="sidebar-close" onClick={() => setMenuOpen(false)}>✕</button>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              key={item.key}
              className={`nav-item ${page === item.key ? 'nav-item-active' : ''}`}
              onClick={() => { setPage(item.key); setMenuOpen(false); }}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">{user?.name?.[0]?.toUpperCase()}</div>
            <div>
              <div className="user-name">{user?.name}</div>
              <div className="user-role">{user?.role?.replace('_', ' ')}</div>
            </div>
          </div>
          <button className="btn-logout" onClick={logout}>Sign Out</button>
        </div>
      </aside>
 
      {/* Overlay */}
      {menuOpen && <div className="overlay" onClick={() => setMenuOpen(false)} />}
 
      {/* Main */}
      <div className="main-wrap">
        <header className="topbar">
          <button className="hamburger" onClick={() => setMenuOpen(true)}>☰</button>
          <h2 className="page-title">
            {navItems.find((i) => i.key === page)?.label || 'Dashboard'}
          </h2>
          <div className="topbar-user">
            <span className="user-dept">{user?.department}</span>
            <div className="user-avatar sm">{user?.name?.[0]?.toUpperCase()}</div>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}