export type DueDateStatus = 'overdue' | 'today' | 'upcoming' | 'none';

export function getDueDateStatus(dueDate: number | null): DueDateStatus {
  if (!dueDate) return 'none';

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);

  const diffTime = due.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return 'overdue';
  if (diffDays === 0) return 'today';
  return 'upcoming';
}

export function getRelativeDueDateText(dueDate: number | null): string {
  if (!dueDate) return '';

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);

  const diffTime = due.getTime() - today.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    const absDays = Math.abs(diffDays);
    return `期限切れ（${absDays}日前）`;
  }
  if (diffDays === 0) return '今日';
  if (diffDays === 1) return '明日';
  if (diffDays === 2) return '明後日';
  if (diffDays <= 7) return `${diffDays}日後`;
  if (diffDays <= 30) return `約${Math.ceil(diffDays / 7)}週間後`;
  return `約${Math.ceil(diffDays / 30)}ヶ月後`;
}

export function formatDate(timestamp: number): string {
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `${year}/${month}/${day}`;
}

export function isOverdue(dueDate: number | null): boolean {
  return getDueDateStatus(dueDate) === 'overdue';
}

export function isToday(dueDate: number | null): boolean {
  return getDueDateStatus(dueDate) === 'today';
}
