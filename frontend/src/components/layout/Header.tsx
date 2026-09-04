import React, { useState } from 'react';
import { RefreshCw, Play, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { HealthStatus, BatchRecoveryResult } from '../../types';
import { recoveryApi } from '../../api';
import { ConfirmDialog } from '../common/ConfirmDialog';

interface Props {
  title: string;
  subtitle: string;
  health: HealthStatus | null;
  onRefresh: () => void;
  isLoading?: boolean;
  onBatchComplete?: (result: BatchRecoveryResult) => void;
}

export const Header: React.FC<Props> = ({
  title,
  subtitle,
  health,
  onRefresh,
  isLoading = false,
  onBatchComplete,
}) => {
  const [isBatchConfirmOpen, setIsBatchConfirmOpen] = useState(false);
  const [isExecutingBatch, setIsExecutingBatch] = useState(false);
  const [batchResult, setBatchResult] = useState<BatchRecoveryResult | null>(null);

  const handleRunBatch = async () => {
    setIsExecutingBatch(true);
    try {
      const res = await recoveryApi.runBatch(500);
      setBatchResult(res);
      setIsBatchConfirmOpen(false);
      onRefresh();
      if (onBatchComplete) {
        onBatchComplete(res);
      }
    } catch (err) {
      console.error('Batch run error:', err);
    } finally {
      setIsExecutingBatch(false);
    }
  };

  return (
    <>
      <header className="h-16 px-6 lg:px-8 border-b border-slate-200 bg-white sticky top-0 z-30 flex items-center justify-between shadow-sm">
        <div>
          <h1 className="text-base lg:text-lg font-bold text-slate-900 tracking-tight">
            {title}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Simulation Pill */}
          <div className="hidden sm:flex flex-col items-end">
            <div
              className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-xs font-semibold text-amber-800"
              title="All recovery actions are simulated. No real financial transactions are executed."
            >
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
              <span>Simulation Mode</span>
            </div>
            <span className="text-[10px] text-slate-400 mt-0.5 max-w-[210px] text-right truncate">
              Simulated transactions only
            </span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            title="Refresh metrics"
            className="p-2 rounded-lg bg-white hover:bg-slate-50 text-slate-600 hover:text-slate-900 border border-slate-200 shadow-sm transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
          </button>

          {/* Run Batch Recovery Button */}
          <button
            onClick={() => setIsBatchConfirmOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-colors active:scale-95"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run Batch Recovery</span>
          </button>
        </div>
      </header>

      {/* Confirmation Dialog */}
      <ConfirmDialog
        isOpen={isBatchConfirmOpen}
        title="Execute Batch Payment Recovery"
        description="Run simulated recovery workflows across all eligible failed and abandoned payments?"
        confirmText="Execute Batch Recovery"
        isLoading={isExecutingBatch}
        details={[
          { label: 'Scope', value: 'Up to 500 Eligible Open Cases' },
          { label: 'Enforcement', value: 'Deterministic Stopping Rules & Max 3 Retries' },
          { label: 'Safety Mode', value: 'Simulation Mode Only (No real bank transactions)' },
        ]}
        onConfirm={handleRunBatch}
        onClose={() => setIsBatchConfirmOpen(false)}
      />

      {/* Post-Batch Result Toast/Notification */}
      {batchResult && (
        <div className="fixed bottom-6 right-6 z-50 max-w-md rounded-xl bg-white border border-emerald-200 p-5 shadow-xl animate-in slide-in-from-bottom duration-300">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2 text-emerald-700">
              <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-600" />
              <span className="text-sm font-bold text-slate-900">Batch Recovery Completed</span>
            </div>
            <button
              onClick={() => setBatchResult(null)}
              className="text-slate-400 hover:text-slate-600 text-xs p-1"
            >
              ✕
            </button>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            All recovery actions executed in simulation mode.
          </p>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-[10px] text-slate-500 font-medium">Processed</div>
              <div className="font-semibold text-slate-800 mt-0.5">{batchResult.cases_processed} cases</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-[10px] text-slate-500 font-medium">Recovered</div>
              <div className="font-semibold text-emerald-700 mt-0.5">{batchResult.payments_recovered} payments</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-[10px] text-slate-500 font-medium">Recovered Revenue</div>
              <div className="font-semibold text-slate-900 mt-0.5">₹{batchResult.recovered_revenue.toLocaleString('en-IN')}</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-[10px] text-slate-500 font-medium">Recovery Rate</div>
              <div className="font-semibold text-blue-700 mt-0.5">{batchResult.recovery_rate}%</div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
