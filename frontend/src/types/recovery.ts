import { Payment } from './payment';

export type RecoveryCaseStatus =
  | 'OPEN'
  | 'INVESTIGATING'
  | 'RECOVERY_RECOMMENDED'
  | 'ACTION_APPROVED'
  | 'ACTION_EXECUTED'
  | 'RECOVERED'
  | 'ESCALATED'
  | 'STOPPED'
  | 'FAILED'
  | 'IN_PROGRESS'
  | 'CLOSED';

export type RecoveryActionType =
  | 'RETRY_PAYMENT'
  | 'RETRY_LATER'
  | 'SEND_PAYMENT_LINK'
  | 'SEND_REMINDER'
  | 'CHANGE_PAYMENT_METHOD'
  | 'ESCALATE_TO_HUMAN'
  | 'STOP_RECOVERY';

export interface RecoveryAction {
  id: number;
  recovery_case_id: number;
  action_type: RecoveryActionType | string;
  status: 'SCHEDULED' | 'EXECUTED' | 'FAILED' | 'SKIPPED';
  scheduled_at?: string | null;
  executed_at?: string | null;
  reason?: string | null;
  metadata_?: Record<string, any> | null;
  created_at: string;
}

export interface RecoveryCase {
  id: number;
  payment_id: number;
  revenue_at_risk: number;
  recoverability_score: number;
  diagnosis?: string | null;
  recommended_action?: string | null;
  status: RecoveryCaseStatus;
  recovered_amount: number;
  ai_diagnosis?: string | null;
  ai_confidence?: number | null;
  ai_summary?: string | null;
  ai_evidence?: Array<Record<string, any>> | null;
  ai_recommended_action?: string | null;
  policy_result?: 'ALLOWED' | 'DENIED' | string | null;
  final_action?: string | null;
  escalation_required: boolean;
  recovery_attempts?: number;
  expires_at?: string | null;
  created_at: string;
  updated_at: string;
  payment?: Payment | null;
  recovery_actions?: RecoveryAction[];
}

export interface TimelineEvent {
  event: string;
  timestamp?: string | null;
  actor: string;
  description: string;
  metadata?: Record<string, any>;
}

export interface RecoveryExecutionResult {
  case_id: number;
  payment_id: string;
  action: string;
  status: string;
  previous_amount: number;
  recovered_amount: number;
  retry_count: number;
  idempotent: boolean;
  message: string;
}

export interface BatchRecoveryResult {
  cases_processed: number;
  actions_executed: number;
  payments_recovered: number;
  payments_failed: number;
  escalated: number;
  stopped: number;
  revenue_at_risk: number;
  potentially_recoverable: number;
  recovered_revenue: number;
  recovery_rate: number;
}
