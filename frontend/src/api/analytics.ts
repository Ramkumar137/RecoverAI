import { apiClient } from './client';
import {
  AnalyticsOverview,
  RecoveryTrendPoint,
  ActionBreakdownItem,
  FailureBreakdownItem,
  RevenueRiskMetrics,
  HealthStatus,
} from '../types';

export const analyticsApi = {
  getHealth: async (): Promise<HealthStatus> => {
    const res = await apiClient.get<HealthStatus>('/health');
    return res.data;
  },

  getOverview: async (): Promise<AnalyticsOverview> => {
    const res = await apiClient.get<AnalyticsOverview>('/analytics/overview');
    return res.data;
  },

  getRecoveryTrend: async (days = 14): Promise<RecoveryTrendPoint[]> => {
    const res = await apiClient.get<RecoveryTrendPoint[]>(`/analytics/recovery-trend?days=${days}`);
    return res.data;
  },

  getActionBreakdown: async (): Promise<ActionBreakdownItem[]> => {
    const res = await apiClient.get<ActionBreakdownItem[]>('/analytics/action-breakdown');
    return res.data;
  },

  getFailureBreakdown: async (): Promise<FailureBreakdownItem[]> => {
    const res = await apiClient.get<FailureBreakdownItem[]>('/analytics/failure-breakdown');
    return res.data;
  },

  getRevenueRisk: async (): Promise<RevenueRiskMetrics> => {
    const res = await apiClient.get<RevenueRiskMetrics>('/analytics/revenue-risk');
    return res.data;
  },
};
