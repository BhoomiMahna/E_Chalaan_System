/**
 * Charts — Recharts-based chart components for dashboard and analytics.
 */
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const COLORS = ['#6366f1', '#22d3ee', '#10b981', '#f59e0b', '#f43f5e', '#8b5cf6', '#ec4899'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(17, 24, 39, 0.95)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '8px',
      padding: '10px 14px',
      fontSize: '0.8rem',
    }}>
      <p style={{ color: '#94a3b8', marginBottom: 4 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}
        </p>
      ))}
    </div>
  );
};

export function ViolationsBarChart({ data }) {
  if (!data?.length) return <div className="empty-state"><p>No data available</p></div>;
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={(v) => v?.slice(5)} />
        <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" name="Violations" fill="#6366f1" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function FinesLineChart({ data }) {
  if (!data?.length) return <div className="empty-state"><p>No data available</p></div>;
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={(v) => v?.slice(5)} />
        <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
        <Tooltip content={<CustomTooltip />} />
        <Line type="monotone" dataKey="fines" name="Fines (₹)" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function ViolationTypePie({ data }) {
  if (!data) return null;
  const pieData = Object.entries(data).map(([key, val]) => ({
    name: key === 'no_helmet' ? 'No Helmet' : 'Red Light',
    value: val.count,
  }));
  if (!pieData.length) return <div className="empty-state"><p>No data</p></div>;
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100}
             paddingAngle={5} dataKey="value" label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}>
          {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function HourlyChart({ data }) {
  if (!data?.length) return <div className="empty-state"><p>No data</p></div>;
  const sorted = [...data].sort((a, b) => a.hour - b.hour);
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={sorted}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={(v) => `${v}:00`} />
        <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" name="Violations" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function LocationBarChart({ data }) {
  if (!data?.length) return <div className="empty-state"><p>No data</p></div>;
  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} />
        <YAxis dataKey="location" type="category" tick={{ fill: '#64748b', fontSize: 10 }} width={160} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="count" name="Violations" fill="#22d3ee" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
