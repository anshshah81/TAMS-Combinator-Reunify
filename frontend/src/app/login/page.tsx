'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Activity, ShieldAlert } from 'lucide-react';
import { getDemoAccounts, type DemoAccount, type Role } from '@/lib/api';
import { useSession } from '@/components/SessionProvider';
import { Alert, Button } from '@/components/ui';

const HOME_BY_ROLE: Record<Role, string> = {
  family: '/report',
  hospital: '/hospital',
  reviewer: '/matches',
  admin: '/admin',
};

export default function LoginPage() {
  const router = useRouter();
  const { signIn } = useSession();
  const [accounts, setAccounts] = useState<DemoAccount[]>([]);
  const [enabled, setEnabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDemoAccounts()
      .then(result => { setAccounts(result.accounts); setEnabled(result.enabled); })
      .catch(() => setError('The demo API is unavailable. Start the backend on port 8000.'))
      .finally(() => setLoading(false));
  }, []);

  async function choose(account: DemoAccount) {
    setBusy(account.id);
    setError(null);
    try {
      const user = await signIn(account.id);
      router.push(HOME_BY_ROLE[user.role] ?? '/dashboard');
    } catch {
      setError('Sign-in failed. Please try again.');
      setBusy(null);
    }
  }

  return (
    <div className="min-h-screen bg-[#0b1526] text-white flex items-center justify-center px-5 py-12">
      <div className="w-full max-w-lg">
        <Link href="/" className="text-2xl font-bold tracking-tight inline-flex gap-2 items-center">
          <Activity size={26} className="text-sky-400" />reunify<span className="text-sky-400">.</span>
        </Link>
        <h1 className="mt-6 text-3xl font-bold tracking-tight">Demo sign in</h1>
        <p className="mt-2 text-slate-300 text-sm leading-6">
          Choose a fictional account to explore a role. This development-only sign-in grants no real access and is
          not a secure authentication system.
        </p>

        <div className="mt-8 bg-white text-slate-800 rounded-2xl p-6 shadow-sm">
          {loading && <p className="text-slate-500 text-sm">Loading demo accounts…</p>}
          {!loading && error && <Alert tone="error">{error}</Alert>}
          {!loading && !enabled && (
            <div className="text-sm text-slate-700">
              <div className="flex items-center gap-2 font-semibold text-amber-700"><ShieldAlert size={18} /> Demo sign-in is disabled</div>
              <p className="mt-2 leading-6 text-slate-600">
                The backend has <code>DEMO_AUTH_ENABLED</code> off. Enable development-only demo authentication to try
                the intake and tracking flows. You can still view the public <Link href="/dashboard" className="text-blue-600 font-semibold">incident dashboard</Link>.
              </p>
            </div>
          )}
          {!loading && enabled && accounts.length > 0 && (
            <ul className="grid gap-2">
              {accounts.map(account => (
                <li key={account.id}>
                  <Button variant="secondary" disabled={busy !== null} onClick={() => void choose(account)}
                    className="w-full flex items-center justify-between">
                    <span>{account.display_name}</span>
                    <span className="capitalize text-xs text-slate-500">{account.role}</span>
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <Link href="/dashboard" className="mt-6 inline-block text-sky-300 font-semibold text-sm">← Back to dashboard</Link>
      </div>
    </div>
  );
}
