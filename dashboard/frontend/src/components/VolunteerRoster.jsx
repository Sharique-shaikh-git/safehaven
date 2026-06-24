import { useState, useEffect } from 'react';
import { Users } from 'lucide-react';
import { API_BASE } from '../config';

const ST = {
  available:   { label: 'Available',   dotCls: 'dot-green', numColor: '#16A34A', bg: 'rgba(22,163,74,0.07)',   border: 'rgba(22,163,74,0.15)'   },
  on_site:     { label: 'On Site',     dotCls: 'dot-blue',  numColor: '#1B4FDC', bg: 'rgba(27,79,220,0.07)',   border: 'rgba(27,79,220,0.15)'   },
  en_route:    { label: 'En Route',    dotCls: 'dot-amber', numColor: '#D97706', bg: 'rgba(217,119,6,0.07)',   border: 'rgba(217,119,6,0.15)'   },
  unavailable: { label: 'Unavailable', dotCls: 'dot-gray',  numColor: '#9DAABF', bg: 'rgba(0,0,0,0.03)',       border: '#E5E9F2'                 },
};

const SKILL_COLOR = {
  medical: '#DC2626', rescue: '#D97706', first_aid: '#CA8A04',
  logistics: '#0891B2', childcare: '#7C3AED', spanish: '#16A34A',
  translation: '#0F766E', communications: '#0369A1',
};

export default function VolunteerRoster() {
  const [vols, setVols] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/volunteers`).then(r => r.json()).then(setVols).catch(() => {});
  }, []);

  const counts = Object.fromEntries(
    Object.keys(ST).map(s => [s, vols.filter(v => v.status === s).length])
  );

  return (
    <div className="card anim-fade-in" style={{ height: '100%' }}>
      <div className="card-header">
        <span className="card-title">Volunteers</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          <Users size={13} color="#9DAABF" />
          <span style={{ fontSize: 12, color: '#9DAABF', fontWeight: 500 }}>{vols.length} registered</span>
        </div>
      </div>

      {/* Status summary grid */}
      <div style={{ padding: '12px 14px', borderBottom: '1px solid #E5E9F2', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        {Object.entries(ST).map(([status, cfg]) => (
          <div key={status} style={{
            padding: '8px 12px', borderRadius: 9,
            background: cfg.bg, border: `1px solid ${cfg.border}`,
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span className={`dot ${cfg.dotCls}`} />
              <span style={{ fontSize: 12, color: '#4A5568', fontWeight: 500 }}>{cfg.label}</span>
            </div>
            <span style={{ fontSize: 20, fontWeight: 700, color: cfg.numColor, lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>
              {counts[status]}
            </span>
          </div>
        ))}
      </div>

      {/* Volunteer list */}
      <div style={{ overflowY: 'auto', maxHeight: 260 }}>
        {vols.map((vol, i) => {
          const cfg = ST[vol.status] || ST.unavailable;
          return (
            <div
              key={vol.id}
              className="anim-fade-up"
              style={{
                padding: '8px 14px',
                borderBottom: i < vols.length - 1 ? '1px solid #F4F6FB' : 'none',
                display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8,
                transition: 'background 0.15s',
                animationDelay: `${i * 0.025}s`,
              }}
              onMouseEnter={e => { e.currentTarget.style.background = '#F8F9FC'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, minWidth: 0 }}>
                <span className={`dot ${cfg.dotCls}`} style={{ marginTop: 4 }} />
                <div style={{ minWidth: 0 }}>
                  <span style={{ fontSize: 12, fontFamily: '"JetBrains Mono", monospace', color: '#4A5568', fontWeight: 500 }}>
                    {vol.id}
                  </span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 3, marginTop: 4 }}>
                    {vol.skills?.map(sk => {
                      const c = SKILL_COLOR[sk] || '#9DAABF';
                      return (
                        <span key={sk} style={{
                          fontSize: 10, fontWeight: 600, padding: '1px 6px', borderRadius: 4,
                          background: `${c}12`, border: `1px solid ${c}25`, color: c,
                        }}>
                          {sk}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>
              <span style={{ fontSize: 11, color: '#9DAABF', flexShrink: 0, fontFamily: '"JetBrains Mono", monospace' }}>
                {vol.hours_logged}h
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
