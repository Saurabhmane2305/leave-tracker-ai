import { useEffect, useState } from 'react';
import { getPendingLeaves, getWeekCalendar } from '../api';
 
export default function ManagerDashboard({ setPage }) {
  const [pending, setPending] = useState([]);
  const [calendar, setCalendar] = useState(null);
  const [loading, setLoading] = useState(true);
 
  useEffect(() => {
    Promise.all([getPendingLeaves(), getWeekCalendar()])
      .then(([p, c]) => { setPending(p); setCalendar(c); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);
 
  if (loading) return <div className="loader">Loading…</div>;
 
  return (
    <div className="page-content">
      <div className="stats-grid">
        <div className="stat-card stat-card-accent">
          <div className="stat-num">{pending.length}</div>
          <div className="stat-label">Pending Approvals</div>
        </div>
        <div className="stat-card">
          <div className="stat-num">{calendar?.this_week?.length ?? 0}</div>
          <div className="stat-label">On Leave This Week</div>
        </div>
        <div className="stat-card">
          <div className="stat-num">{calendar?.next_week?.length ?? 0}</div>
          <div className="stat-label">On Leave Next Week</div>
        </div>
      </div>
 
      <div className="quick-actions">
        <button className="quick-btn" onClick={() => setPage('pending')}>
          ⏳ Review Pending ({pending.length})
        </button>
        <button className="quick-btn" onClick={() => setPage('calendar')}>
          📅 Team Calendar
        </button>
        <button className="quick-btn" onClick={() => setPage('chat')}>
          🤖 AI Assistant
        </button>
      </div>
 
      {pending.length > 0 && (
        <section>
          <h3 className="section-title">Latest Pending</h3>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr><th>Employee</th><th>Type</th><th>From</th><th>To</th><th>Days</th></tr>
              </thead>
              <tbody>
                {pending.slice(0, 5).map((l) => (
                  <tr key={l.id}>
                    <td>{l.employee_name}</td>
                    <td>{l.leave_type_name}</td>
                    <td>{l.start_date}</td>
                    <td>{l.end_date}</td>
                    <td>{l.working_days}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}