/**
 * StatsCards — Animated stat card grid for the dashboard overview.
 */
import { AlertTriangle, IndianRupee, Clock, CalendarDays } from 'lucide-react';

export default function StatsCards({ stats }) {
  if (!stats) return null;

  const cards = [
    {
      label: 'Total Violations',
      value: stats.total_violations?.toLocaleString() || '0',
      icon: AlertTriangle,
      color: 'indigo',
    },
    {
      label: 'Total Fines',
      value: `₹${(stats.total_fines || 0).toLocaleString()}`,
      icon: IndianRupee,
      color: 'emerald',
    },
    {
      label: 'Pending Cases',
      value: stats.pending_count?.toLocaleString() || '0',
      icon: Clock,
      color: 'amber',
    },
    {
      label: "Today's Violations",
      value: stats.today_count?.toLocaleString() || '0',
      icon: CalendarDays,
      color: 'rose',
    },
  ];

  return (
    <div className="stats-grid">
      {cards.map((card, i) => (
        <div
          key={card.label}
          className={`stat-card ${card.color}`}
          style={{ animationDelay: `${i * 0.1}s` }}
        >
          <div className={`stat-icon ${card.color}`}>
            <card.icon size={22} />
          </div>
          <div className="stat-info">
            <h3>{card.value}</h3>
            <p>{card.label}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
