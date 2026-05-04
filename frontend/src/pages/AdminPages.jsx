import { useEffect, useState } from 'react';
import { getAdminStats, getAllLeaves, getAllUsers, createUser, changeRole } from '../api';
 
const STATUS_COLOR = { pending: 'badge-yellow', approved: 'badge-green', rejected: 'badge-red' };
 
export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
 
  useEffect(() => {
    getAdminStats()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);
 
  if (loading) return <div className="loader">Loading…</div>;
 
  return (
    <div className="page-content">
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-num">{stats.total_employees ?? '—'}</div>
            <div className="stat-label">Employees</div>
          </div>
          <div className="stat-card">
            <div className="stat-num">{stats.total_leaves ?? '—'}</div>
            <div className="stat-label">Total Requests</div>
          </div>
          <div className="stat-card">
            <div className="stat-num">{stats.pending ?? '—'}</div>
            <div className="stat-label">Pending</div>
          </div>
          <div className="stat-card">
            <div className="stat-num">{stats.approved ?? '—'}</div>
            <div className="stat-label">Approved</div>
          </div>
        </div>
      )}
    </div>
  );
}
 
export function AdminLeavesPage() {
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
 
  useEffect(() => {
    getAllLeaves().then(setLeaves).catch(console.error).finally(() => setLoading(false));
  }, []);
 
  if (loading) return <div className="loader">Loading…</div>;
 
  return (
    <div className="page-content">
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Type</th>
              <th>From</th>
              <th>To</th>
              <th>Days</th>
              <th>Manager</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {leaves.map((l) => (
              <tr key={l.id}>
                <td>{l.employee_name}</td>
                <td>{l.leave_type_name}</td>
                <td>{l.start_date}</td>
                <td>{l.end_date}</td>
                <td>{l.working_days}</td>
                <td>{l.manager_name}</td>
                <td><span className={`badge ${STATUS_COLOR[l.status]}`}>{l.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
 
export function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'employee', department: '' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
 
  useEffect(() => {
    getAllUsers().then(setUsers).catch(console.error).finally(() => setLoading(false));
  }, []);
 
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
 
  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const newUser = await createUser(form);
      setUsers((u) => [...u, newUser]);
      setShowForm(false);
      setForm({ name: '', email: '', password: '', role: 'employee', department: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };
 
  const handleRoleChange = async (id, role) => {
    try {
      await changeRole(id, role);
      setUsers((u) => u.map((x) => x.id === id ? { ...x, role } : x));
    } catch (e) {
      alert(e.message);
    }
  };
 
  if (loading) return <div className="loader">Loading…</div>;
 
  return (
    <div className="page-content">
      <div className="section-header">
        <h3 className="section-title">All Users</h3>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add User'}
        </button>
      </div>
 
      {showForm && (
        <div className="form-card">
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleCreate}>
            <div className="form-row">
              <div className="form-group">
                <label>Name</label>
                <input value={form.name} onChange={set('name')} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.email} onChange={set('email')} required />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={form.password} onChange={set('password')} required />
              </div>
              <div className="form-group">
                <label>Department</label>
                <input value={form.department} onChange={set('department')} required />
              </div>
            </div>
            <div className="form-group">
              <label>Role</label>
              <select value={form.role} onChange={set('role')}>
                <option value="employee">Employee</option>
                <option value="manager">Manager</option>
                <option value="super_admin">Super Admin</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Creating…' : 'Create User'}
            </button>
          </form>
        </div>
      )}
 
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Department</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td>{u.department}</td>
                <td>
                  <select
                    value={u.role}
                    onChange={(e) => handleRoleChange(u.id, e.target.value)}
                    className="role-select"
                  >
                    <option value="employee">Employee</option>
                    <option value="manager">Manager</option>
                    <option value="super_admin">Super Admin</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}