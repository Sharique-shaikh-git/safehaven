import { useState, useEffect } from 'react';
import { Building2 } from 'lucide-react';
import { API_BASE } from '../config';

function pct(occ, cap) { return cap > 0 ? Math.round((occ / cap) * 100) : 0; }
function fillCls(p) { return p >= 90 ? 'fill-danger' : p >= 70 ? 'fill-warning' : 'fill-success'; }
function pctColor(p) { return p >= 90 ? '#DC2626' : p >= 70 ? '#D97706' : '#16A34A'; }

export default function ShelterCapacity() {
  const [shelters, setShelters] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/shelters`).then(r => r.json()).then(setShelters).catch(() => {});
  }, []);

  const totalCap = shelters.reduce((s, sh) => s + sh.capacity, 0);
  const totalOcc = shelters.reduce((s, sh) => s + sh.current_occupancy, 0);
  const overall  = pct(totalOcc, totalCap);

  return (
    <div className="card anim-fade-in" style={{ height: '100%' }}>
      <div className="card-header">
        <span className="card-title">Shelter Capacity</span>
        <span style={{
          fontSize: 12, fontWeight: 700,
          color: pctColor(overall),
          fontFamily: '"JetBrains Mono", monospace',
        }}>
          {overall}% utilized
        </span>
      </div>

      {/* Overall summary */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #E5E9F2' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontSize: 12, color: '#9DAABF' }}>All shelters combined</span>
          <span style={{ fontSize: 12, fontWeight: 600, color: '#0F1733', fontFamily: '"JetBrains Mono", monospace' }}>
            {totalOcc.toLocaleString()} / {totalCap.toLocaleString()} beds
          </span>
        </div>
        <div className="track">
          <div className={`fill ${fillCls(overall)}`} style={{ width: `${overall}%` }} />
        </div>
      </div>

      {/* Per-shelter list */}
      <div style={{ overflowY: 'auto', maxHeight: 360 }}>
        {shelters.map((sh, i) => {
          const p = pct(sh.current_occupancy, sh.capacity);
          return (
            <div
              key={sh.id}
              className="anim-fade-up"
              style={{
                padding: '10px 16px',
                borderBottom: i < shelters.length - 1 ? '1px solid #F4F6FB' : 'none',
                transition: 'background 0.15s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = '#F8F9FC'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 5 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, minWidth: 0 }}>
                  <Building2 size={12} color="#9DAABF" style={{ flexShrink: 0 }} />
                  <span style={{
                    fontSize: 12.5, fontWeight: 500, color: '#0F1733',
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }} title={sh.name}>{sh.name}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0, marginLeft: 8 }}>
                  {sh.status === 'full' && (
                    <span className="badge badge-critical" style={{ padding: '1px 5px', fontSize: 10 }}>Full</span>
                  )}
                  {sh.amenities?.includes('medical') && (
                    <span className="badge badge-blue" style={{ padding: '1px 5px', fontSize: 10 }}>Med</span>
                  )}
                  <span style={{
                    fontSize: 12, fontWeight: 700,
                    color: pctColor(p),
                    fontFamily: '"JetBrains Mono", monospace',
                    minWidth: 36, textAlign: 'right',
                  }}>
                    {p}%
                  </span>
                </div>
              </div>
              <div className="track" style={{ height: 4 }}>
                <div className={`fill ${fillCls(p)}`} style={{ width: `${p}%` }} />
              </div>
              <div style={{ fontSize: 11, color: '#9DAABF', marginTop: 3 }}>
                {sh.current_occupancy} / {sh.capacity} beds
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
