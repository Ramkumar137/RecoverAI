import React, { useState, useEffect } from 'react';
import { CreditCard, RefreshCw } from 'lucide-react';
import { paymentsApi } from '../api';
import { Payment } from '../types';
import { PageContainer } from '../components/layout/PageContainer';
import { PaymentTable } from '../components/payments/PaymentTable';
import { PaymentFilters } from '../components/payments/PaymentFilters';
import { LoadingState } from '../components/common/LoadingState';
import { ErrorState } from '../components/common/ErrorState';
import { EmptyState } from '../components/common/EmptyState';

export const Payments: React.FC = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [failureReason, setFailureReason] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPayments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await paymentsApi.list({
        limit: 100,
        status: status || undefined,
        failure_reason: failureReason || undefined,
        search: search || undefined,
      });
      setPayments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load payments ledger');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadPayments();
    }, 250);
    return () => clearTimeout(timer);
  }, [search, status, failureReason]);

  const handleReset = () => {
    setSearch('');
    setStatus('');
    setFailureReason('');
  };

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-blue-600" />
            Payments Ledger
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Payment history, failure signals, and recovery status
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-medium text-slate-600 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm">
            {payments.length} Transactions Listed
          </span>
          <button
            onClick={loadPayments}
            className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 shadow-sm transition-colors"
            title="Reload ledger"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>
      </div>

      <PaymentFilters
        search={search}
        onSearchChange={setSearch}
        status={status}
        onStatusChange={setStatus}
        failureReason={failureReason}
        onFailureReasonChange={setFailureReason}
        onReset={handleReset}
      />

      {isLoading ? (
        <LoadingState message="Fetching payments ledger..." />
      ) : error ? (
        <ErrorState message={error} onRetry={loadPayments} />
      ) : payments.length === 0 ? (
        <EmptyState
          title="No Transactions Found"
          message="Try adjusting your search criteria or clearing active filters."
          actionText="Clear Filters"
          onAction={handleReset}
        />
      ) : (
        <PaymentTable payments={payments} />
      )}
    </PageContainer>
  );
};
