import { useState, useEffect, useRef } from 'react';
import { Bell, Clock, Wifi, WifiOff, X, AlertOctagon, Flame, Minus, CheckCircle } from 'lucide-react';
import { API_BASE } from '../config';

function getSev(score) {
  if (score >= 9) return { cls: 'badge-critical', label: 'Critical', Icon: AlertOctagon };
  if (score >= 7) return { cls: 'badge-high',     label: 'High',     Icon: Flame        };
  if (score >= 5) return { cls: 'badge-moderate', label: 'Moderate', Icon: Minus        };
  return               { cls: 'badge-low',        label: 'Low',      Icon: CheckCircle  };
}

export default function TopBar({ title }) {
  const [ok,          setOk]       = useState(true);
  const [incidents,   setIncidents]= useState([]);
  const [time,        setTime]     = useState(new Date());
  const [bellOpen,    setBellOpen] = useState(false);
  const bellRef = useRef(null);

  /* Fetch incidents for notification panel */
  useEffect(() => {
    const go = () => {
      fetch(`${API_BASE}/api/incidents`)
        .then(r => r.json())
        .then(d => { setIncidents(d); setOk(true); })
        .catch(() => setOk(false));
    };
    go();
    const id = setInterval(go, 5000);
    return () => clearInterval(id);
  }, []);

  /* Live clock */
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  /* Close dropdown when clicking outside */
  useEffect(() => {
    const handler = (e) => {
      if (bellRef.current && !bellRef.current.contains(e.target)) {
        setBellOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const dateStr = time.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
  const timeStr = time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });

  /* Show only the 5 most recent incidents */
  const recent = [...incidents].sort((a, b) => (b.timestamp ?? '') > (a.timestamp ?? '') ? 1 : -1).slice(0, 5);

  return (
    <header className="topbar">
      <div className="topbar-left">
        <div className="topbar-title">{title}</div>
      </div>

      <div className="topbar-right">
        {/* Date / time */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#9DAABF' }}>
          <Clock size={13} />
          <span style={{ fontSize: 12, fontFamily: '"JetBrains Mono", monospace', letterSpacing: '0.02em' }}>
            {dateStr} | {timeStr}
          </span>
        </div>

        {/* Connection status */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 5,
          padding: '4px 10px', borderRadius: 20,
          background: ok ? 'rgba(22,163,74,0.08)' : 'rgba(220,38,38,0.08)',
          border: `1px solid ${ok ? 'rgba(22,163,74,0.2)' : 'rgba(220,38,38,0.2)'}`,
        }}>
          {ok ? <Wifi size={12} color="#16A34A" /> : <WifiOff size={12} color="#DC2626" />}
          <span style={{ fontSize: 11.5, fontWeight: 500, color: ok ? '#16A34A' : '#DC2626' }}>
            {ok ? 'Connected' : 'Offline'}
          </span>
        </div>

        {/* Bell with dropdown */}
        <div ref={bellRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setBellOpen(o => !o)}
            style={{
              position: 'relative', background: bellOpen ? '#F4F6FB' : '#fff',
              border: '1px solid #E5E9F2', borderRadius: 8,
              width: 34, height: 34, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#9DAABF', transition: 'background 0.15s',
            }}
            title="Notifications"
          >
            <Bell size={15} />
            {incidents.length > 0 && (
              <span style={{
                position: 'absolute', top: -4, right: -4,
                background: '#DC2626', color: '#fff', borderRadius: 20,
                fontSize: 9.5, fontWeight: 700,
                minWidth: 16, height: 16,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                padding: '0 3px', border: '1.5px solid #fff',
              }}>
                {incidents.length}
              </span>
            )}
          </button>

          {/* Dropdown panel */}
          {bellOpen && (
            <div style={{
              position: 'absolute', top: 40, right: 0,
              width: 340, background: '#fff',
              border: '1px solid #E5E9F2', borderRadius: 12,
              boxShadow: '0 8px 30px rgba(15,23,51,0.12), 0 2px 8px rgba(15,23,51,0.06)',
              zIndex: 9999, overflow: 'hidden',
              animation: 'fadeUp 0.18s cubic-bezier(0.23,1,0.32,1) both',
            }}>
              {/* Header */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 14px', borderBottom: '1px solid #E5E9F2',
                background: '#F8F9FC',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                  <Bell size={13} color="#1B4FDC" />
                  <span style={{ fontSize: 13, fontWeight: 700, color: '#0F1733' }}>Notifications</span>
                  {incidents.length > 0 && (
                    <span className="badge badge-blue" style={{ padding: '1px 7px' }}>
                      {incidents.length}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => setBellOpen(false)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9DAABF', display: 'flex', alignItems: 'center' }}
                >
                  <X size={15} />
                </button>
              </div>

              {/* Notification list */}
              <div style={{ maxHeight: 320, overflowY: 'auto' }}>
                {recent.length === 0 ? (
                  <div style={{ padding: '28px 14px', textAlign: 'center', color: '#9DAABF', fontSize: 13 }}>
                    No incidents yet
                  </div>
                ) : (
                  recent.map((inc, i) => {
                    const { cls, label, Icon: SIcon } = getSev(inc.severity_score ?? 0);
                    const ts = inc.timestamp
                      ? new Date(inc.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
                      : '';
                    return (
                      <div
                        key={i}
                        style={{
                          padding: '11px 14px',
                          borderBottom: i < recent.length - 1 ? '1px solid #F4F6FB' : 'none',
                          transition: 'background 0.15s',
                          cursor: 'default',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.background = '#F8F9FC'; }}
                        onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
                          <span className={`badge ${cls}`}>
                            <SIcon size={10} />
                            {inc.severity_score ?? '—'}/10 · {label}
                          </span>
                          <span style={{ fontSize: 11, color: '#9DAABF', fontFamily: '"JetBrains Mono", monospace' }}>{ts}</span>
                        </div>
                        <p style={{
                          fontSize: 12.5, color: '#4A5568', lineHeight: 1.45,
                          overflow: 'hidden', display: '-webkit-box',
                          WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
                        }}>
                          {inc.raw_report || '—'}
                        </p>
                        <div style={{ marginTop: 4, fontSize: 11, color: '#9DAABF' }}>
                          {inc.parallel_branch_triggered ? '5 agents activated' : '3 agents activated'}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* Footer */}
              <div style={{
                padding: '9px 14px', borderTop: '1px solid #E5E9F2',
                background: '#F8F9FC', textAlign: 'center',
              }}>
                <span style={{ fontSize: 11.5, color: '#1B4FDC', fontWeight: 500, cursor: 'pointer' }}
                  onClick={() => setBellOpen(false)}>
                  View all in Incident Management →
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Avatar */}
        <div style={{
          width: 34, height: 34, borderRadius: 8, background: '#1B4FDC',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 12, fontWeight: 700, color: '#fff', cursor: 'pointer',
          flexShrink: 0,
        }}>
          EC
        </div>
      </div>
    </header>
  );
}
