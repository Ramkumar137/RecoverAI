import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { RecoveryTrendPoint } from '../../types';
import { formatINRCompact, formatINR, formatShortDate } from '../../utils/formatters';

interface Props {
  data: RecoveryTrendPoint[];
}

export const RecoveryTrendChart: React.FC<Props> = ({ data }) => {
  return (
    <div className="rounded-xl bg-white border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">
            Revenue Recovery Over Time
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            14-day daily time-series: Revenue at Risk vs. Recovered Revenue &bull; <span className="text-slate-400">Synthetic recovery dataset</span>
          </p>
        </div>
      </div>

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorRecovered" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#059669" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#059669" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatShortDate}
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#e2e8f0' }}
            />
            <YAxis
              tickFormatter={(v) => formatINRCompact(v)}
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              width={70}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                borderColor: '#e2e8f0',
                borderRadius: '0.5rem',
                fontSize: '12px',
                color: '#0f172a',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
              }}
              formatter={(value: any, name: any) => [
                formatINR(value),
                name === 'revenue_at_risk' ? 'Revenue at Risk' : 'Recovered Revenue',
              ]}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend
              verticalAlign="top"
              align="right"
              wrapperStyle={{ fontSize: '11px', paddingBottom: '10px' }}
              formatter={(value) => (value === 'revenue_at_risk' ? 'Revenue at Risk' : 'Recovered Revenue')}
            />
            <Area
              type="monotone"
              dataKey="revenue_at_risk"
              stroke="#f43f5e"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorRisk)"
            />
            <Area
              type="monotone"
              dataKey="recovered"
              stroke="#059669"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorRecovered)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
