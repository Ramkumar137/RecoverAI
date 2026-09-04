export interface AnalyticsOverview {
  revenue_at_risk: number;
  potentially_recoverable: number;
  recovered_revenue: number;
  recovery_rate: number;
  active_cases: number;
  recovered_cases: number;
  escalated_cases: number;
  stopped_cases: number;
}

export interface RecoveryTrendPoint {
  date: string;
  revenue_at_risk: number;
  recovered: number;
}

export interface ActionBreakdownItem {
  action: string;
  attempts: number;
  successful: number;
  recovered_amount: number;
}

export interface FailureBreakdownItem {
  failure_reason: string;
  count: number;
  amount_at_risk: number;
  recovered_amount: number;
  recovery_rate: number;
}

export interface RevenueRiskMetrics {
  total_revenue_at_risk: number;
  potentially_recoverable_revenue: number;
  recovered_revenue: number;
  recovery_rate: number;
  status_breakdown: Record<string, number>;
}
