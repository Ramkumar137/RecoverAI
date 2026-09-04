import React from 'react';
import { ArrowDown, CheckCircle2, TrendingUp, AlertTriangle, ShieldCheck } from 'lucide-react';
import { formatINR, formatPercent } from '../../utils/formatters';

interface Props {
  revenueAtRisk: number;
  potentiallyRecoverable: number;
  recoveredRevenue: number;
  recoveryRate: number;
  attemptsCount?: number;
}

export const RecoveryFunnel: React.FC<Props> = ({
  revenueAtRisk,
  potentiallyRecoverable,
  recoveredRevenue,
  recoveryRate,
  attemptsCount = 127,
}) => {
  const potentialPct = revenueAtRisk > 0 ? (potentiallyRecoverable / revenueAtRisk) * 100 : 0;
  const recoveredPctOfRisk = revenueAtRisk > 0 ? (recoveredRevenue / revenueAtRisk) * 100 : 0;

  return (
    <div className="rounded-xl bg-white border border-slate-200 p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-600" />
            Revenue Recovery Funnel
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Stage-by-stage progression from initial transaction failure to recovered settlement
          </p>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">Realized Conversion</span>
          <span className="text-base font-bold font-mono text-emerald-600">{formatPercent(recoveryRate)}</span>
        </div>
      </div>

      {/* Visual Pipeline Bars */}
      <div className="space-y-4">
        {/* Step 1: Revenue at Risk */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-800 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500" />
              Revenue at Risk
            </span>
            <span className="font-mono font-bold text-slate-900">{formatINR(revenueAtRisk)} (100%)</span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden">
            <div className="h-full bg-rose-500 rounded-full w-full" />
          </div>
        </div>

        <div className="flex justify-center -my-1 text-slate-400">
          <ArrowDown className="w-3.5 h-3.5" />
        </div>

        {/* Step 2: Potentially Recoverable */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-800 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              Potentially Recoverable
            </span>
            <span className="font-mono font-bold text-slate-900">
              {formatINR(potentiallyRecoverable)} ({potentialPct.toFixed(1)}% of Risk)
            </span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden">
            <div
              className="h-full bg-amber-500 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(5, potentialPct))}%` }}
            />
          </div>
        </div>

        <div className="flex justify-center -my-1 text-slate-400">
          <ArrowDown className="w-3.5 h-3.5" />
        </div>

        {/* Step 3: Recovery Attempts */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <div>
              <span className="font-semibold text-slate-800 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-600" />
                Recovery Attempts
              </span>
              <span className="text-[11px] text-slate-500 block mt-0.5 ml-4">
                A case may generate multiple bounded recovery attempts.
              </span>
            </div>
            <span className="font-mono font-bold text-slate-900">
              {attemptsCount} Attempts
            </span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(5, (attemptsCount / (attemptsCount + 30)) * 100))}%` }}
            />
          </div>
        </div>

        <div className="flex justify-center -my-1 text-slate-400">
          <ArrowDown className="w-3.5 h-3.5" />
        </div>

        {/* Step 4: Recovered Revenue */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-800 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-600" />
              Recovered Revenue
            </span>
            <span className="font-mono font-bold text-emerald-700">
              {formatINR(recoveredRevenue)} ({recoveredPctOfRisk.toFixed(1)}% of Risk &bull; {recoveryRate}% of Recoverable)
            </span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden">
            <div
              className="h-full bg-emerald-600 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(5, recoveredPctOfRisk))}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
