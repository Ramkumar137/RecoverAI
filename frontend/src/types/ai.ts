export interface TelemetryEvidence {
  factor: string;
  impact: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | string;
  description: string;
}

export interface AIInvestigation {
  payment_id?: string | null;
  payment_numeric_id: number;
  recovery_case_id: number;
  ai_available: boolean;
  diagnosis: string;
  confidence: number;
  summary: string;
  evidence: TelemetryEvidence[];
  ai_recommended_action: string;
  ai_rationale?: string | null;
  policy_result: 'ALLOWED' | 'DENIED' | string;
  final_action: string;
  policy_applied: string;
  policy_reason: string;
  escalation_required: boolean;
  recovery_channel?: string | null;
  wait_time_minutes?: number;
  recoverability_score: number;
  revenue_at_risk: number;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
}
