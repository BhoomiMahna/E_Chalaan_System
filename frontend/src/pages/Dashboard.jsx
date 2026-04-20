/**
 * Dashboard Page — Overview with stats, charts, and recent violations.
 */
import { useState, useEffect } from 'react';
import StatsCards from '../components/StatsCards';
import { ViolationsBarChart, FinesLineChart, ViolationTypePie } from '../components/Charts';
import { getStats, getViolations } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, violRes] = await Promise.all([
        getStats(),
        getViolations(1, 5),
      ]);
      setStats(statsRes.data);
      setRecent(violRes.data.violations || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <h1>Dashboard</h1>
          <p>Loading overview...</p>
        </div>
        <div className="stats-grid">
          {[1,2,3,4].map(i => (
            <div key={i} className="skeleton" style={{ height: 100, borderRadius: 16 }} />
          ))}
        </div>
      </div>
    );
  }

  const formatDate = (dt) => {
    if (!dt) return '';
    try {
      return new Date(dt).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
    } catch { return dt; }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Real-time overview of traffic violation monitoring system</p>
      </div>

      <StatsCards stats={stats} />

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Violations Per Day (Last 30 Days)</h3>
          <ViolationsBarChart data={stats?.daily || []} />
        </div>
        <div className="chart-card">
          <h3>Fines Collected (Last 30 Days)</h3>
          <FinesLineChart data={stats?.daily || []} />
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Violation Type Distribution</h3>
          <ViolationTypePie data={stats?.by_type} />
        </div>
        <div className="chart-card">
          <h3>Recent Violations</h3>
          {recent.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {recent.map((v) => (
                <div key={v.id} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '12px 16px', background: 'var(--bg-glass)',
                  borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)',
                }}>
                  <div>
                    <span style={{ fontFamily: 'monospace', fontWeight: 600, color: 'var(--text-primary)', marginRight: 12 }}>
                      {v.vehicle_number}
                    </span>
                    <span className={`badge ${v.violation_type}`}>
                      {v.violation_type === 'no_helmet' ? 'No Helmet' : 'Red Light'}
                    </span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>₹{v.fine_amount?.toLocaleString()}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{formatDate(v.date_time)}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state"><p>No recent violations</p></div>
          )}
        </div>
      </div>

      {stats && (
        <div className="charts-grid" style={{ marginTop: 0 }}>
          <div className="chart-card">
            <h3>Week Summary</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div style={{ padding: 16, background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-indigo)' }}>
                  {stats.week_violations?.toLocaleString() || 0}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>This Week Violations</div>
              </div>
              <div style={{ padding: 16, background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>
                  ₹{(stats.week_fines || 0).toLocaleString()}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>This Week Fines</div>
              </div>
            </div>
          </div>
          <div className="chart-card">
            <h3>Status Breakdown</h3>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {stats.by_status && Object.entries(stats.by_status).map(([status, count]) => (
                <div key={status} style={{
                  flex: 1, minWidth: 100, padding: 16,
                  background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)', textAlign: 'center'
                }}>
                  <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{count}</div>
                  <span className={`badge ${status}`}>{status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
