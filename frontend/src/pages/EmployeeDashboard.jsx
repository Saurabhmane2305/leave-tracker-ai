import { useEffect, useState } from 'react';
import { getMyBalance, getMyLeaves } from '../api';
 
const STATUS_COLOR = {
  pending: 'badge-yellow',
  approved: 'badge-green',
  rejected: 'badge-red',
};
 
export default function EmployeeDashboard({ setPage }) {
  const [balance, setBalance] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
 
  useEffect(() => {
    Promise.all([getMyBalance(), getMyLeaves()])
      .then(([bal, lv]) => {
        setBalance(Array.isArray(bal) ? bal : []);
        setLeaves(Array.isArray(lv) ? lv : []);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);
 
  if (loading) return <div className="loader">Loading…</div>;
 
  const recent = leaves.slice(0, 5);
 
  return (
    <div className="page-content">
      {error && <div className="alert alert-error">{error}</div>}
 
      <section>
        <h3 className="section-title">Leave Balance</h3>
        {balance.length === 0 ? (
          <div className="empty-state">No balance data found.</div>
        ) : (
          <div className="cards-grid">
            {balance.map((b) => {
              const quota = b.yearly_quota || 0;
              const used = b.used_days || 0;
              const remaining = b.remaining ?? (quota - used);
              const pct = quota > 0 ? Math.min((used / quota) * 100, 100) : 0;
              return (
                <div className="balance-card" key={b.leave_type_id}>
                  <div className="balance-type">{b.leave_type_name}</div>
                  <div className="balance-numbers">
                    <span className="balance-remaining">{remaining}</span>
                    <span className="balance-total">/ {quota}</span>
                  </div>
                  <div className="balance-bar">
                    <div className="balance-fill" style={{ width: `${pct}%` }} />
                  </div>
                  <div className="balance-used">{used} used</div>
                </div>
              );
            })}
          </div>
        )}
      </section>
 
      <section>
        <h3 className="section-title">Quick Actions</h3>
        <div className="quick-actions">
          <button className="quick-btn" onClick={() => setPage('apply')}>
            <span>✏️</span> Apply for Leave
          </button>
          <button className="quick-btn" onClick={() => setPage('history')}>
            <span>📋</span> View History
          </button>
          <button className="quick-btn" onClick={() => setPage('chat')}>
            <span>🤖</span> AI Assistant
          </button>
        </div>
      </section>
 
      <section>
        <h3 className="section-title">Recent Requests</h3>
        {recent.length === 0 ? (
          <div className="empty-state">No leave requests yet.</div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>From</th>
                  <th>To</th>
                  <th>Days</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((l) => (
                  <tr key={l.id}>
                    <td>{l.leave_type_name}</td>
                    <td>{l.start_date}</td>
                    <td>{l.end_date}</td>
                    <td>{l.working_days}</td>
                    <td>
                      <span className={`badge ${STATUS_COLOR[l.status] || 'badge-yellow'}`}>
                        {l.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}