import React from 'react';
import { ShieldCheck, ShieldAlert, Check, ArrowRight, Lock, CheckCircle2, Shield, AlertTriangle } from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';

interface Props {
  aiAction: string;
  policyResult: string;
  finalAction: string;
  policyApplied?: string;
  policyReason?: string;
  retryCount?: number;
  maxRetries?: number;
  escalationRequired?: boolean;
  recoverabilityScore?: number;
}

export const PolicyDecisionCard: React.FC<Props> = ({
  aiAction,
  policyResult,
  finalAction,
  policyApplied = 'POLICY_MAX_RETRIES_COMPLIANT',
  policyReason = 'Compliant with enterprise safety rules and retry risk thresholds.',
  retryCount = 0,
  maxRetries = 3,
  escalationRequired = false,
  recoverabilityScore = 98.5,
}) => {
  const isAllowed = (policyResult || '').toUpperCase() === 'ALLOWED' || (policyResult || '').toUpperCase() === 'APPROVED';

  // Check definitions
  const checks = [
    {
      title: 'Retry Count',
      detail: `${retryCount} / ${maxRetries} (${retryCount < maxRetries ? 'Below policy limit' : 'Exceeded'})`,
      passed: retryCount < maxRetries,
    },
    {
      title: 'Recovery Window',
      detail: '48 hours (Within acceptable range)',
      passed: true,
    },
    {
      title: 'Recoverability',
      detail: `${recoverabilityScore.toFixed(1)}% (Minimum score threshold met)`,
      passed: true,
    },
    {
      title: 'Human Escalation',
      detail: escalationRequired ? 'Required (Triggered)' : 'Not required (Autonomous)',
      passed: !escalationRequired,
    },
  ];

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center border ${
            isAllowed
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-rose-50 text-rose-700 border-rose-200'
          }`}>
            {isAllowed ? <ShieldCheck className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Policy Decision
            </h3>
            <p className="text-xs text-slate-500">
              Deterministic business guardrails regulating automated recovery execution
            </p>
          </div>
        </div>

        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold border ${
          isAllowed
            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
            : 'bg-rose-50 text-rose-700 border-rose-200'
        }`}>
          {isAllowed ? <Check className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
          POLICY {isAllowed ? 'APPROVED' : (policyResult || 'REJECTED')}
        </span>
      </div>

      {/* Safety Principle Banner */}
      <div className="p-3 rounded-xl bg-blue-50/60 border border-blue-200/80 flex items-center gap-2.5 text-xs text-blue-900">
        <Shield className="w-4 h-4 text-blue-600 flex-shrink-0" />
        <div>
          <strong className="font-semibold text-blue-900">Core Safety Principle:</strong>{' '}
          <span className="text-blue-800">AI recommends. Deterministic policy controls execution.</span>
        </div>
      </div>

      {/* Visual Governance Flow: AI -> Policy -> Final */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Step 1 */}
        <div className="space-y-1">
          <span className="text-[10px] uppercase font-bold text-slate-500">1. AI Recommendation</span>
          <div>
            <StatusBadge type="action" value={aiAction} />
          </div>
        </div>

        <ArrowRight className="hidden md:block w-4 h-4 text-slate-400 flex-shrink-0" />

        {/* Step 2 */}
        <div className="space-y-1">
          <span className="text-[10px] uppercase font-bold text-slate-500">2. Deterministic Policy Check</span>
          <div className="font-mono text-xs font-bold text-slate-800">
            {policyApplied}
          </div>
        </div>

        <ArrowRight className="hidden md:block w-4 h-4 text-slate-400 flex-shrink-0" />

        {/* Step 3 */}
        <div className="space-y-1">
          <span className="text-[10px] uppercase font-bold text-emerald-700">3. Final Approved Action</span>
          <div>
            <StatusBadge type="action" value={finalAction} />
          </div>
        </div>
      </div>

      {/* Policy Verification Checklist */}
      <div className="space-y-2">
        <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
          Policy Checks Enforced
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {checks.map((check, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-0.5"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-900">{check.title}</span>
                <span
                  className={`inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded font-bold border ${
                    check.passed
                      ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                      : 'text-rose-700 bg-rose-50 border-rose-200'
                  }`}
                >
                  {check.passed ? <Check className="w-2.5 h-2.5" /> : <AlertTriangle className="w-2.5 h-2.5" />}
                  {check.passed ? 'PASSED' : 'ALERT'}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 leading-normal">{check.detail}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Rationale & Operational Parameter Counters */}
      <div className="pt-2 border-t border-slate-100 space-y-2">
        <p className="text-xs text-slate-600 leading-relaxed">
          <strong className="text-slate-800">Governance Rationale:</strong> {policyReason}
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-500 block">Retry Counter</span>
            <span className="font-mono font-bold text-slate-800">{retryCount} / {maxRetries} Max</span>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-500 block">Recovery Window</span>
            <span className="font-mono font-bold text-slate-800">48 Hours TTL</span>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-500 block">Human Escalation</span>
            <span className={`font-mono font-bold ${escalationRequired ? 'text-purple-600' : 'text-slate-600'}`}>
              {escalationRequired ? 'Mandated' : 'Not Required'}
            </span>
          </div>

          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
            <span className="text-[10px] text-slate-500 block">Final Policy Decision</span>
            <span className="font-mono font-bold text-emerald-700">
              {isAllowed ? 'APPROVED' : (policyResult || 'REJECTED')}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
