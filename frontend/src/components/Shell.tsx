'use client';
import Link from 'next/link';
import {usePathname} from 'next/navigation';
import {Activity, ClipboardList, Hospital, LayoutDashboard, ListChecks, Settings, Search, ShieldCheck} from 'lucide-react';
const entries=[{href:'/',label:'Overview',Icon:LayoutDashboard},{href:'/report',label:'Family report',Icon:ClipboardList},{href:'/hospital',label:'Hospital intake',Icon:Hospital},{href:'/matches',label:'Match review',Icon:Search},{href:'/tracking',label:'Report tracking',Icon:ListChecks},{href:'/admin',label:'Administration',Icon:Settings}];
export function Shell({children}:{children:React.ReactNode}){
 const pathname=usePathname();
 return <div className="min-h-screen lg:flex">
   <aside className="w-full lg:w-64 bg-[#101f39] text-white px-6 py-7 lg:min-h-screen">
     <Link href="/" className="text-2xl font-bold tracking-tight inline-flex gap-2 items-center"><Activity size={27} className="text-sky-400"/>reunify<span className="text-sky-400">.</span></Link>
     <div className="mt-1 text-xs text-slate-400">Crisis Response Platform</div>
     <div className="mt-8 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">Workspace</div>
     <nav aria-label="Main navigation" className="mt-3 grid grid-cols-2 gap-1 sm:grid-cols-3 lg:flex lg:flex-col">{entries.map(({href,label,Icon})=><Link key={href} href={href} aria-current={pathname===href?'page':undefined} className={'flex gap-3 items-center rounded-lg px-3 py-2.5 text-sm '+(pathname===href?'bg-blue-500 text-white':'text-slate-300 hover:bg-slate-800')}><Icon size={17}/>{label}</Link>)}</nav>
     <div className="mt-10 rounded-xl border border-slate-700 p-4 text-xs text-slate-300"><div className="flex items-center gap-2 text-white font-semibold"><ShieldCheck size={16}/> Demo workspace</div><p className="mt-2 leading-5">Synthetic cases only. No live patient data or identity verification.</p></div>
   </aside>
   <main className="flex-1 min-w-0 px-5 md:px-10 py-8 max-w-screen-2xl">{children}</main>
 </div>;
}
