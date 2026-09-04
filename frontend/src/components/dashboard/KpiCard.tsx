import React from 'react';
import { LucideIcon } from 'lucide-react';

interface Props {
  title: string;
  value: string;
  subtitle?: string;
  badgeText?: string;
  badgeType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  colorScheme?: 'rose' | 'amber' | 'emerald' | 'sky' | 'purple' | 'slate';
  secondaryValue?: string;
}

export const KPICard: React.FC<Props> = ({
  title,
  value,
  subtitle,
  badgeText,
  badgeType = 'neutral',
  icon: Icon,
  colorScheme = 'sky',
  secondaryValue,
}) => {
  const schemeStyles = {
    rose: {
      border: 'border-slate-200 hover:border-rose-300',
      iconBg: 'bg-rose-50 text-rose-600 border border-rose-200',
      badge: 'bg-rose-50 text-rose-700 border-rose-200',
    },
    amber: {
      border: 'border-slate-200 hover:border-amber-300',
      iconBg: 'bg-amber-50 text-amber-600 border border-amber-200',
      badge: 'bg-amber-50 text-amber-700 border-amber-200',
    },
    emerald: {
      border: 'border-slate-200 hover:border-emerald-300',
      iconBg: 'bg-emerald-50 text-emerald-600 border border-emerald-200',
      badge: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    sky: {
      border: 'border-slate-200 hover:border-blue-300',
      iconBg: 'bg-blue-50 text-blue-600 border border-blue-200',
      badge: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    purple: {
      border: 'border-slate-200 hover:border-purple-300',
      iconBg: 'bg-purple-50 text-purple-600 border border-purple-200',
      badge: 'bg-purple-50 text-purple-700 border-purple-200',
    },
    slate: {
      border: 'border-slate-200 hover:border-slate-300',
      iconBg: 'bg-slate-100 text-slate-600 border border-slate-200',
      badge: 'bg-slate-100 text-slate-700 border-slate-200',
    },
  }[colorScheme];

  return (
    <div className={`relative overflow-hidden rounded-xl bg-white border ${schemeStyles.border} p-5 shadow-sm transition-all duration-200 hover:shadow`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-500 tracking-wider uppercase">{title}</span>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${schemeStyles.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="space-y-0.5">
        <div className="text-2xl font-bold tracking-tight text-slate-900 font-mono">{value}</div>
        {secondaryValue && (
          <div className="text-xs font-mono text-slate-500">{secondaryValue}</div>
        )}
      </div>

      {(subtitle || badgeText) && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
          {subtitle && (
            <span className="text-[11px] text-slate-500 truncate">{subtitle}</span>
          )}
          {badgeText && (
            <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${schemeStyles.badge} flex-shrink-0`}>
              {badgeText}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
