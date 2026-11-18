'use client';

import { useEffect, useState } from 'react';
import { Shell } from '@/components/Shell';
import { loadDashboard, type Incident, type Overview } from '@/lib/api';
import { Activity, Users, Hospital, Search, CloudRain, ShieldCheck, ListChecks, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState('');
  const [status, setStatus] = useState('all');

  useEffect(() => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    let mounted = true;
    setLoading(true);
    setError(false);
    loadDashboard(controller.signal)
      .then(([totals, rows]) => {
        if (mounted) { setOverview(totals); setIncidents(rows); }
      })
      .catch(() => { if (mounted) setError(true); })
      .finally(() => { clearTimeout(timeout); if (mounted) setLoading(false); });
    return () => { mounted = false; clearTimeout(timeout); controller.abort(); };
  }, [attempt]);

  const filtered = incidents.filter(incident =>
    (status === 'all' || incident.status === status) &&
    `${incident.name} ${incident.affected_region}`.toLowerCase().includes(query.trim().toLowerCase()),
  );
  const cards = [
    { label: 'Active incidents', value: overview?.incident_count, Icon: Activity },
    { label: 'Missing-person reports', value: overview?.missing_reports, Icon: Users },
    { label: 'Unidentified patients', value: overview?.hospital_records, Icon: Hospital },
    { label: 'Suggested matches', value: overview?.suggested_matches, Icon: Search },
    { label: 'Needing investigation', value: overview?.candidates_needing_review, Icon: ListChecks },
    { label: 'Verified resolutions', value: overview?.verified_resolutions, Icon: CheckCircle },
  ];

  return <Shell>
    <div className="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <div className="text-xs font-semibold uppercase tracking-widest text-blue-600">Operations center · Synthetic demo</div>
        <h1 className="text-3xl md:text-4xl mt-2 font-bold tracking-tight">Incident overview</h1>
        <p className="text-slate-600 mt-2">A shared picture of fictional disaster response exercises.</p>
      </div>
      <span className="rounded-full bg-blue-50 text-blue-700 border border-blue-200 px-3 py-2 text-xs font-semibold inline-flex gap-2 items-center"><ShieldCheck size={16} /> Prototype only</span>
    </div>
    {error && <div role="alert" className="mt-7 bg-amber-50 border border-amber-200 p-4 rounded-xl text-amber-900">
      Demo data could not be loaded. Check that the migrated and seeded API is running on port 8000.
      <button onClick={() => setAttempt(value => value + 1)} className="ml-3 font-semibold underline">Try again</button>
    </div>}
    <div aria-busy={loading} className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {cards.map(({ label, value, Icon }) => <section key={label} className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex justify-between items-center text-slate-600"><h2 className="text-sm">{label}</h2><Icon size={21} className="text-blue-600" /></div>
        <div className="text-4xl font-bold mt-4">{loading || error ? '—' : value ?? '—'}</div>
        <div className="text-xs text-slate-500 mt-2">All synthetic exercises</div>
      </section>)}
    </div>
    <div className="mt-8 grid gap-6 xl:grid-cols-[1.5fr_1fr]">
      <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <h2 className="font-semibold text-xl">Incident directory</h2>
        <p className="text-slate-600 text-sm mt-1">Search exercises by name or region. Totals above cover all exercises.</p>
        <div className="mt-5 flex gap-3 flex-wrap">
          <label className="flex-1 min-w-0 text-sm font-medium">Search exercises
            <input value={query} onChange={event => setQuery(event.target.value)} maxLength={100} placeholder="Name or region" type="search" className="mt-1 w-full border border-slate-300 rounded-lg p-2" />
          </label>
          <label className="text-sm font-medium">Status
            <select value={status} onChange={event => setStatus(event.target.value)} className="mt-1 block border border-slate-300 rounded-lg p-2">
              <option value="all">All statuses</option><option value="active">Active</option><option value="closed">Closed</option>
            </select>
          </label>
        </div>
        <div role="status" className="mt-4 text-sm text-slate-600">
          {loading ? 'Loading incident data…' : error ? 'Incident data unavailable.' : `${filtered.length} exercise${filtered.length === 1 ? '' : 's'} found`}
        </div>
        {!loading && !error && (filtered.length === 0 ? <p className="mt-5 text-slate-600">No exercises match your filters.</p> : filtered.map(item => <article key={item.id} className="mt-5 p-4 rounded-xl border border-slate-200 flex gap-3">
          <div className="bg-blue-50 text-blue-600 rounded-lg p-3 h-fit"><CloudRain size={24} /></div>
          <div className="min-w-0">
            <h3 className="font-semibold">{item.name}</h3>
            <p className="text-slate-600 text-sm mt-1">{item.affected_region}</p>
            <p className="mt-3 text-xs font-semibold capitalize">{item.status} · {item.disaster_type} · <time dateTime={item.start_time}>{item.start_time.slice(0, 10)}</time></p>
            <p className="text-xs text-slate-500 mt-1">{item.id}</p>
          </div>
        </article>))}
      </section>
      <aside className="bg-[#101f39] rounded-2xl text-white p-6 h-fit">
        <h2 className="font-semibold text-xl">People make the final decision</h2>
        <p className="text-slate-300 text-sm mt-3 leading-6">Reunify is designed to help authorized teams investigate possible connections between missing-person reports and unidentified patient records.</p>
        <p className="text-slate-300 text-sm mt-3 leading-6">These counts are fictional scenario data. Suggested matches are seeded examples, not model results. AI analysis and case review arrive in later phases.</p>
        <div className="mt-6 border-t border-slate-700 pt-5 text-sm text-sky-300">AI suggestions never verify identity or contact families.</div>
      </aside>
    </div>
    <p className="text-slate-500 text-xs mt-8">Training and demonstration only · Never upload real patient information</p>
  </Shell>;
}
