import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Play,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { recoveryApi, aiApi } from '../api';
import { RecoveryCase, TimelineEvent, AIInvestigation, RecoveryExecutionResult } from '../types';
import { formatINR } from '../utils/formatters';
import { PageContainer } from '../components/layout/PageContainer';
import { StatusBadge } from '../components/common/StatusBadge';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { AIInvestigationCard } from '../components/recovery/AIInvestigationCard';
import { PolicyDecisionCard } from '../components/recovery/PolicyDecisionCard';
import { RecoveryTimeline } from '../components/recovery/RecoveryTimeline';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';

export const RecoveryCaseDetails: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const [caseData, setCaseData] = useState<RecoveryCase | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [investigation, setInvestigation] = useState<AIInvestigation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Execution Modal State
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionMessage, setExecutionMessage] = useState<string | null>(null);

  const isFetchingRef = useRef(false);

  const loadCaseData = async () => {
    if (!caseId) return;
    if (isFetchingRef.current) return;
    isFetchingRef.current = true;
    setIsLoading(true);
    setError(null);
    try {
      const c = await recoveryApi.getCase(Number(caseId));
      setCaseData(c);

      // Load timeline
      const tl = await recoveryApi.getTimeline(Number(caseId));
      setTimeline(tl);

      // Load or trigger AI Investigation
      const paymentRef = c.payment?.payment_id || String(c.payment_id);
      try {
        const inv = await aiApi.getReport(paymentRef);
        setInvestigation(inv);
      } catch {
        const inv = await aiApi.investigate(paymentRef, false);
        setInvestigation(inv);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load recovery case details');
    } finally {
      setIsLoading(false);
      isFetchingRef.current = false;
    }
  };

  useEffect(() => {
    loadCaseData();
  }, [caseId]);

  const handleExecuteRecovery = async () => {
    if (!caseData) return;
    setIsExecuting(true);
    try {
      const result = await recoveryApi.executeRecovery(caseData.id);
      setIsConfirmOpen(false);
      setExecutionMessage(
        result.idempotent
          ? `Idempotent execution: Case is already in terminal state '${result.status}'. Zero revenue inflation.`
          : `Recovery action '${result.action}' executed successfully! Outcome: ${result.status}`
      );
      // Reload case and timeline
      await loadCaseData();
    } catch (err: any) {
      setExecutionMessage(`Execution failed: ${err.message || 'Unknown error'}`);
    } finally {
      setIsExecuting(false);
    }
  };

  if (isLoading && !caseData) {
    return (
      <PageContainer>
        <LoadingState message="Loading recovery case telemetry..." />
      </PageContainer>
    );
  }

  if (error || !caseData) {
    return (
      <PageContainer>
        <ErrorState message={error || 'Case not found'} onRetry={loadCaseData} />
      </PageContainer>
    );
  }

  const paymentRef = caseData.payment?.payment_id || `Payment #${caseData.payment_id}`;
  const amountNum = Number(caseData.payment?.amount || caseData.revenue_at_risk);
  const isTerminal = ['RECOVERED', 'STOPPED', 'ESCALATED'].includes(caseData.status);

  return (
    <PageContainer>
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <Link
            to="/recovery"
            className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-600 hover:text-slate-900 border border-slate-200 shadow-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold font-mono text-slate-900">Recovery Case #{caseData.id}</h2>
              <StatusBadge type="status" value={caseData.status} />
              {paymentRef === 'PAY_10482' && (
                <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-mono uppercase font-bold">
                  VIP Demo
                </span>
              )}
            </div>
            <div className="text-xs text-slate-500 font-mono mt-0.5">
              Payment Reference: <strong className="text-slate-800">{paymentRef}</strong> &bull; Amount: <strong className="text-slate-900">{formatINR(amountNum)}</strong>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Simulation Mode Pill */}
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-[11px] font-semibold text-amber-800">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            SIMULATION MODE ACTIVE
          </span>

          {/* Execute Recovery Button */}
          <button
            onClick={() => setIsConfirmOpen(true)}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold shadow-sm transition-all active:scale-95 ${
              isTerminal
                ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isTerminal ? 'Re-execute (Idempotency Test)' : 'Execute Recovery Action'}</span>
          </button>
        </div>
      </div>

      {/* Execution Feedback Banner */}
      {executionMessage && (
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-between text-xs text-blue-900">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{executionMessage}</span>
          </div>
          <button
            onClick={() => setExecutionMessage(null)}
            className="text-blue-600 hover:text-blue-800 text-xs px-2 font-medium"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* SECTION A: REVENUE SUMMARY */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm text-left">
          <span className="text-[11px] uppercase font-bold text-rose-600 block mb-1">
            Revenue at Risk
          </span>
          <div className="text-2xl font-mono font-bold text-slate-900">{formatINR(caseData.revenue_at_risk)}</div>
          <span className="text-[10px] text-slate-500">Transaction exposure</span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm text-left">
          <span className="text-[11px] uppercase font-bold text-amber-600 block mb-1">
            Recoverability Score
          </span>
          <div className="text-2xl font-mono font-bold text-amber-600">
            {caseData.recoverability_score.toFixed(1)}%
          </div>
          <span className="text-[10px] text-slate-500">ML prediction likelihood</span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm text-left">
          <span className="text-[11px] uppercase font-bold text-blue-600 block mb-1">
            Approved Strategy
          </span>
          <div className="mt-1">
            <StatusBadge type="action" value={caseData.final_action || caseData.recommended_action || 'None'} />
          </div>
          <span className="text-[10px] text-slate-500 block mt-1">Deterministic policy</span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm text-left">
          <span className="text-[11px] uppercase font-bold text-emerald-600 block mb-1">
            Recovered Amount
          </span>
          <div className="text-2xl font-mono font-bold text-emerald-600">
            {formatINR(caseData.recovered_amount)}
          </div>
          <span className="text-[10px] text-slate-500">Settled to merchant</span>
        </div>
      </div>

      {/* Distinction Banner: Recoverability Score vs AI Confidence */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100">
          <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-mono font-bold text-xs flex-shrink-0 border border-amber-200">
            ML
          </div>
          <div>
            <div className="font-semibold text-slate-900">
              Recoverability Score ({caseData.recoverability_score.toFixed(1)}%)
            </div>
            <p className="text-slate-500 text-[11px] mt-0.5 leading-relaxed">
              ML-estimated statistical probability that this transaction will successfully settle if a bounded recovery action is taken.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-mono font-bold text-xs flex-shrink-0 border border-blue-200">
            AI
          </div>
          <div>
            <div className="font-semibold text-slate-900">
              AI Recommendation Confidence ({investigation ? (investigation.confidence * 100).toFixed(0) : '90'}%)
            </div>
            <p className="text-slate-500 text-[11px] mt-0.5 leading-relaxed">
              Diagnostic certainty of the root cause classification and recommended intervention channel based on telemetry signals.
            </p>
          </div>
        </div>
      </div>

      {/* SECTION B & C: AI INVESTIGATION & POLICY DECISION */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {investigation ? (
          <AIInvestigationCard investigation={investigation} />
        ) : (
          <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm text-center text-xs text-slate-500">
            No AI investigation report available.
          </div>
        )}

        <PolicyDecisionCard
          aiAction={caseData.ai_recommended_action || caseData.recommended_action || 'RETRY_LATER'}
          policyResult={caseData.policy_result || 'ALLOWED'}
          finalAction={caseData.final_action || caseData.recommended_action || 'RETRY_LATER'}
          policyApplied={investigation?.policy_applied || 'POLICY_MAX_RETRIES_COMPLIANT'}
          policyReason={investigation?.policy_reason || 'Transaction complies with all safety rules and retry thresholds.'}
          retryCount={caseData.payment?.retry_count || 0}
          maxRetries={3}
          escalationRequired={caseData.escalation_required}
          recoverabilityScore={caseData.recoverability_score}
        />
      </div>

      {/* SECTION D: RECOVERY AUDIT TIMELINE */}
      <RecoveryTimeline events={timeline} />

      {/* Confirmation Dialog */}
      <ConfirmDialog
        isOpen={isConfirmOpen}
        title="Execute Simulated Recovery Action"
        description={`Trigger bounded recovery workflow for case #${caseData.id}?`}
        confirmText="Confirm &amp; Execute Action"
        isLoading={isExecuting}
        details={[
          { label: 'Payment ID', value: paymentRef },
          { label: 'Amount', value: formatINR(amountNum) },
          { label: 'Approved Action', value: caseData.final_action || caseData.recommended_action || 'RETRY_LATER' },
          { label: 'Policy Ruling', value: caseData.policy_result || 'ALLOWED' },
          { label: 'Current Status', value: caseData.status },
        ]}
        onConfirm={handleExecuteRecovery}
        onClose={() => setIsConfirmOpen(false)}
      />
    </PageContainer>
  );
};
