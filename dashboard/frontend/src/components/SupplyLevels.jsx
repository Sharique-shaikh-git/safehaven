import { useState, useEffect } from 'react';
import { Droplets, Utensils, Heart, BedDouble, Package } from 'lucide-react';
import { API_BASE } from '../config';

const ITEMS = [
  { key: 'water_liters', label: 'Water',   unit: 'L',     Icon: Droplets,  color: '#0369A1', bg: 'rgba(3,105,161,0.08)',   border: 'rgba(3,105,161,0.15)'   },
  { key: 'food_meals',   label: 'Food',    unit: 'meals', Icon: Utensils,  color: '#B45309', bg: 'rgba(180,83,9,0.08)',    border: 'rgba(180,83,9,0.15)'    },
  { key: 'medical_kits', label: 'Medical', unit: 'kits',  Icon: Heart,     color: '#DC2626', bg: 'rgba(220,38,38,0.08)',   border: 'rgba(220,38,38,0.15)'   },
  { key: 'blankets',     label: 'Blankets',unit: '',      Icon: BedDouble, color: '#7C3AED', bg: 'rgba(124,58,237,0.08)',  border: 'rgba(124,58,237,0.15)'  },
  { key: 'cots',         label: 'Cots',    unit: '',      Icon: Package,   color: '#0F766E', bg: 'rgba(15,118,110,0.08)',  border: 'rgba(15,118,110,0.15)'  },
];

function CountUp({ target }) {
  const [v, setV] = useState(0);
  useEffect(() => {
    if (!target) { setV(0); return; }
    let cur = 0;
    const step = target / 30;
    const id = setInterval(() => {
      cur = Math.min(cur + step, target);
      setV(Math.round(cur));
      if (cur >= target) clearInterval(id);
    }, 28);
    return () => clearInterval(id);
  }, [target]);
  return <>{v.toLocaleString()}</>;
}

export default function SupplyLevels() {
  const [supplies, setSupplies] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/supplies`).then(r => r.json()).then(setSupplies).catch(() => {});
  }, []);

  const totals = supplies.reduce((acc, s) => {
    ITEMS.forEach(({ key }) => { acc[key] = (acc[key] || 0) + (s[key] || 0); });
    return acc;
  }, {});

  return (
    <div className="card anim-fade-in" style={{ height: '100%' }}>
      <div className="card-header">
        <span className="card-title">Supply Inventory</span>
        <span style={{ fontSize: 11, color: '#9DAABF' }}>{supplies.length} locations</span>
      </div>
      <div style={{ padding: '12px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        {ITEMS.map(({ key, label, unit, Icon, color, bg, border }, i) => (
          <div
            key={key}
            className="anim-fade-up"
            style={{
              padding: '12px', borderRadius: 10,
              background: bg, border: `1px solid ${border}`,
              display: 'flex', alignItems: 'center', gap: 11,
              animationDelay: `${i * 0.05}s`,
              transition: 'box-shadow 0.18s',
              cursor: 'default',
            }}
            onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)'; }}
            onMouseLeave={e => { e.currentTarget.style.boxShadow = 'none'; }}
          >
            <div style={{
              width: 36, height: 36, borderRadius: 10, flexShrink: 0,
              background: '#fff', border: `1px solid ${border}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            }}>
              <Icon size={16} color={color} />
            </div>
            <div>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#0F1733', lineHeight: 1.1, fontVariantNumeric: 'tabular-nums' }}>
                <CountUp target={totals[key] || 0} />
              </div>
              <div style={{ fontSize: 11, color: '#9DAABF', marginTop: 2, fontWeight: 500 }}>
                {label}{unit ? ` (${unit})` : ''}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
