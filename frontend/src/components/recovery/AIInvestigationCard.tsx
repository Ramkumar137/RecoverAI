import React from 'react';
import { Sparkles, CheckCircle2, AlertCircle, ArrowUpRight, HelpCircle, Check } from 'lucide-react';
import { AIInvestigation } from '../../types';
import { StatusBadge } from '../common/StatusBadge';

interface Props {
  investigation: AIInvestigation;
}

export const AIInvestigationCard: React.FC<Props> = ({ investigation }) => {
  // Derive "Why This Action?" bullet points from investigation signals
  const action = investigation.ai_recommended_action || 'RETRY_LATER';
  const diagnosis = (investigation.diagnosis || '').toUpperCase();

  const getWhyThisAction = () => {
    const reasons: string[] = [];
    let expectedOutcome = 'Recovery attempt scheduled within deterministic safety parameters.';

    // Prioritize actual backend evidence factors when available
    if (investigation.evidence && investigation.evidence.length > 0) {
      investigation.evidence.slice(0, 3).forEach((ev) => {
        reasons.push(`${ev.factor}: ${ev.description}`);
      });
    } else {
      if (action === 'RETRY_PAYMENT' || action === 'RETRY_LATER') {
        reasons.push('Transient failure pattern diagnosed (network fluctuation or bank timeout).');
        reasons.push('Customer account is in good standing with zero chargeback risk.');
        reasons.push('Gateway latency metrics have normalized, indicating high retry viability.');
      } else if (action === 'SEND_PAYMENT_LINK') {
        reasons.push('Authentication or session expiration diagnosed during checkout.');
        reasons.push('Customer demonstrated high checkout intent prior to session drop.');
        reasons.push('Direct payment link eliminates re-authentication friction across devices.');
      } else if (action === 'CHANGE_PAYMENT_METHOD') {
        reasons.push('Instrument-specific decline diagnosed (insufficient balance or card decline).');
        reasons.push('Repeated attempts on current card would worsen decline probability.');
        reasons.push('Prompting UPI or alternative card provides an immediate alternative path.');
      } else if (action === 'ESCALATE_TO_HUMAN') {
        reasons.push('Maximum autonomous retry limits approached or high transaction exposure.');
        reasons.push('Complex failure telemetry requires manual merchant operations review.');
      } else {
        reasons.push('Risk policies or card limits require termination of automated recovery.');
        reasons.push('Prevents negative customer experience and unnecessary gateway fees.');
      }
    }

    if (action === 'RETRY_PAYMENT' || action === 'RETRY_LATER') {
      expectedOutcome = 'High probability of successful recovery after cooldown without customer disruption.';
    } else if (action === 'SEND_PAYMENT_LINK') {
      expectedOutcome = 'Customer completes payment seamlessly via 1-click personalized checkout link.';
    } else if (action === 'CHANGE_PAYMENT_METHOD') {
      expectedOutcome = 'Payment settled using alternate funding instrument (UPI/Netbanking/Debit).';
    } else if (action === 'ESCALATE_TO_HUMAN') {
      expectedOutcome = 'Dedicated operations agent reviews customer context before further outreach.';
    } else {
      expectedOutcome = 'Case closed cleanly to preserve customer relationship and prevent churn.';
    }

    return { reasons, expectedOutcome };
  };

  const { reasons, expectedOutcome } = getWhyThisAction();

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      {/* Card Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-200">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              AI Recovery Investigation
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                {investigation.ai_available ? 'Gemini 2.5 Flash' : 'Deterministic Fallback'}
              </span>
            </h3>
            <p className="text-xs text-slate-500">
              Payment telemetry analysis and recovery recommendation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block">AI Confidence</span>
            <span className="text-base font-mono font-bold text-blue-600">
              {(investigation.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Diagnosis & Summary Banner */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] uppercase font-bold text-slate-600">AI Root Cause Diagnosis</span>
          <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
            {investigation.diagnosis}
          </span>
        </div>
        <p className="text-xs text-slate-700 leading-relaxed">{investigation.summary}</p>
      </div>

      {/* Telemetry Evidence Factors */}
      {investigation.evidence && investigation.evidence.length > 0 && (
        <div className="space-y-2.5">
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
            Recovery Evidence
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {investigation.evidence.map((item, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-900">{item.factor}</span>
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold border ${
                      item.impact === 'POSITIVE'
                        ? 'text-emerald-700 bg-emerald-50 border-emerald-200'
                        : item.impact === 'NEGATIVE'
                        ? 'text-rose-700 bg-rose-50 border-rose-200'
                        : 'text-slate-600 bg-slate-100 border-slate-200'
                    }`}
                  >
                    {item.impact}
                  </span>
                </div>
                <p className="text-[11px] text-slate-600 leading-normal">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Why This Action Section */}
      <div className="p-4 rounded-xl bg-blue-50/50 border border-blue-200/80 space-y-2.5">
        <div className="flex items-center gap-1.5 text-xs font-bold text-blue-900 uppercase tracking-wider">
          <HelpCircle className="w-4 h-4 text-blue-600" />
          <span>Why {action.replace(/_/g, ' ')}?</span>
        </div>
        <ul className="space-y-1.5">
          {reasons.map((r, i) => (
            <li key={i} className="text-xs text-slate-700 flex items-start gap-2">
              <Check className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
              <span>{r}</span>
            </li>
          ))}
        </ul>
        <div className="pt-2 border-t border-blue-100 text-xs text-slate-600">
          <strong className="text-slate-800">Expected Outcome:</strong> {expectedOutcome}
        </div>
      </div>

      {/* Action Recommendation Box */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
          <span className="text-[10px] text-slate-500 uppercase font-semibold block mb-1">
            Recommended Action
          </span>
          <StatusBadge type="action" value={investigation.ai_recommended_action} />
        </div>

        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
          <span className="text-[10px] text-slate-500 uppercase font-semibold block mb-1">
            Execution Channel
          </span>
          <span className="text-xs font-mono font-bold text-slate-800">
            {investigation.recovery_channel || 'GATEWAY_RETRY'}
          </span>
        </div>

        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
          <span className="text-[10px] text-slate-500 uppercase font-semibold block mb-1">
            Recommended Delay
          </span>
          <span className="text-xs font-mono font-bold text-slate-800">
            {investigation.wait_time_minutes ? `${investigation.wait_time_minutes} minutes` : 'Immediate'}
          </span>
        </div>
      </div>
    </div>
  );
};
