import React from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink, ShieldAlert } from 'lucide-react';
import { Payment } from '../../types';
import { formatINR, formatDate } from '../../utils/formatters';
import { StatusBadge } from '../common/StatusBadge';

interface Props {
  payments: Payment[];
  onSelectPayment?: (payment: Payment) => void;
}

export const PaymentTable: React.FC<Props> = ({ payments }) => {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200 text-[11px]">
            <tr>
              <th className="px-5 py-3.5">Payment ID</th>
              <th className="px-5 py-3.5">Customer</th>
              <th className="px-5 py-3.5">Amount</th>
              <th className="px-5 py-3.5">Status</th>
              <th className="px-5 py-3.5">Failure Reason</th>
              <th className="px-5 py-3.5 text-center">Retries</th>
              <th className="px-5 py-3.5">Timestamp</th>
              <th className="px-5 py-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {payments.map((p) => {
              const isDemo = p.payment_id === 'PAY_10482';
              return (
                <tr
                  key={p.id}
                  className={`hover:bg-slate-50/80 transition-colors ${
                    isDemo ? 'bg-blue-50/40 hover:bg-blue-50/60' : ''
                  }`}
                >
                  <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                    <div className="flex items-center gap-1.5">
                      <span>{p.payment_id}</span>
                      {isDemo && (
                        <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 border border-blue-200 text-[9px] font-mono font-semibold uppercase">
                          VIP Demo
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="font-medium text-slate-900">{p.customer?.name || `Customer #${p.customer_id}`}</div>
                    <div className="text-[10px] text-slate-500 truncate max-w-[140px]">
                      {p.customer?.email || '—'}
                    </div>
                  </td>
                  <td className="px-5 py-3.5 font-mono font-bold text-slate-900">
                    {formatINR(p.amount)}
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge type="status" value={p.status} />
                  </td>
                  <td className="px-5 py-3.5">
                    {p.failure_reason ? (
                      <span className="font-mono text-[11px] text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200 font-medium">
                        {p.failure_reason}
                      </span>
                    ) : (
                      <span className="text-slate-400 font-mono text-[11px]">NONE</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-center font-mono font-semibold text-slate-700">
                    <span className={p.retry_count >= 3 ? 'text-rose-600 font-bold' : ''}>
                      {p.retry_count}/3
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-slate-500 font-mono text-[11px]">
                    {formatDate(p.created_at)}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Link
                      to={`/recovery?search=${p.payment_id}`}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold border border-slate-200 shadow-sm transition-colors"
                    >
                      <span>Investigate</span>
                      <ExternalLink className="w-3 h-3 text-slate-400" />
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
