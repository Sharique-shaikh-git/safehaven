import { useState } from 'react';
import {
  Send, Loader2, CheckCircle2, AlertTriangle,
  FileInput, Zap, Package, Users, Radio, ChevronRight, ChevronDown
} from 'lucide-react';
import { API_BASE } from '../config';

const STEPS = [
  { key: 'intake',    label: 'Intake',    Icon: FileInput },
  { key: 'crisis',    label: 'Crisis',    Icon: Zap       },
  { key: 'resources', label: 'Resources', Icon: Package   },
  { key: 'volunteers',label: 'Volunteers',Icon: Users     },
  { key: 'comms',     label: 'Comms',     Icon: Radio     },
];

const FIELDS = [
  { key: 'intake',               label: 'Intake Agent',       Icon: FileInput },
  { key: 'crisis_assessment',    label: 'Crisis Assessment',  Icon: Zap       },
  { key: 'resource_allocation',  label: 'Resource Allocation',Icon: Package   },
  { key: 'volunteer_dispatch',   label: 'Volunteer Dispatch', Icon: Users     },
  { key: 'communications',       label: 'Communications',     Icon: Radio     },
];

const EXAMPLES = [
  'Hurricane Mara hit Bayport. 4 families trapped on roof at 1200 Ocean Dr — elderly residents need immediate medical help and shelter.',
  'Gas explosion at downtown market. 12 injured, 3 critical burns. Structure unstable — need evacuation support and medical triage.',
  'Wildfire approaching Pinecrest, 200 homes threatened. Need evacuation buses and emergency shelter coordination immediately.',
];

function SevBadge({ score }) {
  if (score == null) return null;
  const cls = score >= 9 ? 'badge-critical' : score >= 7 ? 'badge-high' : score >= 5 ? 'badge-moderate' : 'badge-low';
  const lbl = score >= 9 ? 'Critical' : score >= 7 ? 'High' : score >= 5 ? 'Moderate' : 'Low';
  return <span className={`badge ${cls}`}>{score}/10 · {lbl}</span>;
}

