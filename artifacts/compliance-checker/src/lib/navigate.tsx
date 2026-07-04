import { useLocation } from 'wouter';

interface NavigateProps {
  href: string;
}

export function Navigate({ href }: NavigateProps) {
  const [, setLocation] = useLocation();
  setLocation(href);
  return null;
}
