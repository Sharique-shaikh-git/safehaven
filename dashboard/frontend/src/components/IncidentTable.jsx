import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, ArrowUpDown, AlertOctagon, Flame, Minus, CheckCircle } from 'lucide-react';
import { API_BASE } from '../config';

function getSev(score) {
  if (score >= 9) return { cls: 'badge-critical', label: 'Critical', Icon: AlertOctagon };
  if (score >= 7) return { cls: 'badge-high',     label: 'High',     Icon: Flame        };
  if (score >= 5) return { cls: 'badge-moderate', label: 'Moderate', Icon: Minus        };
  return               { cls: 'badge-low',        label: 'Low',      Icon: CheckCircle  };
}

export default function IncidentTable() {
  const [incidents, setIncidents] = useState([]);
  const [sortKey, setKey] = useState('timestamp');
  const [sortDir, setDir] = useState('desc');

  useEffect(() => {
    const go = () => {
      fetch(`${API_BASE}/api/incidents`).then(r => r.json()).then(setIncidents).catch(() => {});
    };
    go();
    const id = setInterval(go, 10000);
    return () => clearInterval(id);
  }, []);

  const handleSort = k => {
    if (sortKey === k) setDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setKey(k); setDir('desc'); }
  };

  const sorted = [...incidents].sort((a, b) => {
    let va = a[sortKey] ?? '', vb = b[sortKey] ?? '';
    if (sortKey === 'severity_score') { va = +va || 0; vb = +vb || 0; }
    return va < vb ? (sortDir === 'asc' ? -1 : 1) : va > vb ? (sortDir === 'asc' ? 1 : -1) : 0;
  });

  const Arrow = ({ col }) => {
    if (sortKey !== col) return <ArrowUpDown size={11} color="#CBD5E0" />;
    return sortDir === 'asc'
      ? <ChevronUp   size={11} color="#1B4FDC" />
      : <ChevronDown size={11} color="#1B4FDC" />;
  };

  if (!incidents.length) {
    return (
      <div className="card anim-fade-in" style={{ padding: '48px 24px', textAlign: 'center' }}>
        <div style={{
          width: 48, height: 48, borderRadius: 14, margin: '0 auto 14px',
          background: 'rgba(27,79,220,0.08)', border: '1px solid rgba(27,79,220,0.15)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Flame size={22} color="#1B4FDC" style={{ opacity: 0.6 }} />
        </div>
        <p style={{ fontSize: 14, color: '#4A5568', fontWeight: 500 }}>No incidents logged yet</p>
        <p style={{ fontSize: 12.5, color: '#9DAABF', marginTop: 4 }}>
          Submit a report in the Command Center to activate the AI pipeline
        </p>
      </div>
    );
  }

  return (
    <div className="card anim-fade-in">
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="card-title">All Incidents</span>
          <span className="badge badge-gray">{incidents.length} total</span>
        </div>
        <span style={{ fontSize: 11, color: '#9DAABF' }}>Auto-refresh · 10 s</span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table className="tbl">
          <thead>
            <tr>
              <th className="sortable" onClick={() => handleSort('timestamp')}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>Time <Arrow col="timestamp" /></span>
              </th>
              <th className="sortable" onClick={() => handleSort('severity_score')}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>Severity <Arrow col="severity_score" /></span>
              </th>
              <th>Report Summary</th>
              <th className="sortable" onClick={() => handleSort('parallel_branch_triggered')}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>Pipeline <Arrow col="parallel_branch_triggered" /></span>
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((inc, i) => {
              const { cls, label, Icon: SIcon } = getSev(inc.severity_score ?? 0);
              return (
                <tr key={i} className="anim-fade-in" style={{ animationDelay: `${i * 0.03}s` }}>
                  <td>
                    <span style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 12, color: '#9DAABF' }}>
                      {inc.timestamp ? new Date(inc.timestamp).toLocaleTimeString('en-US', { hour12: false }) : '—'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${cls}`}>
                      <SIcon size={10} />{inc.severity_score ?? '—'}/10 · {label}
                    </span>
                  </td>
                  <td style={{ maxWidth: 300 }}>
                    <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 12.5 }}>
                      {inc.raw_report ? inc.raw_report.slice(0, 100) + '…' : '—'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${inc.parallel_branch_triggered ? 'badge-blue' : 'badge-gray'}`}>
                      {inc.parallel_branch_triggered ? '5 agents' : '3 agents'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
