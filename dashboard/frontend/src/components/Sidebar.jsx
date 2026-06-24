import { useState } from 'react';
import {
  LayoutDashboard, AlertTriangle, Package, Users,
  Radio, Shield, LogOut, Settings, Map, X,
  Key, Server, CheckCircle, ClipboardList
} from 'lucide-react';

const NAV = [
  { key: 'dashboard',  label: 'Dashboard',     Icon: LayoutDashboard },
  { key: 'map',        label: 'Incident Map',   Icon: Map             },
  { key: 'incidents',  label: 'Incident Mgmt.', Icon: AlertTriangle   },
  { key: 'resources',  label: 'Resources',      Icon: Package         },
  { key: 'volunteers', label: 'Volunteers',     Icon: Users           },
  { key: 'comms',      label: 'Communications', Icon: Radio           },
  { key: 'audit',      label: 'Audit Log',      Icon: ClipboardList   },
];


/* ── Settings modal ── */
function SettingsModal({ onClose }) {
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'rgba(15,23,51,0.45)', backdropFilter: 'blur(4px)',
    }} onClick={onClose}>
      <div
        style={{
          background: '#fff', borderRadius: 14, width: 440, maxWidth: '90vw',
          boxShadow: '0 24px 60px rgba(15,23,51,0.18)',
          animation: 'fadeUp 0.2s cubic-bezier(0.23,1,0.32,1) both',
          overflow: 'hidden',
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '16px 20px', borderBottom: '1px solid #E5E9F2', background: '#F8F9FC',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Settings size={16} color="#1B4FDC" />
            <span style={{ fontSize: 14, fontWeight: 700, color: '#0F1733' }}>System Settings</span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9DAABF', display: 'flex' }}>
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: 14 }}>

          {/* API Status */}
          <div>
            <p style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#9DAABF', marginBottom: 8 }}>
              Connections
            </p>
            {[
              { icon: Server,  label: 'FastAPI Backend',      val: 'http://127.0.0.1:8000', ok: true  },
              { icon: Server,  label: 'Vite Dev Server',      val: 'http://localhost:5173',  ok: true  },
            ].map(r => (
              <div key={r.label} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '9px 12px', borderRadius: 8,
                background: '#F8F9FC', border: '1px solid #E5E9F2', marginBottom: 6,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <r.icon size={13} color="#9DAABF" />
                  <span style={{ fontSize: 12.5, color: '#4A5568', fontWeight: 500 }}>{r.label}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontSize: 11, fontFamily: '"JetBrains Mono", monospace', color: '#9DAABF' }}>{r.val}</span>
                  <CheckCircle size={13} color={r.ok ? '#16A34A' : '#DC2626'} />
                </div>
              </div>
            ))}
          </div>

          {/* API Keys */}
          <div>
            <p style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#9DAABF', marginBottom: 8 }}>
              API Keys (from .env)
            </p>
            {[
              { icon: Key, label: 'Gemini API Key',     val: 'AIza••••••••••••••••••••' },
              { icon: Key, label: 'OpenWeather API Key', val: '••••••••••••••••••••••••' },
              { icon: Key, label: 'Google Maps Key',    val: '••••••••••••••••••••••••' },
            ].map(r => (
              <div key={r.label} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '9px 12px', borderRadius: 8,
                background: '#F8F9FC', border: '1px solid #E5E9F2', marginBottom: 6,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <r.icon size={13} color="#9DAABF" />
                  <span style={{ fontSize: 12.5, color: '#4A5568', fontWeight: 500 }}>{r.label}</span>
                </div>
                <span style={{ fontSize: 11.5, fontFamily: '"JetBrains Mono", monospace', color: '#9DAABF' }}>{r.val}</span>
              </div>
            ))}
          </div>

          {/* System info */}
          <div>
            <p style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#9DAABF', marginBottom: 8 }}>
              System Info
            </p>
            <div style={{
              padding: '10px 12px', borderRadius: 8,
              background: 'rgba(27,79,220,0.05)', border: '1px solid rgba(27,79,220,0.14)',
            }}>
              {[
                { label: 'Framework',   val: 'Google ADK + Gemini 2.0 Flash' },
                { label: 'Agents',      val: '5 — Intake, Crisis, Resource, Volunteer, Comms' },
                { label: 'MCP Servers', val: '4 — Weather, Geocoding, Supply DB, Shelter API' },
                { label: 'Track',       val: 'Agents for Good · Kaggle 2026' },
              ].map(r => (
                <div key={r.label} style={{ display: 'flex', gap: 10, marginBottom: 5 }}>
                  <span style={{ fontSize: 12, color: '#9DAABF', flexShrink: 0, minWidth: 90 }}>{r.label}</span>
                  <span style={{ fontSize: 12, color: '#4A5568', fontWeight: 500 }}>{r.val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ padding: '12px 20px', borderTop: '1px solid #E5E9F2', background: '#F8F9FC', display: 'flex', justifyContent: 'flex-end' }}>
          <button onClick={onClose} className="btn btn-primary" style={{ padding: '7px 20px' }}>Close</button>
        </div>
      </div>
    </div>
  );
}

