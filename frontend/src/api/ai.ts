import { apiClient } from './client';
import { AIInvestigation } from '../types';

export const aiApi = {
  investigate: async (paymentId: string | number, forceRefresh = false): Promise<AIInvestigation> => {
    const res = await apiClient.post<AIInvestigation>(
      `/ai/investigate/${paymentId}?force_refresh=${forceRefresh}`
    );
    return res.data;
  },

  getReport: async (paymentId: string | number): Promise<AIInvestigation> => {
    const res = await apiClient.get<AIInvestigation>(`/ai/investigations/${paymentId}`);
    return res.data;
  },
};
