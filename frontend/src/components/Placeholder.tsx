import {Shell} from '@/components/Shell';
import Link from 'next/link';
export function Placeholder({title,description,phase}:{title:string;description:string;phase:number}){
 return <Shell><div className="text-xs font-semibold uppercase tracking-widest text-blue-600">Reunify / Development roadmap</div><h1 className="text-4xl font-bold mt-3">{title}</h1><p className="text-slate-500 mt-3 max-w-2xl">{description}</p><div className="mt-8 bg-white border border-slate-200 rounded-2xl p-8 max-w-2xl"><div className="text-xs uppercase font-bold tracking-widest text-blue-600">Planned for phase {phase}</div><h2 className="font-semibold text-xl mt-2">Under development</h2><p className="mt-3 text-slate-500 text-sm leading-6">This screen is a placeholder in Phase 1. There are no working intake, patient-data, model-inference or identity-verification functions yet.</p><Link href="/" className="inline-block mt-5 text-blue-600 font-semibold text-sm">← Back to dashboard</Link></div></Shell>;
}
