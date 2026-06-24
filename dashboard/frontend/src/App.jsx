import { useState } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import AgentStatus from './components/AgentStatus';
import SubmitIncident from './components/SubmitIncident';
import IncidentTable from './components/IncidentTable';
import IncidentMap from './components/IncidentMap';
import ShelterCapacity from './components/ShelterCapacity';
import SupplyLevels from './components/SupplyLevels';
import VolunteerRoster from './components/VolunteerRoster';
import CommunicationsPage from './components/CommunicationsPage';
import AuditLog from './components/AuditLog';

const PAGE_META = {
  dashboard:  { title: 'Command Center'        },
  map:        { title: 'Incident Map'           },
  incidents:  { title: 'Incident Management'   },
  resources:  { title: 'Resource Monitor'      },
  volunteers: { title: 'Volunteer Roster'      },
  comms:      { title: 'Communications Hub'    },
  audit:      { title: 'Audit Log'             },
};

/* ── PAGES ─────────────────────────────────────── */

function DashboardPage() {
  return (
    <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
      <div style={{ width: 280, flexShrink: 0 }}>
        <AgentStatus />
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16, minWidth: 0 }}>
        <SubmitIncident />
        <IncidentTable />
      </div>
    </div>
  );
}

function ResourcesPage() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, alignItems: 'flex-start' }}>
      <ShelterCapacity />
      <SupplyLevels />
    </div>
  );
}

const PAGES = {
  dashboard:  DashboardPage,
  map:        () => <IncidentMap />,
  incidents:  () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <SubmitIncident />
      <IncidentTable />
    </div>
  ),
  resources:  ResourcesPage,
  volunteers: () => <div style={{ maxWidth: 720 }}><VolunteerRoster /></div>,
  comms:      () => <CommunicationsPage />,
  audit:      () => <AuditLog />,
};

/* ── APP ────────────────────────────────────────── */
export default function App() {
  const [page, setPage] = useState('dashboard');
  const PageComponent = PAGES[page] || DashboardPage;
  const meta = PAGE_META[page] || PAGE_META.dashboard;

  return (
    <>
      <Sidebar active={page} onChange={setPage} />

      <div className="main-area">
        <TopBar title={meta.title} />

        <div className="content">
          <PageComponent />
        </div>

        <footer style={{
          height: 32, borderTop: '1px solid #E5E9F2',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 20px', background: '#fff', flexShrink: 0,
        }}>
          <span style={{ fontSize: 11, color: '#9DAABF' }}>
            SafeHaven · Agents for Good · Kaggle 2026
          </span>
          <span style={{ fontSize: 11, color: '#9DAABF' }}>
            Gemini 2.0 Flash · Google ADK · 5 Agents · 4 MCP Servers
          </span>
        </footer>
      </div>
    </>
  );
}
