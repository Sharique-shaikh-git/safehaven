import { useState, useEffect } from 'react';
import { Radio, Megaphone, Bell, Users, Building2, Globe, CheckCircle, XCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { API_BASE } from '../config';

const CHANNEL_CFG = {
  broadcast:       { label: 'Public Broadcast',    Icon: Globe,      color: '#1B4FDC', bg: 'rgba(27,79,220,0.08)'  },
  agency_alert:    { label: 'Agency Alert',         Icon: Bell,       color: '#DC2626', bg: 'rgba(220,38,38,0.08)'  },
  volunteer_alert: { label: 'Volunteer Dispatch',   Icon: Users,      color: '#D97706', bg: 'rgba(217,119,6,0.08)'  },
  shelter_update:  { label: 'Shelter Update',       Icon: Building2,  color: '#0891B2', bg: 'rgba(8,145,178,0.08)'  },
  family_update:   { label: 'Family Notification',  Icon: Megaphone,  color: '#7C3AED', bg: 'rgba(124,58,237,0.08)' },
  public_advisory: { label: 'Public Advisory',      Icon: Globe,      color: '#0F766E', bg: 'rgba(15,118,110,0.08)' },
};

function getCfg(ch) {
  return CHANNEL_CFG[ch] || { label: ch, Icon: Radio, color: '#9DAABF', bg: 'rgba(0,0,0,0.04)' };
}

function getSevColor(s) {
  if (s >= 9) return '#DC2626';
  if (s >= 7) return '#D97706';
  if (s >= 5) return '#CA8A04';
  return '#16A34A';
}

function CommCard({ c, i }) {
  const [open, setOpen] = useState(false);
  const cfg   = getCfg(c.channel);
  const Icon  = cfg.Icon;
  const ts    = c.incident_timestamp
    ? new Date(c.incident_timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
    : '';

  return (
    <div
      className="anim-fade-up"
      style={{
        border: '1px solid #E5E9F2', borderRadius: 10,
        overflow: 'hidden', animationDelay: `${i * 0.04}s`,
        transition: 'box-shadow 0.18s',
      }}
    >
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width: '100%', background: '#fff', border: 'none', cursor: 'pointer', textAlign: 'left',
          padding: '11px 14px',
          display: 'flex', alignItems: 'center', gap: 12,
          transition: 'background 0.15s',
        }}
        onMouseEnter={e => { e.currentTarget.style.background = '#F8F9FC'; }}
        onMouseLeave={e => { e.currentTarget.style.background = '#fff'; }}
      >
        {/* Channel icon */}
        <div style={{
          width: 36, height: 36, borderRadius: 9, flexShrink: 0,
          background: cfg.bg, border: `1px solid ${cfg.color}20`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Icon size={15} color={cfg.color} />
        </div>

        {/* Info */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 3 }}>
            <span style={{ fontSize: 12.5, fontWeight: 600, color: '#0F1733' }}>{cfg.label}</span>
            {c.incident_severity != null && (
              <span style={{
                fontSize: 10, fontWeight: 700, padding: '1px 5px', borderRadius: 4,
                background: `${getSevColor(c.incident_severity)}15`,
                color: getSevColor(c.incident_severity),
                border: `1px solid ${getSevColor(c.incident_severity)}25`,
              }}>
                Sev {c.incident_severity}
              </span>
            )}
          </div>
          <p style={{
            fontSize: 12, color: '#4A5568', overflow: 'hidden', textOverflow: 'ellipsis',
            whiteSpace: 'nowrap', maxWidth: 520,
          }}>
            {c.message_summary || '—'}
          </p>
        </div>

        {/* Right side */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          {c.sent
            ? <CheckCircle size={13} color="#16A34A" />
            : <XCircle    size={13} color="#DC2626" />
          }
          <span style={{ fontSize: 11, color: '#9DAABF', fontFamily: '"JetBrains Mono", monospace' }}>{ts}</span>
          {open ? <ChevronDown size={13} color="#9DAABF" /> : <ChevronRight size={13} color="#9DAABF" />}
        </div>
      </button>

      {/* Expanded body */}
      {open && (
        <div style={{ padding: '0 14px 14px', borderTop: '1px solid #F4F6FB' }}>
          <div style={{ display: 'flex', gap: 10, marginBottom: 8, marginTop: 10 }}>
            <span style={{ fontSize: 11, color: '#9DAABF', minWidth: 70 }}>Recipient</span>
            <span style={{ fontSize: 12, fontFamily: '"JetBrains Mono", monospace', color: '#4A5568' }}>{c.recipient || '—'}</span>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <span style={{ fontSize: 11, color: '#9DAABF', minWidth: 70, paddingTop: 2 }}>Message</span>
            <pre style={{
              fontSize: 12, color: '#4A5568', lineHeight: 1.65,
              whiteSpace: 'pre-wrap', wordBreak: 'break-word', flex: 1,
              background: '#F8F9FC', border: '1px solid #E5E9F2',
              borderRadius: 8, padding: '10px 12px', margin: 0,
              fontFamily: 'Inter, sans-serif',
            }}>
              {c.message_summary}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default function CommunicationsPage() {
  const [comms,   setComms]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter,  setFilter]  = useState('all');

  useEffect(() => {
    const go = () => {
      fetch(`${API_BASE}/api/communications`)
        .then(r => r.json()).then(d => { setComms(d); setLoading(false); })
        .catch(() => setLoading(false));
    };
    go();
    const id = setInterval(go, 10000);
    return () => clearInterval(id);
  }, []);

  const channels = ['all', ...new Set(comms.map(c => c.channel))];
  const filtered = filter === 'all' ? comms : comms.filter(c => c.channel === filter);

  const stats = {
    total: comms.length,
    sent:  comms.filter(c => c.sent).length,
    broadcast:       comms.filter(c => c.channel === 'broadcast').length,
    volunteer_alert: comms.filter(c => c.channel === 'volunteer_alert').length,
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60 }}>
        <div style={{ textAlign: 'center' }}>
          <Radio size={28} color="#9DAABF" style={{ marginBottom: 12 }} />
          <p style={{ color: '#9DAABF', fontSize: 13 }}>Loading communications…</p>
        </div>
      </div>
    );
  }

  if (!comms.length) {
    return (
      <div className="card" style={{ padding: '60px 24px', textAlign: 'center' }}>
        <div style={{
          width: 52, height: 52, borderRadius: 14, margin: '0 auto 14px',
          background: 'rgba(27,79,220,0.08)', border: '1px solid rgba(27,79,220,0.15)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Radio size={22} color="#1B4FDC" />
        </div>
        <p style={{ fontSize: 14, fontWeight: 500, color: '#4A5568', marginBottom: 5 }}>No communications yet</p>
        <p style={{ fontSize: 12.5, color: '#9DAABF' }}>
          Submit an incident on the Dashboard — the Communications Hub agent will automatically generate agency alerts, volunteer dispatches, and public briefings.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 }}>
        {[
          { label: 'Total Sent',       value: stats.sent,            color: '#1B4FDC', bg: 'rgba(27,79,220,0.07)'  },
          { label: 'Public Broadcasts',value: stats.broadcast,        color: '#0F766E', bg: 'rgba(15,118,110,0.07)' },
          { label: 'Volunteer Alerts', value: stats.volunteer_alert,  color: '#D97706', bg: 'rgba(217,119,6,0.07)'  },
          { label: 'Total Messages',   value: stats.total,            color: '#9DAABF', bg: 'rgba(0,0,0,0.03)'      },
        ].map(s => (
          <div key={s.label} style={{
            background: s.bg, border: `1px solid ${s.color}28`, borderRadius: 10, padding: '11px 14px',
          }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: s.color, lineHeight: 1 }}>{s.value}</div>
            <div style={{ fontSize: 11, color: '#9DAABF', marginTop: 4, fontWeight: 500 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Filter + list */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">Message Log</span>
          <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
            {channels.map(ch => {
              const label = ch === 'all' ? 'All' : (getCfg(ch).label);
              return (
                <button
                  key={ch}
                  onClick={() => setFilter(ch)}
                  className="btn btn-ghost"
                  style={{
                    padding: '3px 10px', fontSize: 11.5,
                    background: filter === ch ? 'rgba(27,79,220,0.08)' : undefined,
                    color: filter === ch ? '#1B4FDC' : undefined,
                    borderColor: filter === ch ? 'rgba(27,79,220,0.25)' : undefined,
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>
        <div style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {filtered.map((c, i) => <CommCard key={c.comm_id || i} c={c} i={i} />)}
        </div>
      </div>
    </div>
  );
}
