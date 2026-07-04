import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Route, Switch } from 'wouter';
import LandingPage from '@/pages/landing';
import LoginPage from '@/pages/login';
import SignupPage from '@/pages/signup';
import DashboardPage from '@/pages/dashboard';
import NotFound from '@/pages/not-found';
import { ProtectedRoute, PublicOnlyRoute } from '@/components/protected-route';

const queryClient = new QueryClient();

function Router() {
  return (
    <Switch>
      <Route path="/">
        <PublicOnlyRoute><LandingPage /></PublicOnlyRoute>
      </Route>
      <Route path="/login">
        <PublicOnlyRoute><LoginPage /></PublicOnlyRoute>
      </Route>
      <Route path="/signup">
        <PublicOnlyRoute><SignupPage /></PublicOnlyRoute>
      </Route>
      <Route path="/dashboard">
        <ProtectedRoute><DashboardPage /></ProtectedRoute>
      </Route>
      <Route component={NotFound} />
    </Switch>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Router />
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}