export default function SubmitIncident() {
  const [text, setText]  = useState('');
  const [busy, setBusy]  = useState(false);
  const [step, setStep]  = useState(-1);
  const [result, setRes] = useState(null);
  const [err, setErr]    = useState(null);
  const [open, setOpen]  = useState({});

  const submit = async () => {
    if (!text.trim() || busy) return;
    setBusy(true); setErr(null); setRes(null); setStep(0); setOpen({});

    const t = setInterval(() => {
      setStep(p => {
        if (p >= STEPS.length - 1) { clearInterval(t); return p; }
        return p + 1;
      });
    }, 1700);

    try {
      const res  = await fetch(`${API_BASE}/api/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_report: text }),
      });
      const data = await res.json();
      clearInterval(t);
      if (!res.ok) throw new Error(data.detail || 'Pipeline failed');
      setStep(STEPS.length);
      setRes(data);
      setText('');
    } catch (e) {
      clearInterval(t);
      setErr(e.message);
      setStep(-1);
    } finally {
      setBusy(false);
    }
  };

  const tog = k => setOpen(o => ({ ...o, [k]: !o[k] }));

  return (
    <div className="card anim-fade-in">
      <div className="card-header">
        <div>
          <span className="card-title">Submit Incident Report</span>
          <p style={{ fontSize: 12, color: '#9DAABF', marginTop: 2, fontWeight: 400, textTransform: 'none', letterSpacing: 'normal' }}>
            Activates the 5-agent AI coordination pipeline
          </p>
        </div>
      </div>

      <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {/* Example buttons */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 11.5, color: '#9DAABF', alignSelf: 'center', marginRight: 2 }}>Load example:</span>
          {EXAMPLES.map((ex, i) => (
            <button key={i} onClick={() => setText(ex)} disabled={busy} className="btn btn-ghost">
              Example {i + 1}
            </button>
          ))}
        </div>

        {/* Textarea + button */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Describe the disaster — location, people affected, immediate needs…"
            disabled={busy}
            rows={4}
            className="field"
          />
          <button
            onClick={submit}
            disabled={!text.trim() || busy}
            className="btn btn-primary"
            style={{ alignSelf: 'flex-end', padding: '9px 18px' }}
          >
            {busy ? <Loader2 size={14} className="anim-spin" /> : <Send size={14} />}
            {busy ? 'Running…' : 'Deploy'}
          </button>
        </div>

        {/* Pipeline progress */}
        {busy && (
          <div className="anim-fade-in" style={{
            background: '#F8F9FC', border: '1px solid #E5E9F2',
            borderRadius: 10, padding: '11px 14px',
          }}>
            <p style={{ fontSize: 10.5, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#9DAABF', marginBottom: 10 }}>
              Pipeline executing
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 5 }}>
              {STEPS.map((s, i) => {
                const done = i < step, active = i === step;
                const I = s.Icon;
                return (
                  <div key={s.key} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <div className={`step ${done ? 'step-done' : active ? 'step-active' : 'step-pending'}`}>
                      {done ? <CheckCircle2 size={11} /> : active ? <Loader2 size={11} className="anim-spin" /> : <I size={11} />}
                      {s.label}
                    </div>
                    {i < STEPS.length - 1 && (
                      <ChevronRight size={12} color={done ? '#1B4FDC' : '#CBD5E0'} />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Error */}
        {err && (
          <div className="anim-fade-in" style={{
            background: 'rgba(220,38,38,0.05)', border: '1px solid rgba(220,38,38,0.2)',
            borderRadius: 10, padding: '11px 14px', display: 'flex', gap: 10, alignItems: 'flex-start',
          }}>
            <AlertTriangle size={14} color="#DC2626" style={{ flexShrink: 0, marginTop: 1 }} />
            <div>
              <p style={{ fontSize: 12.5, fontWeight: 600, color: '#DC2626', marginBottom: 2 }}>Pipeline error</p>
              <p style={{ fontSize: 12, color: '#B91C1C' }}>{err}</p>
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="anim-fade-in" style={{
            background: 'rgba(22,163,74,0.04)', border: '1px solid rgba(22,163,74,0.18)',
            borderRadius: 10, overflow: 'hidden',
          }}>
            {/* Result header */}
            <div style={{
              padding: '10px 14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              borderBottom: '1px solid rgba(22,163,74,0.12)', background: 'rgba(22,163,74,0.05)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                <CheckCircle2 size={14} color="#16A34A" />
                <span style={{ fontSize: 13, fontWeight: 600, color: '#15803D' }}>Pipeline complete</span>
              </div>
              <div style={{ display: 'flex', gap: 7 }}>
                <SevBadge score={result.severity_score} />
                <span className={`badge ${result.parallel_branch_triggered ? 'badge-blue' : 'badge-gray'}`}>
                  {result.parallel_branch_triggered ? '5 agents' : '3 agents'}
                </span>
              </div>
            </div>

            {/* Collapsible agent outputs */}
            <div>
              {FIELDS.filter(f => result[f.key]).map((f, i, arr) => {
                const FI = f.Icon;
                const isOp = open[f.key];
                return (
                  <div key={f.key} style={{ borderBottom: i < arr.length - 1 ? '1px solid #F4F6FB' : 'none' }}>
                    <button
                      onClick={() => tog(f.key)}
                      style={{
                        width: '100%', padding: '9px 14px',
                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left',
                        transition: 'background 0.15s',
                      }}
                      onMouseEnter={e => { e.currentTarget.style.background = '#F8F9FC'; }}
                      onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <FI size={13} color="#9DAABF" />
                        <span style={{ fontSize: 12.5, fontWeight: 600, color: '#4A5568' }}>{f.label}</span>
                      </span>
                      {isOp ? <ChevronDown size={13} color="#9DAABF" /> : <ChevronRight size={13} color="#9DAABF" />}
                    </button>
                    {isOp && (
                      <div style={{ padding: '0 14px 12px' }}>
                        <pre style={{
                          fontFamily: '"JetBrains Mono", monospace',
                          fontSize: 11.5, color: '#4A5568', lineHeight: 1.7,
                          background: '#F8F9FC', border: '1px solid #E5E9F2',
                          borderRadius: 8, padding: '10px 12px',
                          overflowX: 'auto', overflowY: 'auto', maxHeight: 180,
                          whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                        }}>
                          {result[f.key]}
                        </pre>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
