import React from 'react';
import { TimelineEvent } from '../../types';
import { formatDate } from '../../utils/formatters';
import {
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  Zap,
  Play,
  Clock,
} from 'lucide-react';

interface Props {
  events: TimelineEvent[];
}

export const RecoveryTimeline: React.FC<Props> = ({ events }) => {
  const getActorInfo = (actor: string, event: string) => {
    const act = (actor || '').toUpperCase();
    const evt = (event || '').toUpperCase();

    if (evt.includes('RECOVERED') || evt.includes('SUCCESS')) {
      return {
        icon: CheckCircle,
        color: 'text-emerald-700 bg-emerald-50 border-emerald-300',
        badge: 'SETTLED',
      };
    }
    if (act.includes('GEMINI') || act.includes('AI')) {
      return {
        icon: Sparkles,
        color: 'text-blue-700 bg-blue-50 border-blue-300',
        badge: 'AI RECOVERY',
      };
    }
    if (act.includes('POLICY')) {
      return {
        icon: ShieldCheck,
        color: 'text-indigo-700 bg-indigo-50 border-indigo-300',
        badge: 'POLICY ENGINE',
      };
    }
    if (act.includes('SIMULATOR')) {
      return {
        icon: Zap,
        color: 'text-amber-700 bg-amber-50 border-amber-300',
        badge: 'GATEWAY SIMULATOR',
      };
    }
    if (act.includes('EXECUTION')) {
      return {
        icon: Play,
        color: 'text-cyan-700 bg-cyan-50 border-cyan-300',
        badge: 'WORKFLOW ENGINE',
      };
    }
    return {
      icon: Clock,
      color: 'text-slate-600 bg-slate-100 border-slate-300',
      badge: actor || 'SYSTEM',
    };
  };

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">
            Recovery Audit Timeline
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Trace from initial payment failure signal to recovery resolution
          </p>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-slate-100 text-[11px] font-mono font-semibold text-slate-700 border border-slate-200">
          {events.length} Events Logged
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {events.map((ev, index) => {
          const info = getActorInfo(ev.actor, ev.event);
          const Icon = info.icon;
          return (
            <div key={index} className="relative group">
              {/* Dot */}
              <div
                className={`absolute -left-[1.85rem] top-1 w-6 h-6 rounded-full border flex items-center justify-center ${info.color} shadow-sm`}
              >
                <Icon className="w-3 h-3" />
              </div>

              {/* Event Content Box */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors space-y-1.5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-900 tracking-wide">
                      {ev.event}
                    </span>
                    <span className="text-[10px] uppercase font-bold font-mono px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200 shadow-sm">
                      {info.badge}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-500">
                    {formatDate(ev.timestamp)}
                  </span>
                </div>

                <p className="text-xs text-slate-700 leading-relaxed">{ev.description}</p>

                {ev.metadata && Object.keys(ev.metadata).length > 0 && (
                  <div className="pt-2 mt-2 border-t border-slate-200/80 flex flex-wrap gap-2 text-[10px] font-mono text-slate-600">
                    {Object.entries(ev.metadata).map(([k, v]) => (
                      <span key={k} className="px-2 py-0.5 rounded bg-white border border-slate-200">
                        {k}: <strong className="text-slate-900">{String(v)}</strong>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
