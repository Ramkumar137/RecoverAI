export type PaymentStatus =
  | 'SUCCESS'
  | 'FAILED'
  | 'PENDING'
  | 'ABANDONED'
  | 'EXPIRED'
  | 'RECOVERED';

export type FailureReason =
  | 'INSUFFICIENT_FUNDS'
  | 'BANK_TIMEOUT'
  | 'CARD_DECLINED'
  | 'NETWORK_ERROR'
  | 'AUTHENTICATION_FAILED'
  | 'LIMIT_EXCEEDED'
  | 'UNKNOWN';

export interface Customer {
  id: number;
  customer_id: string;
  name: string;
  email: string;
  phone?: string | null;
  account_age_days: number;
  total_payments: number;
  successful_payments: number;
  failed_payments: number;
  average_payment_amount: number;
  created_at: string;
  updated_at: string;
}

export interface Merchant {
  id: number;
  merchant_id: string;
  name: string;
  business_category: string;
  api_key_prefix: string;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: number;
  payment_id: string;
  customer_id: number;
  merchant_id: number;
  amount: number | string;
  currency: string;
  payment_method: string;
  status: PaymentStatus;
  failure_reason?: FailureReason | string | null;
  retry_count: number;
  customer?: Customer | null;
  merchant?: Merchant | null;
  created_at: string;
  updated_at: string;
}

export interface PaymentFilterParams {
  skip?: number;
  limit?: number;
  status?: string;
  failure_reason?: string;
  search?: string;
}
