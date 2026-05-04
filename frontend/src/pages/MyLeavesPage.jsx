import { useEffect, useState } from 'react';
import { getMyLeaves, cancelLeave } from '../api';
 
const STATUS_COLOR = { pending: 'badge-yellow', approved: 'badge-green', rejected: 'badge-red' };
 
export default function MyLeavesPage() {
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState('');
 
  const load = () => {
    setLoading(true);
    setError('');
    // Bug fix: don't send ?status=all — backend doesn't know 'all'
    const q = filter !== 'all' ? `?status=${filter}` : '';
    getMyLeaves(q)
      .then((data) => setLeaves(Array.isArray(data) ? data : []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };
 
  useEffect(() => { load(); }, [filter]);
 
  const handleCancel = async (id) => {
    if (!window.confirm('Cancel this leave request?')) return;
    try {
      await cancelLeave(id);
      setLeaves((l) => l.filter((x) => x.id !== id));
    } catch (e) {
      alert(e.message);
    }
  };
 
  return (
    <div className="page-content">
      <div className="filter-row">
        {['all', 'pending', 'approved', 'rejected'].map((s) => (
          <button
            key={s}
            className={`filter-btn ${filter === s ? 'active' : ''}`}
            onClick={() => setFilter(s)}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>
 
      {error && <div className="alert alert-error">{error}</div>}
 
      {loading ? (
        <div className="loader">Loading…</div>
      ) : leaves.length === 0 ? (
        <div className="empty-state">No leave requests found.</div>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Type</th>
                <th>From</th>
                <th>To</th>
                <th>Days</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Comment</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {leaves.map((l) => (
                <tr key={l.id}>
                  <td>{l.leave_type_name}</td>
                  <td>{l.start_date}</td>
                  <td>{l.end_date}</td>
                  <td>{l.working_days}</td>
                  <td className="td-reason">{l.reason}</td>
                  <td>
                    <span className={`badge ${STATUS_COLOR[l.status] || 'badge-yellow'}`}>
                      {l.status}
                    </span>
                  </td>
                  <td className="td-comment">{l.manager_comment || '—'}</td>
                  <td>
                    {l.status === 'pending' && (
                      <button className="btn-danger-sm" onClick={() => handleCancel(l.id)}>
                        Cancel
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}