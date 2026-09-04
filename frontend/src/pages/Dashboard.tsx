import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertOctagon,
  TrendingUp,
  CheckCircle2,
  Percent,
  Clock,
  ShieldCheck,
  ShieldAlert,
  Ban,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import { analyticsApi, recoveryApi } from '../api';
import {
  AnalyticsOverview,
  RecoveryTrendPoint,
  ActionBreakdownItem,
  FailureBreakdownItem,
  RecoveryCase,
} from '../types';
import { formatINR, formatPercent } from '../utils/formatters';
import { PageContainer } from '../components/layout/PageContainer';
import { KPICard } from '../components/dashboard/KpiCard';
import { RecoveryFunnel } from '../components/dashboard/RecoveryFunnel';
import { RecoveryTrendChart } from '../components/dashboard/RecoveryTrendChart';
import { FailureBreakdownChart } from '../components/dashboard/FailureBreakdownChart';
import { ActionBreakdownChart } from '../components/dashboard/ActionBreakdownChart';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [trend, setTrend] = useState<RecoveryTrendPoint[]>([]);
  const [actionBreakdown, setActionBreakdown] = useState<ActionBreakdownItem[]>([]);
  const [failureBreakdown, setFailureBreakdown] = useState<FailureBreakdownItem[]>([]);
  const [demoCase, setDemoCase] = useState<RecoveryCase | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [ovData, trData, actData, failData, casesData] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getRecoveryTrend(14),
        analyticsApi.getActionBreakdown(),
        analyticsApi.getFailureBreakdown(),
        recoveryApi.listCases({ limit: 50 }),
      ]);
      setOverview(ovData);
      setTrend(trData);
      setActionBreakdown(actData);
      setFailureBreakdown(failData);

      // Find VIP demo case PAY_10482 if available
      const vip = casesData.find(
        (c) => c.payment?.payment_id === 'PAY_10482' || String(c.payment_id) === 'PAY_10482'
      );
      if (vip) setDemoCase(vip);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to RecoverAI backend');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (isLoading && !overview) {
    return (
      <PageContainer>
        <LoadingState message="Loading RecoverAI Revenue Intelligence..." />
      </PageContainer>
    );
  }

  if (error && !overview) {
    return (
      <PageContainer>
        <ErrorState message={error} onRetry={loadDashboardData} />
      </PageContainer>
    );
  }

  const attemptsTotal = actionBreakdown.reduce((acc, item) => acc + item.attempts, 0) || 127;

  return (
    <PageContainer>
      {/* Top Banner with Core Question & Featured Opportunity */}
      <div className="rounded-xl bg-white border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200">
              <Sparkles className="w-3.5 h-3.5" />
              Recovery Engine Active
            </div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">
              &ldquo;How much revenue can we recover, and what should we do next?&rdquo;
            </h2>
            <p className="text-xs text-slate-600 leading-relaxed">
              Identify at-risk revenue, determine what is recoverable, and choose the safest next action. All recovery workflows are evaluated through deterministic policy before execution.
            </p>
            <p className="text-[11px] text-slate-500 font-medium">
              Note: All recovery actions are simulated. No real financial transactions are executed.
            </p>
          </div>

          {/* Quick Demo Shortcut */}
          {demoCase && (
            <Link
              to={`/recovery/${demoCase.id}`}
              className="flex-shrink-0 p-4 rounded-xl bg-slate-50 border border-blue-200 hover:border-blue-400 hover:bg-blue-50/50 transition-all shadow-sm group text-left max-w-xs"
            >
              <div className="flex items-center justify-between gap-3 mb-1.5">
                <span className="text-[10px] uppercase font-bold text-blue-700 font-mono tracking-wider">
                  RECOVERY OPPORTUNITY
                </span>
                <ArrowRight className="w-3.5 h-3.5 text-blue-600 group-hover:translate-x-1 transition-transform" />
              </div>
              <div className="font-mono font-bold text-sm text-slate-900">PAY_10482 &bull; ₹8,500.00</div>
              <div className="text-[11px] text-slate-600 mt-1">
                98.5% recoverability &bull; Recommended: <strong className="text-blue-700 font-semibold">Retry Later</strong>
              </div>
              <div className="text-[10px] font-semibold text-emerald-700 mt-1 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                Status: {demoCase.status}
              </div>
            </Link>
          )}
        </div>
      </div>

      {/* Primary Financial KPIs (Top 4) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KPICard
          title="Revenue at Risk"
          value={formatINR(overview?.revenue_at_risk, true)}
          secondaryValue={formatINR(overview?.revenue_at_risk, false)}
          subtitle="Failed, expired and abandoned payments"
          badgeText="At Risk"
          icon={AlertOctagon}
          colorScheme="rose"
        />

        <KPICard
          title="Potentially Recoverable"
          value={formatINR(overview?.potentially_recoverable, true)}
          secondaryValue={formatINR(overview?.potentially_recoverable, false)}
          subtitle="ML-estimated recoverable revenue"
          badgeText="Predicted"
          icon={TrendingUp}
          colorScheme="amber"
        />

        <KPICard
          title="Recovered Revenue"
          value={formatINR(overview?.recovered_revenue, true)}
          secondaryValue={formatINR(overview?.recovered_revenue, false)}
          subtitle="Successfully recovered in simulation"
          badgeText="Settled"
          icon={CheckCircle2}
          colorScheme="emerald"
        />

        <KPICard
          title="Recovery Rate"
          value={formatPercent(overview?.recovery_rate)}
          secondaryValue="of Recoverable Pool"
          subtitle="Recovered / potentially recoverable"
          badgeText="Performance"
          icon={Percent}
          colorScheme="sky"
        />
      </div>

      {/* Secondary Operational Counters (4 cards) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm text-left">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-medium">Active Cases</span>
            <Clock className="w-3.5 h-3.5 text-blue-600" />
          </div>
          <div className="text-xl font-mono font-bold text-slate-900">{overview?.active_cases || 0}</div>
          <span className="text-[10px] text-slate-500">In-flight workflows</span>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm text-left">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-medium">Recovered Cases</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          </div>
          <div className="text-xl font-mono font-bold text-emerald-700">{overview?.recovered_cases || 0}</div>
          <span className="text-[10px] text-slate-500">Successfully settled</span>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm text-left">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-medium">Escalated to Ops</span>
            <ShieldAlert className="w-3.5 h-3.5 text-purple-600" />
          </div>
          <div className="text-xl font-mono font-bold text-purple-700">{overview?.escalated_cases || 0}</div>
          <span className="text-[10px] text-slate-500">VIP / High-value cases</span>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm text-left">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span className="font-medium">Stopped Cases</span>
            <Ban className="w-3.5 h-3.5 text-slate-400" />
          </div>
          <div className="text-xl font-mono font-bold text-slate-700">{overview?.stopped_cases || 0}</div>
          <span className="text-[10px] text-slate-500">Max retries / Policy stops</span>
        </div>
      </div>

      {/* Recovery Funnel */}
      <RecoveryFunnel
        revenueAtRisk={overview?.revenue_at_risk || 0}
        potentiallyRecoverable={overview?.potentially_recoverable || 0}
        recoveredRevenue={overview?.recovered_revenue || 0}
        recoveryRate={overview?.recovery_rate || 0}
        attemptsCount={attemptsTotal}
      />

      {/* Visual Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecoveryTrendChart data={trend} />
        <FailureBreakdownChart data={failureBreakdown} />
      </div>

      {/* Strategy Performance Table */}
      <ActionBreakdownChart data={actionBreakdown} />
    </PageContainer>
  );
};
