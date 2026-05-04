const BASE = 'http://localhost:8000';
 
function getToken() {
  return localStorage.getItem('token');
}
 
async function request(path, options = {}) {
  const token = getToken();
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}
 
// Auth
export const login = (email, password) =>
  request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
 
export const getMe = () => request('/auth/me');
 
// Leaves (employee)
export const applyLeave = (data) =>
  request('/leaves/apply', { method: 'POST', body: JSON.stringify(data) });
export const getMyLeaves = (params = '') => request(`/leaves/my${params}`);
export const getMyBalance = () => request('/leaves/balance');
export const cancelLeave = (id) =>
  request(`/leaves/${id}`, { method: 'DELETE' });
 
// Manager
export const getPendingLeaves = () => request('/manager/pending');
export const approveLeave = (id, comment) =>
  request(`/manager/leaves/${id}/approve`, {
    method: 'PATCH',
    body: JSON.stringify({ comment }),
  });
export const rejectLeave = (id, comment) =>
  request(`/manager/leaves/${id}/reject`, {
    method: 'PATCH',
    body: JSON.stringify({ comment }),
  });
 
// Calendar
export const getWeekCalendar = () => request('/calendar/week');
export const getCalendarRange = (start, end) =>
  request(`/calendar/?start=${start}&end=${end}`);
 
// Admin
export const getAllLeaves = () => request('/admin/leaves');
export const getAdminStats = () => request('/admin/stats');
export const getAllUsers = () => request('/users/');
export const getManagers = () => request('/users/managers');
export const createUser = (data) =>
  request('/users/', { method: 'POST', body: JSON.stringify(data) });
export const changeRole = (id, role) =>
  request(`/admin/users/${id}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role }),
  });
 
// AI
export const parseLeaveNL = (text) =>
  request('/ai/parse-leave', { method: 'POST', body: JSON.stringify({ text }) });
export const getManagerInsights = (leaveId) =>
  request(`/ai/manager-insights/${leaveId}`);
export const getPatterns = (employeeId) =>
  request(`/ai/patterns/${employeeId}`);
 
export const chatStream = async (messages, onChunk) => {
  const res = await fetch(`${BASE}/ai/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ messages }),
  });
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onChunk(decoder.decode(value));
  }
};
 
export default { login, getMe };