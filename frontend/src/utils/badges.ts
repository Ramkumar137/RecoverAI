export function getStatusBadge(status: string): { bg: string; text: string; border: string; label: string } {
  const s = (status || '').toUpperCase();
  switch (s) {
    case 'RECOVERED':
    case 'SUCCESS':
      return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', label: 'Recovered' };
    case 'ACTION_APPROVED':
    case 'APPROVED':
    case 'ALLOWED':
      return { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', label: 'Action Approved' };
    case 'INVESTIGATING':
      return { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200', label: 'Investigating' };
    case 'ACTION_EXECUTED':
      return { bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-200', label: 'Action Executed' };
    case 'RECOVERY_RECOMMENDED':
      return { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', label: 'Recommended' };
    case 'PENDING':
      return { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', label: 'Pending' };
    case 'ESCALATED':
    case 'ESCALATE_TO_HUMAN':
      return { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', label: 'Escalated' };
    case 'STOPPED':
    case 'STOP_RECOVERY':
    case 'CLOSED':
      return { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200', label: 'Stopped' };
    case 'FAILED':
    case 'DENIED':
      return { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200', label: 'Failed' };
    case 'ABANDONED':
      return { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200', label: 'Abandoned' };
    case 'EXPIRED':
      return { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200', label: 'Expired' };
    case 'OPEN':
    default:
      return { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', label: s || 'Open' };
  }
}

export function getScoreTier(score: number): { label: 'HIGH' | 'MEDIUM' | 'LOW'; color: string; bg: string; border: string } {
  if (score >= 70) {
    return { label: 'HIGH', color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200' };
  }
  if (score >= 30) {
    return { label: 'MEDIUM', color: 'text-amber-800', bg: 'bg-amber-50', border: 'border-amber-200' };
  }
  return { label: 'LOW', color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-200' };
}

export function getActionBadge(action: string): { bg: string; text: string; border: string; label: string } {
  const a = (action || '').toUpperCase();
  switch (a) {
    case 'RETRY_PAYMENT':
      return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', label: 'Retry Payment' };
    case 'RETRY_LATER':
      return { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200', label: 'Retry Later' };
    case 'SEND_PAYMENT_LINK':
      return { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', label: 'Send Payment Link' };
    case 'SEND_REMINDER':
      return { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200', label: 'Send Reminder' };
    case 'CHANGE_PAYMENT_METHOD':
      return { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', label: 'Change Method' };
    case 'ESCALATE_TO_HUMAN':
      return { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', label: 'Escalate to Ops' };
    case 'STOP_RECOVERY':
      return { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200', label: 'Stop Recovery' };
    default:
      return { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200', label: action || 'None' };
  }
}

export function calculateRecoveryPriority(amount: number, score: number, retryCount: number = 0): 'HIGH' | 'MEDIUM' | 'LOW' {
  if (retryCount >= 3 || score < 20) return 'LOW';
  if (score >= 70 && amount >= 2500) return 'HIGH';
  if (score >= 40 || amount >= 5000) return 'MEDIUM';
  return 'LOW';
}

export function getPriorityBadge(priority: 'HIGH' | 'MEDIUM' | 'LOW'): { bg: string; text: string; border: string; label: string } {
  switch (priority) {
    case 'HIGH':
      return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', label: 'High' };
    case 'MEDIUM':
      return { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', label: 'Medium' };
    case 'LOW':
    default:
      return { bg: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200', label: 'Low' };
  }
}
