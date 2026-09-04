import { apiClient } from './client';
import { Payment, PaymentFilterParams } from '../types';

export const paymentsApi = {
  list: async (params?: PaymentFilterParams): Promise<Payment[]> => {
    const query = new URLSearchParams();
    if (params?.skip !== undefined) query.set('skip', params.skip.toString());
    if (params?.limit !== undefined) query.set('limit', params.limit.toString());
    if (params?.status) query.set('status', params.status);
    if (params?.failure_reason) query.set('failure_reason', params.failure_reason);
    if (params?.search) query.set('search', params.search);

    const qs = query.toString();
    const res = await apiClient.get<Payment[]>(`/payments${qs ? `?${qs}` : ''}`);
    return res.data;
  },

  getById: async (paymentId: string | number): Promise<Payment> => {
    const res = await apiClient.get<Payment>(`/payments/${paymentId}`);
    return res.data;
  },
};
