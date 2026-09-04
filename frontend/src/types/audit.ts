export interface AuditLogEntry {
  id: number;
  recovery_case_id?: number | null;
  event_type: string;
  description: string;
  actor: string;
  metadata_?: Record<string, any> | null;
  created_at: string;
}
