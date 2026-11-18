'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Activity, ClipboardList, Hospital, LayoutDashboard, ListChecks, LogOut, Search, Settings, ShieldCheck } from 'lucide-react';
import type { Role } from '@/lib/api';
import { useSession } from '@/components/SessionProvider';

type Entry = { href: string; label: string; Icon: typeof Activity; roles?: Role[] };

const entries: Entry[] = [
  { href: '/dashboard', label: 'Overview', Icon: LayoutDashboard },
  { href: '/report', label: 'Family report', Icon: ClipboardList, roles: ['family'] },
  { href: '/tracking', label: 'Report tracking', Icon: ListChecks, roles: ['family'] },
  { href: '/hospital', label: 'Hospital intake', Icon: Hospital, roles: ['hospital'] },
  { href: '/matches', label: 'Match review', Icon: Search, roles: ['reviewer', 'admin'] },
  { href: '/admin', label: 'Administration', Icon: Settings, roles: ['admin'] },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, signOut } = useSession();
  const visible = entries.filter(entry => !entry.roles || (user && entry.roles.includes(user.role)));

  return (
    <div className="min-h-screen lg:flex">
      <aside className="w-full lg:w-64 bg-[#101f39] text-white px-6 py-7 lg:min-h-screen">
        <Link href="/" className="text-2xl font-bold tracking-tight inline-flex gap-2 items-center">
          <Activity size={27} className="text-sky-400" />reunify<span className="text-sky-400">.</span>
        </Link>
        <div className="mt-1 text-xs text-slate-400">Crisis Response Platform</div>
        <div className="mt-8 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">Workspace</div>
        <nav aria-label="Main navigation" className="mt-3 grid grid-cols-2 gap-1 sm:grid-cols-3 lg:flex lg:flex-col">
          {visible.map(({ href, label, Icon }) => (
            <Link key={href} href={href} aria-current={pathname === href ? 'page' : undefined}
              className={'flex gap-3 items-center rounded-lg px-3 py-2.5 text-sm ' + (pathname === href ? 'bg-blue-500 text-white' : 'text-slate-300 hover:bg-slate-800')}>
              <Icon size={17} />{label}
            </Link>
          ))}
        </nav>
        <div className="mt-8 rounded-xl border border-slate-700 p-4 text-xs text-slate-300">
          {loading ? (
            <p className="text-slate-400">Checking session…</p>
          ) : user ? (
            <div>
              <div className="text-white font-semibold">{user.display_name}</div>
              <div className="mt-0.5 capitalize text-slate-400">{user.role} account (demo)</div>
              <button onClick={() => { void signOut().then(() => router.push('/')); }}
                className="mt-3 inline-flex items-center gap-2 text-sky-300 font-semibold">
                <LogOut size={14} /> Sign out
              </button>
            </div>
          ) : (
            <div>
              <div className="flex items-center gap-2 text-white font-semibold"><ShieldCheck size={16} /> Not signed in</div>
              <Link href="/login" className="mt-2 inline-block text-sky-300 font-semibold">Demo sign in →</Link>
            </div>
          )}
        </div>
        <div className="mt-6 text-[11px] leading-5 text-slate-400">Synthetic cases only. No live patient data or identity verification.</div>
      </aside>
      <main className="flex-1 min-w-0 px-5 md:px-10 py-8 max-w-screen-2xl">{children}</main>
    </div>
  );
}
