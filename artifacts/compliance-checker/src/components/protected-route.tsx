import { Navigate } from '@/lib/navigate';
import { isAuthenticated } from '@/lib/api';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  if (!isAuthenticated()) {
    return <Navigate href="/login" />;
  }
  return <>{children}</>;
}

interface PublicOnlyRouteProps {
  children: React.ReactNode;
}

export function PublicOnlyRoute({ children }: PublicOnlyRouteProps) {
  if (isAuthenticated()) {
    return <Navigate href="/dashboard" />;
  }
  return <>{children}</>;
}
