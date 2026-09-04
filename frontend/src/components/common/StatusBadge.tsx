import React from 'react';
import { getStatusBadge, getActionBadge, getScoreTier, getPriorityBadge } from '../../utils/badges';

interface Props {
  type: 'status' | 'action' | 'score' | 'priority';
  value: string | number;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<Props> = ({ type, value, size = 'sm' }) => {
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs';

  if (type === 'score') {
    const num = Number(value);
    const tier = getScoreTier(num);
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-full font-mono font-bold border ${tier.bg} ${tier.color} ${tier.border} ${sizeClasses}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-current" />
        {num.toFixed(1)}% ({tier.label})
      </span>
    );
  }

  if (type === 'priority') {
    const p = String(value).toUpperCase() as 'HIGH' | 'MEDIUM' | 'LOW';
    const info = getPriorityBadge(p === 'HIGH' || p === 'MEDIUM' ? p : 'LOW');
    return (
      <span className={`inline-flex items-center gap-1 rounded-full font-semibold border ${info.bg} ${info.text} ${info.border} ${sizeClasses}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-current" />
        {info.label} Priority
      </span>
    );
  }

  if (type === 'action') {
    const info = getActionBadge(String(value));
    return (
      <span className={`inline-flex items-center rounded-md font-medium border ${info.bg} ${info.text} ${info.border} ${sizeClasses}`}>
        {info.label}
      </span>
    );
  }

  const info = getStatusBadge(String(value));
  return (
    <span className={`inline-flex items-center gap-1 rounded-full font-semibold uppercase tracking-wider border ${info.bg} ${info.text} ${info.border} ${sizeClasses}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {info.label}
    </span>
  );
};
