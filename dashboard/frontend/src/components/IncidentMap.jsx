import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect, useRef, useState, useMemo } from 'react';
import { API_BASE } from '../config';

const CENTER   = [27.95, -82.45];
const ZOOM     = 11;
const SEV_COLOR = { critical: '#DC2626', high: '#D97706', moderate: '#CA8A04', low: '#16A34A' };

function getSev(score) {
  if (score >= 9) return 'critical';
  if (score >= 7) return 'high';
  if (score >= 5) return 'moderate';
  return 'low';
}
function pct(occ, cap)  { return cap > 0 ? Math.round((occ / cap) * 100) : 0; }
function fillCls(p)     { return p >= 90 ? 'fill-danger' : p >= 70 ? 'fill-warning' : 'fill-success'; }
function pctColor(p)    { return p >= 90 ? '#DC2626' : p >= 70 ? '#D97706' : '#16A34A'; }

/* Pre-compute stable fallback offsets so pins don't jump on re-render */
const OFFSETS = Array.from({ length: 60 }, () => [
  (Math.random() - 0.5) * 0.13,
  (Math.random() - 0.5) * 0.13,
]);

export default function IncidentMap() {
  const mapDivRef    = useRef(null);
  const mapRef       = useRef(null);
  const markersRef   = useRef([]);
  const [incidents, setIncidents] = useState([]);
  const [shelters,  setShelters]  = useState([]);
  const [filter,    setFilter]    = useState('all');
  const [backendOk, setBackendOk] = useState(false);

  /* ── Init Leaflet map once ── */
  useEffect(() => {
    if (mapRef.current || !mapDivRef.current) return;

    mapRef.current = L.map(mapDivRef.current, {
      center: CENTER,
      zoom: ZOOM,
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapRef.current);

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  /* ── Fetch data ── */
  useEffect(() => {
    const go = () => {
      Promise.all([
        fetch(`${API_BASE}/api/incidents`).then(r => r.json()),
        fetch(`${API_BASE}/api/shelters`).then(r => r.json()),
      ])
        .then(([inc, sh]) => { setIncidents(inc); setShelters(sh); setBackendOk(true); })
        .catch(() => setBackendOk(false));
    };
    go();
    const id = setInterval(go, 10000);
    return () => clearInterval(id);
  }, []);

  /* ── Draw markers whenever data or filter changes ── */
  const filtered = useMemo(() => {
    if (filter === 'all') return incidents;
    return incidents.filter(inc => getSev(inc.severity_score ?? 0) === filter);
  }, [incidents, filter]);

  useEffect(() => {
    if (!mapRef.current) return;

    /* Remove old markers */
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    /* Shelter circles */
    shelters.forEach(sh => {
      if (!sh.lat || !sh.lon) return;
      const p = pct(sh.current_occupancy, sh.capacity);
      const bar = `<div style="height:4px;background:#EEF1F8;border-radius:3px;overflow:hidden;margin-top:6px">
        <div style="height:100%;width:${p}%;background:${pctColor(p)};border-radius:3px"></div></div>`;
      const m = L.circleMarker([sh.lat, sh.lon], {
        color: '#1B4FDC', weight: 2,
        fillColor: '#1B4FDC', fillOpacity: 0.15, radius: 9,
      }).bindPopup(`
        <div style="padding:10px;min-width:180px;font-family:Inter,sans-serif">
          <b style="font-size:13px;color:#0F1733">🏫 ${sh.name}</b>
          <div style="font-size:12px;color:#4A5568;margin-top:5px">${sh.current_occupancy} / ${sh.capacity} beds</div>
          ${bar}
          <div style="font-size:11px;color:${pctColor(p)};margin-top:4px;font-weight:600">${p}% occupied</div>
        </div>`
      ).addTo(mapRef.current);
      markersRef.current.push(m);
    });

    /* Incident pins */
    filtered.forEach((inc, i) => {
      const sev   = getSev(inc.severity_score ?? 0);
      const color = SEV_COLOR[sev];
      const off   = OFFSETS[i % OFFSETS.length];
      const lat   = inc.lat  ? inc.lat  : CENTER[0] + off[0];
      const lon   = inc.lon  ? inc.lon  : CENTER[1] + off[1];
      const label = sev.charAt(0).toUpperCase() + sev.slice(1);
      const ts    = inc.timestamp ? new Date(inc.timestamp).toLocaleTimeString('en-US', { hour12: false }) : '';

      const m = L.circleMarker([lat, lon], {
        color, weight: 2.5, fillColor: color, fillOpacity: 0.8, radius: 10,
      }).bindPopup(`
        <div style="padding:10px;min-width:200px;font-family:Inter,sans-serif">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
            <span style="padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;
              background:${color}18;color:${color};border:1px solid ${color}30">${label}</span>
            <span style="font-size:11px;color:#9DAABF">${ts}</span>
          </div>
          <div style="font-size:12.5px;color:#4A5568;line-height:1.5">
            ${inc.raw_report ? inc.raw_report.slice(0, 130) + '…' : '—'}
          </div>
          <div style="margin-top:6px;font-size:11px;color:#9DAABF">
            Score: ${inc.severity_score ?? '—'}/10 · ${inc.parallel_branch_triggered ? '5 agents activated' : '3 agents activated'}
          </div>
        </div>`
      ).addTo(mapRef.current);
      markersRef.current.push(m);
    });
  }, [filtered, shelters]);

  const counts = useMemo(() => ({
    total:    incidents.length,
    critical: incidents.filter(i => getSev(i.severity_score ?? 0) === 'critical').length,
    high:     incidents.filter(i => getSev(i.severity_score ?? 0) === 'high').length,
    shelters: shelters.filter(s => s.status !== 'closed').length,
  }), [incidents, shelters]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

      {/* Offline banner */}
      {!backendOk && (
        <div style={{
          background: 'rgba(220,38,38,0.06)', border: '1px solid rgba(220,38,38,0.18)',
          borderRadius: 9, padding: '10px 16px',
          display: 'flex', alignItems: 'center', gap: 12,
        }}>
          <span style={{ fontSize: 18 }}>⚠️</span>
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: '#DC2626', marginBottom: 2 }}>Backend offline — no data</p>
            <p style={{ fontSize: 12, color: '#9DAABF' }}>
              Run in <b>safehaven/</b>:{' '}
              <code style={{ background: '#F4F6FB', border: '1px solid #E5E9F2', padding: '1px 6px', borderRadius: 4, fontFamily: 'monospace', fontSize: 11.5 }}>
                uvicorn dashboard.api:app --reload --port 8000
              </code>
            </p>
          </div>
        </div>
      )}

      {/* Stats strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 }}>
        {[
          { label: 'Total Incidents', value: counts.total,    color: '#1B4FDC', bg: 'rgba(27,79,220,0.07)'  },
          { label: 'Critical',        value: counts.critical, color: '#DC2626', bg: 'rgba(220,38,38,0.07)'  },
          { label: 'High Severity',   value: counts.high,     color: '#D97706', bg: 'rgba(217,119,6,0.07)'  },
          { label: 'Active Shelters', value: counts.shelters, color: '#16A34A', bg: 'rgba(22,163,74,0.07)'  },
        ].map(s => (
          <div key={s.label} style={{
            background: s.bg, border: `1px solid ${s.color}28`, borderRadius: 10, padding: '11px 14px',
          }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: s.color, lineHeight: 1 }}>{s.value}</div>
            <div style={{ fontSize: 11, color: '#9DAABF', marginTop: 4, fontWeight: 500 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Map card */}
      <div className="card" style={{ overflow: 'hidden' }}>
        {/* Header + filter */}
        <div className="card-header">
          <span className="card-title">Active Incidents Map</span>
          <div style={{ display: 'flex', gap: 5 }}>
            {['all', 'critical', 'high', 'moderate', 'low'].map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className="btn btn-ghost"
                style={{
                  padding: '3px 10px', fontSize: 11.5,
                  background: filter === f ? 'rgba(27,79,220,0.08)' : undefined,
                  color: filter === f ? '#1B4FDC' : undefined,
                  borderColor: filter === f ? 'rgba(27,79,220,0.25)' : undefined,
                }}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', height: 430 }}>
          {/* Map container */}
          <div style={{ flex: 1, position: 'relative' }}>
            <div ref={mapDivRef} style={{ height: '100%', width: '100%' }} />
          </div>

          {/* Right panel */}
          <div style={{ width: 210, flexShrink: 0, borderLeft: '1px solid #E5E9F2', display: 'flex', flexDirection: 'column' }}>
            {/* Quick info */}
            <div style={{ padding: '12px 14px', borderBottom: '1px solid #E5E9F2' }}>
              <div style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#9DAABF', marginBottom: 8 }}>
                Quick Info
              </div>
              {[
                { label: 'Most affected', value: 'Bayport Coast'  },
                { label: 'Total alerts',  value: counts.total     },
                { label: 'Critical',      value: counts.critical   },
                { label: 'High',          value: counts.high       },
              ].map(r => (
                <div key={r.label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 5 }}>
                  <span style={{ color: '#9DAABF' }}>{r.label}</span>
                  <span style={{ fontWeight: 600, color: '#1B4FDC' }}>{r.value}</span>
                </div>
              ))}
            </div>

            {/* Legend */}
            <div style={{ padding: '12px 14px', borderBottom: '1px solid #E5E9F2' }}>
              <div style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#9DAABF', marginBottom: 8 }}>
                Legend
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {[
                  { color: '#DC2626', label: 'Critical' },
                  { color: '#D97706', label: 'High'     },
                  { color: '#CA8A04', label: 'Moderate' },
                  { color: '#16A34A', label: 'Low'      },
                ].map(l => (
                  <div key={l.label} className="legend-item">
                    <span className="legend-dot" style={{ background: l.color }} />
                    {l.label} Incident
                  </div>
                ))}
                <div style={{ height: 1, background: '#E5E9F2', margin: '3px 0' }} />
                <div className="legend-item">
                  <span style={{
                    width: 10, height: 10, border: '2px solid #1B4FDC',
                    background: 'rgba(27,79,220,0.15)', borderRadius: '50%',
                    display: 'inline-block', flexShrink: 0,
                  }} />
                  Active Shelter
                </div>
              </div>
            </div>

            {/* Shelter list */}
            {shelters.length > 0 && (
              <div style={{ padding: '12px 14px', flex: 1, overflowY: 'auto' }}>
                <div style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#9DAABF', marginBottom: 8 }}>
                  Top Shelters
                </div>
                {shelters.slice(0, 5).map(sh => {
                  const p = pct(sh.current_occupancy, sh.capacity);
                  return (
                    <div key={sh.id} style={{ marginBottom: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 3 }}>
                        <span style={{ color: '#4A5568', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 120 }} title={sh.name}>
                          {sh.name}
                        </span>
                        <span style={{ fontWeight: 700, color: pctColor(p), flexShrink: 0, fontFamily: '"JetBrains Mono", monospace' }}>
                          {p}%
                        </span>
                      </div>
                      <div className="track" style={{ height: 3 }}>
                        <div className={`fill ${fillCls(p)}`} style={{ width: `${p}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
