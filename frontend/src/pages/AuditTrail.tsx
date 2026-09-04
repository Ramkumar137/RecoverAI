import React, { useState, useEffect } from 'react';
import { ClipboardList, RefreshCw, Filter } from 'lucide-react';
import { recoveryApi } from '../api';
import { AuditLogEntry } from '../types';
import { formatDate } from '../utils/formatters';
import { PageContainer } from '../components/layout/PageContainer';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';

export const AuditTrail: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [eventType, setEventType] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const eventTypes = [
    { id: '', label: 'All Event Types' },
    { id: 'PAYMENT_FAILED', label: 'Payment Failed' },
    { id: 'CASE_CREATED', label: 'Case Created' },
    { id: 'AI_INVESTIGATION_COMPLETED', label: 'AI Investigation Completed' },
    { id: 'RECOVERY_ACTION_STARTED', label: 'Action Started' },
    { id: 'PAYMENT_RECOVERED', label: 'Payment Recovered' },
    { id: 'PAYMENT_RETRY_ATTEMPTED', label: 'Retry Attempted' },
    { id: 'RECOVERY_STOPPED', label: 'Recovery Stopped' },
    { id: 'HUMAN_ESCALATION', label: 'Human Escalation' },
  ];

  const loadLogs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await recoveryApi.listAuditLogs({
        limit: 100,
        event_type: eventType || undefined,
      });
      setLogs(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit logs');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [eventType]);

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <ClipboardList className="w-5 h-5 text-blue-600" />
            Audit Trail
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Trace every AI recommendation, policy decision, and recovery action.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-blue-600 transition-colors shadow-sm"
          >
            {eventTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label}
              </option>
            ))}
          </select>

          <button
            onClick={loadLogs}
            className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 shadow-sm transition-colors"
            title="Reload audit ledger"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>
      </div>

      {isLoading ? (
        <LoadingState message="Loading audit trail records..." />
      ) : error ? (
        <ErrorState message={error} onRetry={loadLogs} />
      ) : logs.length === 0 ? (
        <EmptyState
          title="No Audit Records Found"
          message="No entries match the selected event type."
          actionText="Clear Filter"
          onAction={() => setEventType('')}
        />
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200 text-[11px]">
                <tr>
                  <th className="px-5 py-3.5">Timestamp</th>
                  <th className="px-5 py-3.5">Event Type</th>
                  <th className="px-5 py-3.5">Actor</th>
                  <th className="px-5 py-3.5">Case Reference</th>
                  <th className="px-5 py-3.5">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-slate-500 whitespace-nowrap text-[11px]">
                      {formatDate(log.created_at)}
                    </td>
                    <td className="px-5 py-3.5 font-mono font-bold whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 text-[11px] font-semibold">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-slate-800 font-medium whitespace-nowrap">
                      {log.actor}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-slate-600 whitespace-nowrap">
                      {log.recovery_case_id ? `Case #${log.recovery_case_id}` : '—'}
                    </td>
                    <td className="px-5 py-3.5 text-slate-700 leading-relaxed max-w-md">
                      {log.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </PageContainer>
  );
};
