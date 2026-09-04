import React from 'react';
import { Loader2 } from 'lucide-react';

interface Props {
  message?: string;
  submessage?: string;
  className?: string;
}

export const LoadingState: React.FC<Props> = ({
  message = 'Loading data...',
  submessage = 'Connecting to RecoverAI intelligence engine',
  className = 'min-h-[300px]',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${className}`}>
      <div className="relative mb-4">
        <div className="w-12 h-12 rounded-full border-2 border-blue-100 border-t-blue-600 animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <Loader2 className="w-5 h-5 text-blue-600 animate-pulse" />
        </div>
      </div>
      <h3 className="text-sm font-semibold text-slate-800">{message}</h3>
      <p className="text-xs text-slate-500 mt-1 max-w-sm">{submessage}</p>
    </div>
  );
};
