import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { Dashboard } from './pages/Dashboard';
import { Payments } from './pages/Payments';
import { RecoveryCases } from './pages/RecoveryCases';
import { RecoveryCaseDetails } from './pages/RecoveryCaseDetails';
import { Analytics } from './pages/Analytics';
import { AuditTrail } from './pages/AuditTrail';
import { analyticsApi } from './api';
import { HealthStatus } from './types';

const AppLayout: React.FC = () => {
  const location = useLocation();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const checkHealth = async () => {
    try {
      const data = await analyticsApi.getHealth();
      setHealth(data);
    } catch {
      setHealth(null);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getPageHeader = () => {
    const p = location.pathname;
    if (p === '/' || p === '/dashboard') {
      return {
        title: 'Payment Revenue Recovery',
        subtitle: 'Identify at-risk revenue, determine what is recoverable, and choose the safest next action.',
      };
    }
    if (p.startsWith('/recovery/')) {
      return {
        title: 'Recovery Investigation',
        subtitle: 'AI recommendations, deterministic policy validation, and simulated recovery',
      };
    }
    if (p === '/recovery') {
      return {
        title: 'Recovery Cases',
        subtitle: 'AI recommendations and recovery execution',
      };
    }
    if (p === '/payments') {
      return {
        title: 'Payments',
        subtitle: 'Payment history, failure signals, and recovery status',
      };
    }
    if (p === '/analytics') {
      return {
        title: 'Analytics',
        subtitle: 'Recovery performance and strategy ROI',
      };
    }
    if (p === '/audit') {
      return {
        title: 'Audit Trail',
        subtitle: 'Trace every AI recommendation, policy decision, and recovery action.',
      };
    }
    return {
      title: 'RecoverAI',
      subtitle: 'AI Revenue Recovery',
    };
  };

  const headerInfo = getPageHeader();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-900 antialiased selection:bg-blue-600 selection:text-white">
      {/* Navigation Sidebar */}
      <Sidebar apiConnected={health?.status === 'ok'} />

      {/* Main Content Workspace */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <Header
          title={headerInfo.title}
          subtitle={headerInfo.subtitle}
          health={health}
          onRefresh={() => setRefreshKey((prev) => prev + 1)}
        />
        <main className="flex-1 pb-16" key={refreshKey}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/recovery" element={<RecoveryCases />} />
            <Route path="/recovery/:caseId" element={<RecoveryCaseDetails />} />
            <Route path="/payments" element={<Payments />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/audit" element={<AuditTrail />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
};

export default App;
