/**
 * ViolationTable — Reusable data table for displaying violation records.
 */
import { Eye } from 'lucide-react';

export default function ViolationTable({ violations, onViewDetail }) {
  if (!violations?.length) {
    return (
      <div className="table-container">
        <div className="empty-state">
          <h3>No violations found</h3>
          <p>Try adjusting your filters or search criteria.</p>
        </div>
      </div>
    );
  }

  const formatDate = (dt) => {
    if (!dt) return 'N/A';
    try {
      const d = new Date(dt);
      return d.toLocaleDateString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
      }) + ' ' + d.toLocaleTimeString('en-IN', {
        hour: '2-digit', minute: '2-digit',
      });
    } catch { return dt; }
  };

  const typeLabel = (t) => t === 'no_helmet' ? 'No Helmet' : 'Red Light';

  return (
    <div className="table-container">
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Vehicle No.</th>
              <th>Owner</th>
              <th>Violation</th>
              <th>Fine</th>
              <th>Date & Time</th>
              <th>Location</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {violations.map((v) => (
              <tr key={v.id}>
                <td>#{v.id}</td>
                <td style={{ fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                  {v.vehicle_number}
                </td>
                <td>{v.owner_name}</td>
                <td><span className={`badge ${v.violation_type}`}>{typeLabel(v.violation_type)}</span></td>
                <td style={{ fontWeight: 600 }}>₹{v.fine_amount?.toLocaleString()}</td>
                <td style={{ fontSize: '0.8rem' }}>{formatDate(v.date_time)}</td>
                <td style={{ fontSize: '0.8rem' }}>{v.location}</td>
                <td><span className={`badge ${v.status}`}>{v.status}</span></td>
                <td>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => onViewDetail?.(v)}
                    title="View details & AI explanation"
                  >
                    <Eye size={14} /> View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