/* ── Logout modal ── */
function LogoutModal({ onClose }) {
  const [done, setDone] = useState(false);

  if (done) {
    return (
      <div style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'rgba(15,23,51,0.45)', backdropFilter: 'blur(4px)',
      }}>
        <div style={{
          background: '#fff', borderRadius: 14, padding: '40px 32px', textAlign: 'center',
          boxShadow: '0 24px 60px rgba(15,23,51,0.18)', animation: 'fadeUp 0.2s both',
        }}>
          <CheckCircle size={40} color="#16A34A" style={{ marginBottom: 14 }} />
          <p style={{ fontSize: 15, fontWeight: 700, color: '#0F1733', marginBottom: 6 }}>Session ended</p>
          <p style={{ fontSize: 13, color: '#9DAABF' }}>Refresh the page to start a new session.</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'rgba(15,23,51,0.45)', backdropFilter: 'blur(4px)',
    }} onClick={onClose}>
      <div
        style={{
          background: '#fff', borderRadius: 14, width: 360, maxWidth: '90vw',
          boxShadow: '0 24px 60px rgba(15,23,51,0.18)',
          animation: 'fadeUp 0.2s cubic-bezier(0.23,1,0.32,1) both',
          overflow: 'hidden',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ padding: '28px 24px', textAlign: 'center' }}>
          <div style={{
            width: 52, height: 52, borderRadius: 14,
            background: 'rgba(220,38,38,0.08)', border: '1px solid rgba(220,38,38,0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px',
          }}>
            <LogOut size={22} color="#DC2626" />
          </div>
          <p style={{ fontSize: 15, fontWeight: 700, color: '#0F1733', marginBottom: 6 }}>Sign out?</p>
          <p style={{ fontSize: 13, color: '#9DAABF', lineHeight: 1.5 }}>
            You'll need to log back in to access the SafeHaven Command Center.
          </p>
        </div>
        <div style={{
          display: 'flex', gap: 10, padding: '0 24px 24px',
        }}>
          <button onClick={onClose} className="btn btn-ghost" style={{ flex: 1 }}>Cancel</button>
          <button
            onClick={() => setDone(true)}
            className="btn"
            style={{ flex: 1, background: '#DC2626', color: '#fff', boxShadow: '0 1px 3px rgba(220,38,38,0.35)' }}
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Sidebar ── */
export default function Sidebar({ active, onChange }) {
  const [showSettings, setShowSettings] = useState(false);
  const [showLogout,   setShowLogout]   = useState(false);

  return (
    <>
      <aside className="sidebar">
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <Shield size={16} color="#fff" />
          </div>
          <div>
            <div className="sidebar-logo-text">SafeHaven</div>
            <div style={{ fontSize: 9.5, color: 'rgba(255,255,255,0.45)', fontWeight: 500, marginTop: 1 }}>
              Response Network
            </div>
          </div>
        </div>

        {/* Main nav */}
        <div className="sidebar-section">
          <div className="sidebar-section-label">Navigation</div>
          {NAV.map(({ key, label, Icon }) => (
            <button
              key={key}
              className={`nav-item${active === key ? ' active' : ''}`}
              onClick={() => onChange(key)}
            >
              <Icon size={15} className="nav-icon" />
              {label}
            </button>
          ))}
        </div>

        {/* Bottom */}
        <div className="sidebar-bottom">
          <button className="nav-item" style={{ marginBottom: 4 }} onClick={() => setShowSettings(true)}>
            <Settings size={15} className="nav-icon" />
            Settings
          </button>
          <button className="nav-item" style={{ marginBottom: 6 }} onClick={() => setShowLogout(true)}>
            <LogOut size={15} className="nav-icon" />
            Logout
          </button>
          <div className="sidebar-version">v2.0 · Agents for Good</div>
        </div>
      </aside>

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
      {showLogout   && <LogoutModal   onClose={() => setShowLogout(false)}   />}
    </>
  );
}
