import { apiClient } from './client';
import {
  RecoveryCase,
  TimelineEvent,
  RecoveryExecutionResult,
  BatchRecoveryResult,
  AuditLogEntry,
} from '../types';

export const recoveryApi = {
  listCases: async (params?: { skip?: number; limit?: number; status?: string }): Promise<RecoveryCase[]> => {
    const query = new URLSearchParams();
    if (params?.skip !== undefined) query.set('skip', params.skip.toString());
    if (params?.limit !== undefined) query.set('limit', params.limit.toString());
    if (params?.status) query.set('status', params.status);

    const qs = query.toString();
    const res = await apiClient.get<RecoveryCase[]>(`/recovery/cases${qs ? `?${qs}` : ''}`);
    return res.data;
  },

  getCase: async (caseId: number): Promise<RecoveryCase> => {
    const res = await apiClient.get<RecoveryCase>(`/recovery/cases/${caseId}`);
    return res.data;
  },

  getTimeline: async (caseId: number): Promise<TimelineEvent[]> => {
    const res = await apiClient.get<TimelineEvent[]>(`/recovery/cases/${caseId}/timeline`);
    return res.data;
  },

  analyzePayment: async (paymentId: string | number): Promise<RecoveryCase> => {
    const res = await apiClient.post<RecoveryCase>(`/recovery/analyze/${paymentId}`);
    return res.data;
  },

  executeRecovery: async (caseId: number): Promise<RecoveryExecutionResult> => {
    const res = await apiClient.post<RecoveryExecutionResult>(`/recovery/execute/${caseId}`);
    return res.data;
  },

  runBatch: async (limit = 500): Promise<BatchRecoveryResult> => {
    const res = await apiClient.post<BatchRecoveryResult>(`/recovery/run-batch?limit=${limit}`);
    return res.data;
  },

  listAuditLogs: async (params?: { skip?: number; limit?: number; event_type?: string; case_id?: number }): Promise<AuditLogEntry[]> => {
    const query = new URLSearchParams();
    if (params?.skip !== undefined) query.set('skip', params.skip.toString());
    if (params?.limit !== undefined) query.set('limit', params.limit.toString());
    if (params?.event_type) query.set('event_type', params.event_type);
    if (params?.case_id) query.set('case_id', params.case_id.toString());

    const qs = query.toString();
    const res = await apiClient.get<AuditLogEntry[]>(`/recovery/audit-logs${qs ? `?${qs}` : ''}`);
    return res.data;
  },
};
