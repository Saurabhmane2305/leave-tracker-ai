import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import EmployeeDashboard from './pages/EmployeeDashboard';
import ManagerDashboard from './pages/ManagerDashboard';
import ApplyLeavePage from './pages/ApplyLeavePage';
import MyLeavesPage from './pages/MyLeavesPage';
import PendingApprovalsPage from './pages/PendingApprovalsPage';
import CalendarPage from './pages/CalendarPage';
import ChatPage from './pages/ChatPage';
import AdminDashboard, { AdminLeavesPage, AdminUsersPage } from './pages/AdminPages';
 
function AppInner() {
  const { user, loading } = useAuth();
  const [page, setPage] = useState('dashboard');
 
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div className="loader">Loading…</div>
      </div>
    );
  }
 
  if (!user) return <LoginPage />;
 
  const renderPage = () => {
    if (user.role === 'super_admin') {
      switch (page) {
        case 'dashboard': return <AdminDashboard />;
        case 'admin-leaves': return <AdminLeavesPage />;
        case 'admin-users': return <AdminUsersPage />;
        case 'calendar': return <CalendarPage />;
        default: return <AdminDashboard />;
      }
    }
    if (user.role === 'manager') {
      switch (page) {
        case 'dashboard': return <ManagerDashboard setPage={setPage} />;
        case 'pending': return <PendingApprovalsPage />;
        case 'calendar': return <CalendarPage />;
        case 'chat': return <ChatPage />;
        default: return <ManagerDashboard setPage={setPage} />;
      }
    }
    // employee
    switch (page) {
      case 'dashboard': return <EmployeeDashboard setPage={setPage} />;
      case 'apply': return <ApplyLeavePage />;
      case 'history': return <MyLeavesPage />;
      case 'chat': return <ChatPage />;
      default: return <EmployeeDashboard setPage={setPage} />;
    }
  };
 
  return (
    <Layout page={page} setPage={setPage}>
      {renderPage()}
    </Layout>
  );
}
 
export default function App() {
  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}