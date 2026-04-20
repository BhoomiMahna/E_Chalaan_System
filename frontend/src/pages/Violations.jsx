/**
 * Violations Page — Full table with search, filters, pagination, and detail modal.
 */
import { useState, useEffect, useCallback } from 'react';
import ViolationTable from '../components/ViolationTable';
import Filters from '../components/Filters';
import { filterViolations, getViolations, aiExplain } from '../services/api';
import { X, Bot, Loader2 } from 'lucide-react';

export default function Violations() {
  const [violations, setViolations] = useState([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [selected, setSelected] = useState(null);
  const [explanation, setExplanation] = useState('');
  const [explaining, setExplaining] = useState(false);

  const loadData = useCallback(async (p = page) => {
    setLoading(true);
    try {
      const hasFilters = Object.values(filters).some(v => v);
      let res;
      if (hasFilters) {
        res = await filterViolations({ ...filters, page: p, per_page: 20 });
      } else {
        res = await getViolations(p, 20);
      }
      setViolations(res.data.violations || []);
      setTotal(res.data.total || 0);
      setPages(res.data.pages || 1);
    } catch (err) {
      console.error('Failed to load violations:', err);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => { loadData(page); }, [page]);

  const handleSearch = () => { setPage(1); loadData(1); };

  const handleViewDetail = async (violation) => {
    setSelected(violation);
    setExplanation('');
    setExplaining(true);
    try {
      const res = await aiExplain(violation.id);
      setExplanation(res.data.explanation || 'No explanation available.');
    } catch {
      setExplanation('Could not generate explanation. AI service may be unavailable.');
    } finally {
      setExplaining(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Violations</h1>
        <p>Browse, search, and filter all traffic violation records</p>
      </div>

      <Filters filters={filters} onChange={setFilters} onSearch={handleSearch} />

      <div style={{ marginBottom: 12, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        Showing {violations.length} of {total} violations
      </div>

      {loading ? (
        <div className="table-container" style={{ padding: 40, textAlign: 'center' }}>
          <Loader2 size={32} className="spinning" style={{ color: 'var(--accent-indigo)', animation: 'spin 1s linear infinite' }} />
          <p style={{ marginTop: 12, color: 'var(--text-muted)' }}>Loading violations...</p>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      ) : (
        <ViolationTable violations={violations} onViewDetail={handleViewDetail} />
      )}

      {/* Pagination */}
      {pages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</button>
          {Array.from({ length: Math.min(pages, 7) }, (_, i) => {
            const p = i + 1;
            return (
              <button key={p} className={page === p ? 'active' : ''} onClick={() => setPage(p)}>
                {p}
              </button>
            );
          })}
          {pages > 7 && <span>...</span>}
          <button disabled={page >= pages} onClick={() => setPage(p => p + 1)}>Next</button>
        </div>
      )}

      {/* Detail Modal */}
      {selected && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
          animation: 'fadeIn 0.2s ease',
        }} onClick={() => setSelected(null)}>
          <div className="glass-card" style={{
            maxWidth: 600, width: '90%', maxHeight: '80vh', overflow: 'auto',
          }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 style={{ fontSize: '1.1rem' }}>Violation Detail #{selected.id}</h3>
              <button onClick={() => setSelected(null)} style={{ background: 'none', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
              <div><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Vehicle</span>
                <div style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '1.1rem' }}>{selected.vehicle_number}</div></div>
              <div><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Owner</span>
                <div>{selected.owner_name}</div></div>
              <div><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Type</span>
                <div><span className={`badge ${selected.violation_type}`}>
                  {selected.violation_type === 'no_helmet' ? 'No Helmet' : 'Red Light'}</span></div></div>
              <div><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Fine</span>
                <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>₹{selected.fine_amount?.toLocaleString()}</div></div>
              <div><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Location</span>
                <div>{selected.location}</div></div>
              <div><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Status</span>
                <div><span className={`badge ${selected.status}`}>{selected.status}</span></div></div>
              <div style={{ gridColumn: '1 / -1' }}><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Address</span>
                <div>{selected.address}</div></div>
            </div>

            <div style={{
              background: 'var(--bg-glass)', border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)', padding: 16,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <Bot size={18} style={{ color: 'var(--accent-indigo)' }} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>AI Explanation</span>
              </div>
              {explaining ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)' }}>
                  <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                  Generating explanation...
                </div>
              ) : (
                <div style={{ fontSize: '0.85rem', lineHeight: 1.7, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
                  {explanation}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
