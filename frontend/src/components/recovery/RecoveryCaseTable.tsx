import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';
import { RecoveryCase } from '../../types';
import { formatINR } from '../../utils/formatters';
import { StatusBadge } from '../common/StatusBadge';
import { calculateRecoveryPriority } from '../../utils/badges';

interface Props {
  cases: RecoveryCase[];
}

export const RecoveryCaseTable: React.FC<Props> = ({ cases }) => {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200 text-[11px]">
            <tr>
              <th className="px-4 py-3.5">Case &amp; Payment</th>
              <th className="px-4 py-3.5">Amount at Risk</th>
              <th className="px-4 py-3.5">Recovery Score</th>
              <th className="px-4 py-3.5">Priority</th>
              <th className="px-4 py-3.5">AI Recommendation</th>
              <th className="px-4 py-3.5">Policy</th>
              <th className="px-4 py-3.5">Final Action</th>
              <th className="px-4 py-3.5">Recovery Status</th>
              <th className="px-4 py-3.5 text-right">View</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {cases.map((c) => {
              const paymentRef = c.payment?.payment_id || `Payment #${c.payment_id}`;
              const isVIP = paymentRef === 'PAY_10482';
              const retryCount = c.payment?.retry_count ?? c.recovery_attempts ?? 0;
              const priority = calculateRecoveryPriority(c.revenue_at_risk, c.recoverability_score, retryCount);
              const isApproved = c.policy_result === 'ALLOWED' || c.policy_result === 'APPROVED';

              return (
                <tr
                  key={c.id}
                  className={`hover:bg-slate-50/80 transition-colors ${
                    isVIP ? 'bg-blue-50/40 hover:bg-blue-50/60' : ''
                  }`}
                >
                  <td className="px-4 py-3.5">
                    <div className="flex items-center gap-1.5 font-bold font-mono text-slate-900">
                      <span>Case #{c.id}</span>
                      {isVIP && (
                        <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 border border-blue-200 text-[9px] font-mono font-semibold uppercase">
                          VIP Demo
                        </span>
                      )}
                    </div>
                    <div className="font-mono text-[11px] text-slate-500">{paymentRef}</div>
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="font-mono font-bold text-slate-900">{formatINR(c.revenue_at_risk)}</div>
                    {c.recovered_amount > 0 && (
                      <div className="text-[10px] font-mono font-semibold text-emerald-600">
                        +{formatINR(c.recovered_amount)} recovered
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3.5">
                    <StatusBadge type="score" value={c.recoverability_score} />
                  </td>
                  <td className="px-4 py-3.5">
                    <StatusBadge type="priority" value={priority} />
                  </td>
                  <td className="px-4 py-3.5">
                    <StatusBadge type="action" value={c.ai_recommended_action || c.recommended_action || 'None'} />
                  </td>
                  <td className="px-4 py-3.5">
                    {c.policy_result ? (
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                        isApproved
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          : 'bg-rose-50 text-rose-700 border-rose-200'
                      }`}>
                        {isApproved ? <ShieldCheck className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                        {isApproved ? 'APPROVED' : c.policy_result}
                      </span>
                    ) : (
                      <span className="text-slate-400 font-mono text-[10px]">PENDING</span>
                    )}
                  </td>
                  <td className="px-4 py-3.5">
                    <StatusBadge type="action" value={c.final_action || c.recommended_action || 'None'} />
                  </td>
                  <td className="px-4 py-3.5">
                    <StatusBadge type="status" value={c.status} />
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <Link
                      to={`/recovery/${c.id}`}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-all active:scale-95"
                    >
                      <span>View Details</span>
                      <ArrowRight className="w-3.5 h-3.5" />
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
