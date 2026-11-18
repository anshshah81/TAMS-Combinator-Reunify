import Link from 'next/link';
import { Activity, ClipboardList, Hospital, ShieldCheck, Search, UserCheck } from 'lucide-react';

const steps = [
  { Icon: ClipboardList, title: 'Families report', body: 'A family describes a missing loved one, their appearance and last-known location, with explicit consent.' },
  { Icon: Hospital, title: 'Hospitals record', body: 'Authorized staff log unidentified patients and observed details within their own organization.' },
  { Icon: Search, title: 'Reunify suggests', body: 'Transparent matching surfaces possible connections as ranked evidence — never a confirmed identity.' },
  { Icon: UserCheck, title: 'People decide', body: 'Trained reviewers investigate, compare records, and independently verify. AI never verifies or contacts families.' },
];

export default function Landing() {
  return (
    <div className="min-h-screen">
      <header className="bg-[#101f39] text-white">
        <div className="max-w-screen-xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="text-2xl font-bold tracking-tight inline-flex gap-2 items-center">
            <Activity size={26} className="text-sky-400" />reunify<span className="text-sky-400">.</span>
          </div>
          <nav className="flex items-center gap-3 text-sm">
            <Link href="/dashboard" className="text-slate-200 hover:text-white px-3 py-2">Incident dashboard</Link>
            <Link href="/login" className="rounded-lg bg-white/10 border border-white/20 px-3 py-2 font-semibold hover:bg-white/20">Authorized staff login</Link>
          </nav>
        </div>
        <div className="max-w-screen-xl mx-auto px-6 pb-16 pt-10">
          <span className="rounded-full bg-sky-500/20 text-sky-200 border border-sky-400/30 px-3 py-1.5 text-xs font-semibold inline-flex gap-2 items-center">
            <ShieldCheck size={15} /> Synthetic demonstration · Not a production medical system
          </span>
          <h1 className="mt-6 text-4xl md:text-5xl font-bold tracking-tight max-w-3xl leading-tight">
            Helping authorized teams reunite families after a disaster
          </h1>
          <p className="mt-5 text-slate-300 text-lg max-w-2xl leading-8">
            Reunify connects family missing-person reports with unidentified-patient records and gives trained
            reviewers ranked evidence to investigate. Human reviewers make every identification decision.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/report" className="rounded-lg bg-blue-600 hover:bg-blue-700 px-5 py-3 font-semibold">Report a missing person</Link>
            <Link href="/login" className="rounded-lg bg-white text-slate-900 hover:bg-slate-100 px-5 py-3 font-semibold">Authorized staff login</Link>
          </div>
        </div>
      </header>

      <main className="max-w-screen-xl mx-auto px-6 py-14">
        <h2 className="text-2xl font-bold tracking-tight">How matching works</h2>
        <p className="text-slate-600 mt-2 max-w-2xl">
          Reunify treats facial and clothing signals as uncertain evidence, not proof. It distinguishes missing
          information from conflicting information and supports a &ldquo;no confident match&rdquo; outcome.
        </p>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {steps.map(({ Icon, title, body }) => (
            <section key={title} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
              <div className="bg-blue-50 text-blue-600 rounded-lg p-3 w-fit"><Icon size={22} /></div>
              <h3 className="font-semibold text-lg mt-4">{title}</h3>
              <p className="text-slate-600 text-sm mt-2 leading-6">{body}</p>
            </section>
          ))}
        </div>

        <div className="mt-12 bg-[#101f39] rounded-2xl text-white p-8">
          <h2 className="font-semibold text-xl">A clear principle</h2>
          <p className="text-slate-300 mt-3 max-w-3xl leading-7">
            AI suggests potential matches. Authorized human reviewers investigate and independently verify identity.
            The system never automatically confirms identity, discloses sensitive patient information to families,
            or notifies anyone on its own.
          </p>
        </div>
      </main>

      <footer className="border-t border-slate-200">
        <div className="max-w-screen-xl mx-auto px-6 py-8 text-sm text-slate-500">
          Training and demonstration only. All people, incidents, and photographs are fictional or consented.
          Never upload real patient information.
        </div>
      </footer>
    </div>
  );
}
