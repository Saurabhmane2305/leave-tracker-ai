import { useEffect, useState } from 'react';
import { applyLeave, getMyBalance, parseLeaveNL, getManagers } from '../api';
 
export default function ApplyLeavePage() {
  const [form, setForm] = useState({
    leave_type_id: '',
    manager_id: '',
    start_date: '',
    end_date: '',
    reason: '',
  });
  const [balance, setBalance] = useState([]);
  const [managers, setManagers] = useState([]);
  const [nlText, setNlText] = useState('');
  const [nlLoading, setNlLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
 
  useEffect(() => {
    Promise.all([getMyBalance(), getManagers()])
      .then(([bal, mgrs]) => {
        setBalance(Array.isArray(bal) ? bal : []);
        setManagers(Array.isArray(mgrs) ? mgrs : []);
      })
      .catch((e) => setError('Failed to load form data: ' + e.message));
  }, []);
 
  const handleNLParse = async () => {
    if (!nlText.trim()) return;
    setNlLoading(true);
    setError('');
    try {
      const parsed = await parseLeaveNL(nlText);
      setForm((f) => ({
        ...f,
        start_date: parsed.start_date || f.start_date,
        end_date: parsed.end_date || f.end_date,
        reason: parsed.reason || f.reason,
        leave_type_id: parsed.leave_type_id ? String(parsed.leave_type_id) : f.leave_type_id,
      }));
    } catch (e) {
      setError('Could not parse. Please fill manually.');
    } finally {
      setNlLoading(false);
    }
  };
 
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.leave_type_id) { setError('Please select a leave type.'); return; }
    if (!form.manager_id) { setError('Please select a manager.'); return; }
    if (!form.start_date || !form.end_date) { setError('Please select both dates.'); return; }
    if (form.end_date < form.start_date) { setError('End date cannot be before start date.'); return; }
 
    setSubmitting(true);
    setError('');
    setSuccess('');
    try {
      await applyLeave({
        ...form,
        leave_type_id: parseInt(form.leave_type_id),
        manager_id: parseInt(form.manager_id),
      });
      setSuccess('Leave applied successfully!');
      setForm({ leave_type_id: '', manager_id: '', start_date: '', end_date: '', reason: '' });
      setNlText('');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };
 
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
 
  return (
    <div className="page-content">
      <div className="form-card">
        <div className="nl-section">
          <label className="section-title">🤖 AI Quick Fill</label>
          <p className="hint">Describe your leave in plain English</p>
          <div className="nl-row">
            <input
              className="nl-input"
              placeholder="e.g. I need Monday and Tuesday off for a family function"
              value={nlText}
              onChange={(e) => setNlText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleNLParse()}
            />
            <button className="btn btn-secondary" onClick={handleNLParse} disabled={nlLoading}>
              {nlLoading ? '…' : 'Parse'}
            </button>
          </div>
        </div>
 
        <div className="divider" />
 
        {success && <div className="alert alert-success">{success}</div>}
        {error && <div className="alert alert-error">{error}</div>}
 
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Leave Type</label>
              <select value={form.leave_type_id} onChange={set('leave_type_id')}>
                <option value="">Select type</option>
                {balance.map((b) => (
                  <option key={b.leave_type_id} value={String(b.leave_type_id)}>
                    {b.leave_type_name} ({b.remaining ?? (b.yearly_quota - (b.used_days || 0))} days left)
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Manager</label>
              <select value={form.manager_id} onChange={set('manager_id')}>
                <option value="">Select manager</option>
                {managers.map((m) => (
                  <option key={m.id} value={String(m.id)}>{m.name} — {m.department}</option>
                ))}
              </select>
            </div>
          </div>
 
          <div className="form-row">
            <div className="form-group">
              <label>Start Date</label>
              <input type="date" value={form.start_date} onChange={set('start_date')} />
            </div>
            <div className="form-group">
              <label>End Date</label>
              <input type="date" value={form.end_date} onChange={set('end_date')} />
            </div>
          </div>
 
          <div className="form-group">
            <label>Reason</label>
            <textarea
              rows={3}
              value={form.reason}
              onChange={set('reason')}
              placeholder="Brief reason for leave…"
              required
            />
          </div>
 
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit Leave Request'}
          </button>
        </form>
      </div>
    </div>
  );
}