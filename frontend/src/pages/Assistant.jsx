/**
 * Assistant Page — AI chat interface with natural language query support.
 */
import { useState, useRef, useEffect } from 'react';
import { aiQuery } from '../services/api';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';

const QUICK_ACTIONS = [
  'Show helmet violations today',
  'Total fines this week',
  'Which area has most violations?',
  'How many pending violations?',
  'Show red light violations',
  'Total violations count',
];

export default function Assistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI Traffic Assistant. Ask me anything about violations, fines, or traffic data.\n\nTry questions like:\n- "Show helmet violations today"\n- "Total fines this week"\n- "Which area has most violations?"',
      time: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    const query = text || input.trim();
    if (!query || loading) return;

    const userMsg = { role: 'user', content: query, time: new Date().toLocaleTimeString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await aiQuery(query);
      const data = res.data.data || res.data;
      let response = '';

      if (data.error) {
        response = `Error: ${data.error}`;
      } else if (data.results?.length > 0) {
        // Format results
        if (data.results.length === 1 && Object.keys(data.results[0]).length <= 3) {
          // Aggregate result (count, sum, etc.)
          response = Object.entries(data.results[0])
            .map(([k, v]) => `**${k.replace(/_/g, ' ')}**: ${typeof v === 'number' ? v.toLocaleString() : v}`)
            .join('\n');
        } else {
          // Table-like results
          response = `Found **${data.count}** results:\n\n`;
          data.results.slice(0, 10).forEach((row, i) => {
            if (row.vehicle_number) {
              response += `${i + 1}. **${row.vehicle_number}** — ${row.violation_type === 'no_helmet' ? 'No Helmet' : row.violation_type === 'red_light' ? 'Red Light' : row.violation_type} — Rs.${row.fine_amount?.toLocaleString()} — ${row.status || ''}\n`;
            } else {
              response += `${i + 1}. ${Object.entries(row).map(([k, v]) => `${k}: ${v}`).join(' | ')}\n`;
            }
          });
          if (data.count > 10) response += `\n...and ${data.count - 10} more results`;
        }
        if (data.sql) response += `\n\n_SQL: \`${data.sql}\`_`;
      } else {
        response = 'No results found for your query. Try rephrasing your question.';
        if (data.sql) response += `\n\n_SQL: \`${data.sql}\`_`;
      }

      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: response,
        time: new Date().toLocaleTimeString(),
      }]);
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your query. Please try again.',
        time: new Date().toLocaleTimeString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>AI Assistant</h1>
        <p>Ask questions about violations, fines, and traffic data in natural language</p>
      </div>

      <div className="chat-container glass-card" style={{ padding: 0 }}>
        {/* Quick Actions */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <Sparkles size={14} /> Quick Queries
          </div>
          <div className="quick-actions">
            {QUICK_ACTIONS.map((q) => (
              <button key={q} className="quick-action-btn" onClick={() => sendMessage(q)}>
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="chat-messages" style={{ padding: '20px' }}>
          {messages.map((msg, i) => (
            <div key={i} className={`chat-message ${msg.role}`}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                {msg.role === 'assistant' ? (
                  <Bot size={16} style={{ color: 'var(--accent-indigo)' }} />
                ) : (
                  <User size={16} />
                )}
                <span style={{ fontWeight: 600, fontSize: '0.8rem' }}>
                  {msg.role === 'assistant' ? 'TrafficAI' : 'You'}
                </span>
              </div>
              <div className="msg-content">{msg.content}</div>
              <div className="msg-time">{msg.time}</div>
            </div>
          ))}
          {loading && (
            <div className="chat-message assistant">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)' }}>
                <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                Thinking...
              </div>
              <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="chat-input-bar" style={{ padding: '12px 20px' }}>
          <input
            className="input-field"
            placeholder="Ask about violations, fines, trends..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            disabled={loading}
          />
          <button
            className="btn btn-primary"
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
