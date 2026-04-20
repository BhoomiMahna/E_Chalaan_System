/**
 * Analytics Page — Advanced charts, AI predictions, and insights.
 */
import { useState, useEffect } from 'react';
import { HourlyChart, LocationBarChart } from '../components/Charts';
import { getStats, aiPredict } from '../services/api';
import { TrendingUp, MapPin, Clock, Brain } from 'lucide-react';

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadStats = async () => {
      try {
        const res = await getStats();
        if (!cancelled) setStats(res.data);
      } catch (err) {
        console.error('Failed to load stats:', err);
      }
    };

    const loadPredictions = async () => {
      try {
        const res = await aiPredict();
        if (!cancelled && res.data.success) {
          setPredictions(res.data.predictions);
        }
      } catch (err) {
        console.error('Failed to load predictions:', err);
      }
    };

    Promise.all([loadStats(), loadPredictions()]).finally(() => {
      if (!cancelled) setLoading(false);
    });

    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <div>
        <div className="page-header"><h1>Analytics & Predictions</h1><p>Loading...</p></div>
        {[1,2].map(i => <div key={i} className="skeleton" style={{ height: 300, marginBottom: 20, borderRadius: 16 }} />)}
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Analytics & Predictions</h1>
        <p>Advanced analytics and AI-powered predictive insights</p>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3><Clock size={16} style={{ display: 'inline', marginRight: 8 }} />Violations by Hour of Day</h3>
          <HourlyChart data={stats?.hourly || []} />
        </div>
        <div className="chart-card">
          <h3><MapPin size={16} style={{ display: 'inline', marginRight: 8 }} />Top Violation Locations</h3>
          <LocationBarChart data={stats?.by_location || []} />
        </div>
      </div>

      {/* AI Insights */}
      {predictions?.insights?.length > 0 && (
        <div className="glass-card" style={{ marginBottom: 20 }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <Brain size={20} style={{ color: 'var(--accent-violet)' }} /> AI Insights
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {predictions.insights.map((insight, i) => (
              <div key={i} style={{
                padding: '12px 16px', background: 'var(--bg-glass)',
                borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)',
                fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-secondary)',
              }}>
                {insight}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* High Risk Areas */}
      {predictions?.high_risk_areas?.length > 0 && (
        <div className="glass-card" style={{ marginBottom: 20 }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <MapPin size={20} style={{ color: 'var(--accent-rose)' }} /> High Risk Areas
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
            {predictions.high_risk_areas.map((area, i) => (
              <div key={i} style={{
                padding: 16, background: 'var(--bg-glass)',
                borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)',
                borderLeft: `3px solid ${area.risk_level === 'high' ? 'var(--accent-rose)' : area.risk_level === 'medium' ? 'var(--accent-amber)' : 'var(--accent-emerald)'}`,
              }}>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{area.location}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {area.violation_count} violations ({area.percentage}%)
                </div>
                <span className={`badge ${area.risk_level === 'high' ? 'no_helmet' : area.risk_level === 'medium' ? 'pending' : 'paid'}`}
                  style={{ marginTop: 8 }}>
                  {area.risk_level} risk
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 7-Day Forecast */}
      {predictions?.violation_forecast?.length > 0 && (
        <div className="glass-card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <TrendingUp size={20} style={{ color: 'var(--accent-cyan)' }} /> 7-Day Violation Forecast
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: 10 }}>
            {predictions.violation_forecast.map((f, i) => (
              <div key={i} style={{
                padding: 16, textAlign: 'center', background: 'var(--bg-glass)',
                borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)',
              }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>
                  {new Date(f.date).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric' })}
                </div>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                  {f.predicted_count}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>predicted</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
