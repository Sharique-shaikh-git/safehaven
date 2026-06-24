import { useState, useEffect } from 'react';
import { ClipboardList, Shield, Zap, Package, Users, Radio, FileInput, ChevronRight } from 'lucide-react';
import { API_BASE } from '../config';

const ACTION_CFG = {
  intake:                { Icon: FileInput,     color: '#1B4FDC', bg: 'rgba(27,79,220,0.08)'  },
  crisis_assessment:     { Icon: Zap,           color: '#DC2626', bg: 'rgba(220,38,38,0.08)'  },
  resource_allocation:   { Icon: Package,       color: '#0891B2', bg: 'rgba(8,145,178,0.08)'  },
  volunteer_dispatch:    { Icon: Users,         color: '#D97706', bg: 'rgba(217,119,6,0.08)'  },
  communication:         { Icon: Radio,         color: '#0F766E', bg: 'rgba(15,118,110,0.08)' },
  pii_redaction:         { Icon: Shield,        color: '#7C3AED', bg: 'rgba(124,58,237,0.08)' },
};

function getCfg(action) {
  for (const [k, v] of Object.entries(ACTION_CFG)) {
    if (action?.toLowerCase().includes(k.split('_')[0])) return v;
  }
  return { Icon: ClipboardList, color: '#9DAABF', bg: 'rgba(0,0,0,0.04)' };
}

export default function AuditLog() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const go = () => {
      fetch(`${API_BASE}/api/audit`)
        .then(r => r.json()).then(d => { setEntries(d); setLoading(false); })
        .catch(() => setLoading(false));
    };
    go();
    const id = setInterval(go, 10000);
    return () => clearInterval(id);
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60 }}>
        <ClipboardList size={28} color="#9DAABF" />
      </div>
    );
  }

  if (!entries.length) {
    return (
      <div className="card" style={{ padding: '60px 24px', textAlign: 'center' }}>
        <div style={{
          width: 52, height: 52, borderRadius: 14, margin: '0 auto 14px',
          background: 'rgba(124,58,237,0.08)', border: '1px solid rgba(124,58,237,0.15)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <ClipboardList size={22} color="#7C3AED" />
        </div>
        <p style={{ fontSize: 14, fontWeight: 500, color: '#4A5568', marginBottom: 5 }}>Audit log is empty</p>
        <p style={{ fontSize: 12.5, color: '#9DAABF' }}>
          Each agent action is logged here as the pipeline processes incidents.
          Submit an incident to populate the audit trail.
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10 }}>
        {[
          { label: 'Total Actions',  value: entries.length,                                                      color: '#7C3AED', bg: 'rgba(124,58,237,0.07)' },
          { label: 'PII Redactions', value: entries.filter(e => e.action?.includes('pii') || e.action?.includes('redact')).length, color: '#DC2626', bg: 'rgba(220,38,38,0.07)' },
          { label: 'Pipeline Runs',  value: entries.filter(e => e.action?.includes('intake') || e.action === 'pipeline_start').length, color: '#1B4FDC', bg: 'rgba(27,79,220,0.07)' },
        ].map(s => (
          <div key={s.label} style={{ background: s.bg, border: `1px solid ${s.color}28`, borderRadius: 10, padding: '11px 14px' }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: s.color, lineHeight: 1 }}>{s.value}</div>
            <div style={{ fontSize: 11, color: '#9DAABF', marginTop: 4, fontWeight: 500 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Log */}
      <div className="card anim-fade-in">
        <div className="card-header">
          <span className="card-title">Audit Trail</span>
          <span style={{ fontSize: 11, color: '#9DAABF' }}>Newest first · append-only</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="tbl">
            <thead>
              <tr>
                <th>Time</th>
                <th>Action</th>
                <th>Actor</th>
                <th>Details</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e, i) => {
                const cfg = getCfg(e.action || e.actor || '');
                const AI  = cfg.Icon;
                const ts  = e.timestamp
                  ? new Date(e.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
                  : '—';
                return (
                  <tr key={i} className="anim-fade-in" style={{ animationDelay: `${i * 0.02}s` }}>
                    <td>
                      <span style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 11.5, color: '#9DAABF' }}>{ts}</span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                        <div style={{
                          width: 26, height: 26, borderRadius: 7, flexShrink: 0,
                          background: cfg.bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}>
                          <AI size={12} color={cfg.color} />
                        </div>
                        <span style={{ fontSize: 12.5, fontWeight: 500, color: '#0F1733' }}>
                          {e.action || '—'}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span style={{ fontSize: 12, fontFamily: '"JetBrains Mono", monospace', color: '#4A5568' }}>
                        {e.actor || '—'}
                      </span>
                    </td>
                    <td style={{ maxWidth: 280 }}>
                      <span style={{ fontSize: 12, color: '#9DAABF', overflow: 'hidden', textOverflow: 'ellipsis', display: 'block', whiteSpace: 'nowrap' }}>
                        {e.details || e.message || '—'}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-gray">{e.role || 'system'}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
