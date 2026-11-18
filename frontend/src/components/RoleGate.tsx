'use client';

import Link from 'next/link';
import type { Role } from '@/lib/api';
import { useSession } from '@/components/SessionProvider';
import { Shell } from '@/components/Shell';
import { Alert } from '@/components/ui';

// Client-side gating is a convenience only; the backend remains the authority
// and rejects unauthorized requests regardless of what the UI renders.
export function RoleGate({ role, children }: { role: Role | Role[]; children: React.ReactNode }) {
  const { user, loading } = useSession();
  const allowed = Array.isArray(role) ? role : [role];

  if (loading) {
    return <Shell><p role="status" className="text-slate-600">Checking your session…</p></Shell>;
  }
  if (!user) {
    return (
      <Shell>
        <Alert tone="info">
          Please <Link href="/login" className="font-semibold underline">sign in</Link> to use this page.
        </Alert>
      </Shell>
    );
  }
  if (!allowed.includes(user.role)) {
    return (
      <Shell>
        <Alert tone="error">
          This page is for {allowed.join(' or ')} accounts. You are signed in as a {user.role} account.
        </Alert>
      </Shell>
    );
  }
  return <>{children}</>;
}
