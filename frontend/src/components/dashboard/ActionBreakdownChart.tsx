import React from 'react';
import { ActionBreakdownItem } from '../../types';
import { formatINR } from '../../utils/formatters';
import { getActionBadge } from '../../utils/badges';

interface Props {
  data: ActionBreakdownItem[];
}

export const ActionBreakdownChart: React.FC<Props> = ({ data }) => {
  return (
    <div className="rounded-xl bg-white border border-slate-200 p-6 shadow-sm space-y-4">
      <div>
        <h3 className="text-sm font-bold text-slate-900 tracking-tight">Recovery Action Strategy Performance</h3>
        <p className="text-xs text-slate-500 mt-0.5">Which recovery actions actually yield revenue conversions? &bull; <span className="text-slate-400">Synthetic recovery dataset</span></p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
            <tr>
              <th className="px-4 py-2.5">Recovery Strategy</th>
              <th className="px-4 py-2.5 text-center">Attempts</th>
              <th className="px-4 py-2.5 text-center">Recovered</th>
              <th className="px-4 py-2.5 text-right">Amount Salvaged</th>
              <th className="px-4 py-2.5 text-right">Success Rate</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {data.map((item, index) => {
              const info = getActionBadge(item.action);
              const rate = item.attempts > 0 ? (item.successful / item.attempts) * 100 : 0;
              return (
                <tr key={index} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-4 py-2.5 font-medium">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-[11px] font-semibold ${info.bg} ${info.text} ${info.border}`}>
                      {info.label}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-center font-mono font-medium text-slate-700">
                    {item.attempts}
                  </td>
                  <td className="px-4 py-2.5 text-center font-mono font-semibold text-emerald-700">
                    {item.successful}
                  </td>
                  <td className="px-4 py-2.5 text-right font-mono font-bold text-slate-900">
                    {formatINR(item.recovered_amount)}
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <span className={`font-mono font-bold text-xs ${
                      rate >= 40 ? 'text-emerald-700' : rate >= 20 ? 'text-amber-800' : 'text-slate-500'
                    }`}>
                      {rate.toFixed(1)}%
                    </span>
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
