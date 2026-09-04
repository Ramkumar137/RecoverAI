import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  RotateCcw,
  CreditCard,
  BarChart3,
  ClipboardList,
  ShieldCheck,
  TrendingUp,
} from 'lucide-react';

interface Props {
  apiConnected: boolean;
}

export const Sidebar: React.FC<Props> = ({ apiConnected }) => {
  const location = useLocation();

  const navItems = [
    {
      id: 'dashboard',
      path: '/dashboard',
      label: 'Overview',
      icon: LayoutDashboard,
      description: 'Recovery KPIs and opportunities',
    },
    {
      id: 'recovery',
      path: '/recovery',
      label: 'Recovery Cases',
      icon: RotateCcw,
      description: 'AI recommendations and recovery execution',
    },
    {
      id: 'payments',
      path: '/payments',
      label: 'Payments',
      icon: CreditCard,
      description: 'Payment history and failure signals',
    },
    {
      id: 'analytics',
      path: '/analytics',
      label: 'Analytics',
      icon: BarChart3,
      description: 'Recovery performance and strategy ROI',
    },
    {
      id: 'audit',
      path: '/audit',
      label: 'Audit Trail',
      icon: ClipboardList,
      description: 'AI and policy decisions',
    },
  ];

  const isActive = (path: string) => {
    if (path === '/dashboard' && (location.pathname === '/' || location.pathname === '/dashboard')) {
      return true;
    }
    if (path === '/recovery' && location.pathname.startsWith('/recovery')) {
      return true;
    }
    return location.pathname === path;
  };

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col flex-shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-200">
        <Link to="/dashboard" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center shadow-sm group-hover:bg-blue-700 transition-colors">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-base font-bold tracking-tight text-slate-900">RecoverAI</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium">AI Revenue Recovery</p>
          </div>
        </Link>
      </div>

      {/* Product Question Core Notice */}
      <div className="mx-4 mt-4 p-3 rounded-lg bg-slate-50 border border-slate-200 text-left">
        <span className="text-[10px] font-semibold text-blue-700 uppercase tracking-wider block">Core Question</span>
        <p className="text-[11px] text-slate-700 font-medium leading-snug mt-1">
          &ldquo;How much revenue can we recover, and what should we do next?&rdquo;
        </p>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const active = isActive(item.path);
          const Icon = item.icon;
          return (
            <Link
              key={item.id}
              to={item.path}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-left transition-colors ${
                active
                  ? 'bg-blue-50 text-blue-700 font-semibold border border-blue-200 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-medium'
              }`}
            >
              <Icon className={`w-4 h-4 flex-shrink-0 ${active ? 'text-blue-600' : 'text-slate-400'}`} />
              <div className="flex flex-col min-w-0">
                <span className="text-xs leading-tight">{item.label}</span>
                <span className="text-[10px] text-slate-500 truncate mt-0.5">{item.description}</span>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Safety Principle Box */}
      <div className="p-3.5 mx-3 mb-3 rounded-lg bg-slate-50 border border-slate-200 text-left">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800 mb-1">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
          <span>Safety Principle</span>
        </div>
        <p className="text-[11px] text-slate-600 leading-relaxed">
          <strong className="text-slate-800">AI recommends.</strong> Deterministic policy controls execution.
        </p>
      </div>

      {/* Footer System Status */}
      <div className="p-3.5 border-t border-slate-200 bg-slate-50/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${apiConnected ? 'bg-emerald-500' : 'bg-rose-500'}`} />
          <span className="text-[11px] font-medium text-slate-700">
            {apiConnected ? 'Recovery Engine Active' : 'Connecting...'}
          </span>
        </div>
        <span className="text-[10px] font-semibold text-slate-500 uppercase px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200">
          Simulated
        </span>
      </div>
    </aside>
  );
};
