

import { useEffect, useState } from 'react';
import { getWeekCalendar } from '../api';
 
export default function CalendarPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
 
  useEffect(() => {
    getWeekCalendar()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);
 
  if (loading) return <div className="loader">Loading…</div>;
  if (!data) return <div className="empty-state">No data available.</div>;
 
  const renderWeek = (weekData, title) => (
    <div className="calendar-week" key={title}>
      <h4 className="week-title">{title}</h4>
      {weekData && weekData.length > 0 ? (
        <div className="calendar-entries">
          {weekData.map((entry, i) => (
            <div className="cal-entry" key={i}>
              <div className="cal-avatar">{entry.name?.[0]?.toUpperCase()}</div>
              <div>
                <div className="cal-name">{entry.name}</div>
                <div className="cal-meta">{entry.leave_type} · {entry.department}</div>
              </div>
              <div className="cal-dates">
                {entry.start_date} → {entry.end_date}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="cal-empty">No one on leave</div>
      )}
    </div>
  );
 
  return (
    <div className="page-content">
      <div className="calendar-grid">
        {renderWeek(data.this_week, '📅 This Week')}
        {renderWeek(data.next_week, '📅 Next Week')}
      </div>
    </div>
  );
}