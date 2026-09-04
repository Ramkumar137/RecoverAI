import React from 'react';
import { Search, Filter, X } from 'lucide-react';

interface Props {
  search: string;
  onSearchChange: (value: string) => void;
  status: string;
  onStatusChange: (value: string) => void;
  failureReason: string;
  onFailureReasonChange: (value: string) => void;
  onReset: () => void;
}

export const PaymentFilters: React.FC<Props> = ({
  search,
  onSearchChange,
  status,
  onStatusChange,
  failureReason,
  onFailureReasonChange,
  onReset,
}) => {
  const hasFilters = Boolean(search || status || failureReason);

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-4 rounded-2xl bg-white border border-slate-200 shadow-sm">
      <div className="relative flex-1 min-w-[240px]">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search payment reference or customer..."
          className="w-full pl-9 pr-4 py-2 rounded-xl bg-white border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 transition-colors shadow-sm"
        />
      </div>

      <div className="flex items-center gap-2.5 flex-wrap">
        {/* Status Dropdown */}
        <select
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
          className="px-3 py-2 rounded-xl bg-white border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-blue-600 transition-colors shadow-sm"
        >
          <option value="">All Statuses</option>
          <option value="FAILED">Failed</option>
          <option value="ABANDONED">Abandoned</option>
          <option value="RECOVERED">Recovered</option>
          <option value="SUCCESS">Success</option>
          <option value="EXPIRED">Expired</option>
        </select>

        {/* Failure Reason Dropdown */}
        <select
          value={failureReason}
          onChange={(e) => onFailureReasonChange(e.target.value)}
          className="px-3 py-2 rounded-xl bg-white border border-slate-200 text-xs text-slate-700 focus:outline-none focus:border-blue-600 transition-colors shadow-sm"
        >
          <option value="">All Decline Reasons</option>
          <option value="BANK_TIMEOUT">Bank Timeout</option>
          <option value="INSUFFICIENT_FUNDS">Insufficient Funds</option>
          <option value="CARD_DECLINED">Card Declined</option>
          <option value="NETWORK_ERROR">Network Error</option>
          <option value="AUTHENTICATION_FAILED">Auth Failed</option>
          <option value="LIMIT_EXCEEDED">Limit Exceeded</option>
        </select>

        {hasFilters && (
          <button
            onClick={onReset}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-slate-900 transition-colors text-xs flex items-center gap-1 border border-slate-200"
            title="Clear filters"
          >
            <X className="w-3.5 h-3.5" />
            <span className="hidden sm:inline text-[11px]">Reset</span>
          </button>
        )}
      </div>
    </div>
  );
};
