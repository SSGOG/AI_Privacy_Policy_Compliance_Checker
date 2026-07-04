import { cn } from '@/lib/utils';
import { STATUS_COLORS } from '@/lib/api';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const color = STATUS_COLORS[status] ?? '#7f8c8d';

  return (
    <span
      className={cn(
        'inline-flex items-center rounded px-2.5 py-0.5 text-xs font-semibold text-white',
        className,
      )}
      style={{ backgroundColor: color }}
    >
      {status}
    </span>
  );
}
