import { useEffect, useState } from 'react';
import { getPendingLeaves, approveLeave, rejectLeave, getManagerInsights } from '../api';
 
export default function PendingApprovalsPage() {
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [comment, setComment] = useState({});
  const [insights, setInsights] = useState({});
  const [insightLoading, setInsightLoading] = useState({});
  const [acting, setActing] = useState({});
  const [error, setError] = useState('');
 
  useEffect(() => {
    getPendingLeaves()
      .then((data) => setLeaves(Array.isArray(data) ? data : []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);
 
  const act = async (id, action) => {
    setActing((a) => ({ ...a, [id]: true }));
    try {
      const fn = action === 'approve' ? approveLeave : rejectLeave;
      await fn(id, comment[id] || '');
      setLeaves((l) => l.filter((x) => x.id !== id));
    } catch (e) {
      alert(e.message);
    } finally {
      setActing((a) => ({ ...a, [id]: false }));
    }
  };
 
  const loadInsights = async (id) => {
    setInsightLoading((i) => ({ ...i, [id]: true }));
    try {
      const data = await getManagerInsights(id);
      // handle both {insight: "..."} and plain string responses
      setInsights((i) => ({ ...i, [id]: data.insight || data.message || JSON.stringify(data) }));
    } catch (e) {
      setInsights((i) => ({ ...i, [id]: 'Could not load insights: ' + e.message }));
    } finally {
      setInsightLoading((i) => ({ ...i, [id]: false }));
    }
  };
 
  if (loading) return <div className="loader">Loading…</div>;
 
  return (
    <div className="page-content">
      {error && <div className="alert alert-error">{error}</div>}
 
      {leaves.length === 0 ? (
        <div className="empty-state">🎉 No pending approvals!</div>
      ) : (
        <div className="approval-list">
          {leaves.map((l) => (
            <div className="approval-card" key={l.id}>
              <div className="approval-header">
                <div>
                  <div className="approval-name">{l.employee_name}</div>
                  <div className="approval-meta">{l.department} · {l.leave_type_name}</div>
                </div>
                <div className="approval-dates">
                  {l.start_date} → {l.end_date}
                  <span className="badge badge-yellow">{l.working_days} days</span>
                </div>
              </div>
 
              <div className="approval-reason">"{l.reason}"</div>
 
              {insights[l.id] ? (
                <div className="insight-box">{insights[l.id]}</div>
              ) : (
                <button
                  className="btn-insight"
                  onClick={() => loadInsights(l.id)}
                  disabled={insightLoading[l.id]}
                >
                  {insightLoading[l.id] ? '⏳ Loading insights…' : '🤖 Get AI Insights'}
                </button>
              )}
 
              <div className="approval-actions">
                <input
                  className="comment-input"
                  placeholder="Add comment (optional)…"
                  value={comment[l.id] || ''}
                  onChange={(e) => setComment((c) => ({ ...c, [l.id]: e.target.value }))}
                />
                <div className="action-btns">
                  <button
                    className="btn btn-success"
                    onClick={() => act(l.id, 'approve')}
                    disabled={acting[l.id]}
                  >
                    ✓ Approve
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => act(l.id, 'reject')}
                    disabled={acting[l.id]}
                  >
                    ✗ Reject
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}