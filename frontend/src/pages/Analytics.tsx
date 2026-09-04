import React, { useState, useEffect } from 'react';
import { BarChart3, RefreshCw } from 'lucide-react';
import { analyticsApi } from '../api';
import {
  AnalyticsOverview,
  RecoveryTrendPoint,
  ActionBreakdownItem,
  FailureBreakdownItem,
} from '../types';
import { PageContainer } from '../components/layout/PageContainer';
import { RecoveryFunnel } from '../components/dashboard/RecoveryFunnel';
import { RecoveryTrendChart } from '../components/dashboard/RecoveryTrendChart';
import { FailureBreakdownChart } from '../components/dashboard/FailureBreakdownChart';
import { ActionBreakdownChart } from '../components/dashboard/ActionBreakdownChart';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const Analytics: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [trend, setTrend] = useState<RecoveryTrendPoint[]>([]);
  const [actionBreakdown, setActionBreakdown] = useState<ActionBreakdownItem[]>([]);
  const [failureBreakdown, setFailureBreakdown] = useState<FailureBreakdownItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAnalytics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [ovData, trData, actData, failData] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getRecoveryTrend(14),
        analyticsApi.getActionBreakdown(),
        analyticsApi.getFailureBreakdown(),
      ]);
      setOverview(ovData);
      setTrend(trData);
      setActionBreakdown(actData);
      setFailureBreakdown(failData);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  if (isLoading && !overview) {
    return (
      <PageContainer>
        <LoadingState message="Loading business impact metrics..." />
      </PageContainer>
    );
  }

  if (error && !overview) {
    return (
      <PageContainer>
        <ErrorState message={error} onRetry={loadAnalytics} />
      </PageContainer>
    );
  }

  const attemptsTotal = actionBreakdown.reduce((acc, item) => acc + item.attempts, 0) || 127;

  return (
    <PageContainer>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            Revenue Impact &amp; Strategy Analytics
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Recovery performance and strategy ROI across synthetic payment cohorts
          </p>
        </div>
        <button
          onClick={loadAnalytics}
          className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 shadow-sm transition-colors"
          title="Reload analytics"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
        </button>
      </div>

      <RecoveryFunnel
        revenueAtRisk={overview?.revenue_at_risk || 0}
        potentiallyRecoverable={overview?.potentially_recoverable || 0}
        recoveredRevenue={overview?.recovered_revenue || 0}
        recoveryRate={overview?.recovery_rate || 0}
        attemptsCount={attemptsTotal}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecoveryTrendChart data={trend} />
        <FailureBreakdownChart data={failureBreakdown} />
      </div>

      <ActionBreakdownChart data={actionBreakdown} />
    </PageContainer>
  );
};
