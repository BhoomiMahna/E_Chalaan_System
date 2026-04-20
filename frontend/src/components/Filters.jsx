/**
 * Filters — Filter bar component for violations page.
 */
import { Search, Filter } from 'lucide-react';

export default function Filters({ filters, onChange, onSearch }) {
  const handleChange = (key, value) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="filters-bar">
      <div style={{ position: 'relative', flex: '1', maxWidth: 280 }}>
        <Search size={16} style={{
          position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
          color: 'var(--text-muted)'
        }} />
        <input
          type="text"
          className="input-field"
          placeholder="Search vehicle number..."
          style={{ paddingLeft: 36 }}
          value={filters.vehicle_number || ''}
          onChange={(e) => handleChange('vehicle_number', e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSearch?.()}
        />
      </div>

      <select
        className="select-field"
        value={filters.violation_type || ''}
        onChange={(e) => handleChange('violation_type', e.target.value)}
      >
        <option value="">All Types</option>
        <option value="no_helmet">No Helmet</option>
        <option value="red_light">Red Light</option>
      </select>

      <select
        className="select-field"
        value={filters.status || ''}
        onChange={(e) => handleChange('status', e.target.value)}
      >
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="paid">Paid</option>
        <option value="disputed">Disputed</option>
      </select>

      <input
        type="date"
        className="input-field"
        style={{ maxWidth: 180 }}
        value={filters.start_date || ''}
        onChange={(e) => handleChange('start_date', e.target.value)}
        title="Start date"
      />

      <input
        type="date"
        className="input-field"
        style={{ maxWidth: 180 }}
        value={filters.end_date || ''}
        onChange={(e) => handleChange('end_date', e.target.value)}
        title="End date"
      />

      <button className="btn btn-primary" onClick={onSearch}>
        <Filter size={16} /> Apply
      </button>
    </div>
  );
}
