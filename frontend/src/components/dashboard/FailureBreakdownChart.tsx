import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { FailureBreakdownItem } from '../../types';
import { formatINRCompact, formatINR } from '../../utils/formatters';

interface Props {
  data: FailureBreakdownItem[];
}

export const FailureBreakdownChart: React.FC<Props> = ({ data }) => {
  const sorted = [...data]
    .filter((d) => d.failure_reason !== 'NONE' && d.failure_reason !== 'SUCCESS')
    .sort((a, b) => b.amount_at_risk - a.amount_at_risk)
    .slice(0, 6);

  const colors = ['#e11d48', '#ea580c', '#d97706', '#2563eb', '#4f46e5', '#7c3aed'];

  return (
    <div className="rounded-xl bg-white border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">Failure Root Cause Breakdown</h3>
          <p className="text-xs text-slate-500 mt-0.5">Top payment decline reasons by revenue impact &bull; <span className="text-slate-400">Synthetic recovery dataset</span></p>
        </div>
      </div>

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={sorted}
            layout="vertical"
            margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
            <XAxis
              type="number"
              tickFormatter={(v) => formatINRCompact(v)}
              stroke="#94a3b8"
              fontSize={10}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              type="category"
              dataKey="failure_reason"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              width={120}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                borderColor: '#e2e8f0',
                borderRadius: '0.5rem',
                fontSize: '11px',
                color: '#0f172a',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              }}
              formatter={(val: any) => [formatINR(val), 'Amount at Risk']}
            />
            <Bar dataKey="amount_at_risk" radius={[0, 4, 4, 0]}>
              {sorted.map((_, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
