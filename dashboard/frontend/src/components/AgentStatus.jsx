import { useState, useEffect } from 'react';
import { AlertTriangle, Package, Users, Radio, FileInput, CheckCircle, Clock, Loader2, XCircle, Zap } from 'lucide-react';
import { API_BASE } from '../config';

const DEFS = [
  { key: 'intake_agent',          label: 'Intake Agent',       Icon: FileInput,     color: '#1B4FDC', bg: 'rgba(27,79,220,0.08)'  },
  { key: 'crisis_assessor',       label: 'Crisis Assessor',    Icon: AlertTriangle, color: '#DC2626', bg: 'rgba(220,38,38,0.08)'  },
  { key: 'resource_allocator',    label: 'Resource Allocator', Icon: Package,       color: '#0891B2', bg: 'rgba(8,145,178,0.08)'  },
  { key: 'volunteer_coordinator', label: 'Volunteer Coord.',   Icon: Users,         color: '#16A34A', bg: 'rgba(22,163,74,0.08)'  },
  { key: 'communication_hub',     label: 'Comms Hub',          Icon: Radio,         color: '#D97706', bg: 'rgba(217,119,6,0.08)'  },
];

const STATUS = {
  idle:       { cls: 'badge-gray',     Icon: Clock,      label: 'Idle'   },
  processing: { cls: 'badge-blue',     Icon: Loader2,    label: 'Active' },
  done:       { cls: 'badge-low',      Icon: CheckCircle,label: 'Done'   },
  error:      { cls: 'badge-critical', Icon: XCircle,    label: 'Error'  },
};

export default function AgentStatus() {
  const [map, setMap] = useState({});

  useEffect(() => {
    const go = () => {
      fetch(`${API_BASE}/api/agents`).then(r => r.json())
        .then(data => { const m = {}; data.forEach(a => { m[a.id] = a; }); setMap(m); })
        .catch(() => {});
    };
    go();
    const id = setInterval(go, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="card" style={{ height: '100%' }}>
      <div className="card-header">
        <span className="card-title">Agent Network</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          <span className="dot dot-pulse" />
          <span style={{ fontSize: 11, color: '#9DAABF' }}>Live · 5s</span>
        </div>
      </div>
      <div style={{ padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {DEFS.map((ag, i) => {
          const data   = map[ag.key] || {};
          const status = data.status || 'idle';
          const s      = STATUS[status] || STATUS.idle;
          const SI     = s.Icon;
          const AG     = ag.Icon;
          const isProc = status === 'processing';

          return (
            <div
              key={ag.key}
              className="agent-card anim-fade-up"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div style={{
                width: 32, height: 32, borderRadius: 9, flexShrink: 0,
                background: ag.bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <AG size={15} color={ag.color} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 12.5, fontWeight: 600, color: '#0F1733' }}>{ag.label}</span>
                  <span className={`badge ${s.cls}`}>
                    <SI size={10} className={isProc ? 'anim-spin' : ''} />
                    {s.label}
                  </span>
                </div>
                {isProc && (
                  <div className="track" style={{ height: 2, marginTop: 6 }}>
                    <div style={{
                      height: '100%', borderRadius: 1,
                      background: `linear-gradient(90deg, transparent, ${ag.color}, transparent)`,
                      width: '60%',
                      animation: 'shimmer 1.8s linear infinite',
                      backgroundSize: '200% 100%',
                    }} />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{
        margin: '0 12px 12px', padding: '7px 10px', borderRadius: 8,
        background: 'rgba(27,79,220,0.05)', border: '1px solid rgba(27,79,220,0.12)',
        display: 'flex', alignItems: 'center', gap: 6,
      }}>
        <Zap size={11} color="#1B4FDC" />
        <span style={{ fontSize: 11, color: '#9DAABF' }}>Gemini 2.0 Flash · Google ADK</span>
      </div>
    </div>
  );
}
