'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';
import { Shell } from '@/components/Shell';
import { RoleGate } from '@/components/RoleGate';
import { Alert, Badge, Button, Card, Field, Select } from '@/components/ui';
import {
  ApiError, generateCandidates, listCandidates, loadIncidents,
  type Incident, type MatchCandidate,
} from '@/lib/api';

const STATUS_TONE: Record<string, string> = {
  needs_review: 'bg-amber-100 text-amber-800 border-amber-200',
  investigating: 'bg-blue-100 text-blue-800 border-blue-200',
  info_requested: 'bg-violet-100 text-violet-800 border-violet-200',
  rejected: 'bg-slate-200 text-slate-700 border-slate-300',
  verified: 'bg-emerald-100 text-emerald-800 border-emerald-200',
};

function StatusPill({ status }: { status: string }) {
  const tone = STATUS_TONE[status] ?? 'bg-slate-100 text-slate-700 border-slate-200';
  return <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold capitalize ${tone}`}>{status.replace('_', ' ')}</span>;
}

function MatchReview() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [incidentId, setIncidentId] = useState('');
  const [candidates, setCandidates] = useState<MatchCandidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadIncidents().then(list => {
      setIncidents(list);
      if (list.length && !incidentId) setIncidentId(list[0].id);
    }).catch(() => setError('Could not load incidents. Is the API running?'));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!incidentId) return;
    setLoading(true);
    setError(null);
    listCandidates(incidentId)
      .then(setCandidates)
      .catch(caught => setError(caught instanceof ApiError ? caught.message : 'Could not load candidates.'))
      .finally(() => setLoading(false));
  }, [incidentId]);

  async function generate() {
    if (!incidentId || generating) return;
    setGenerating(true);
    setError(null);
    try {
      setCandidates(await generateCandidates(incidentId));
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not generate candidates.');
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="max-w-5xl">
      <Alert tone="info">
        These are <strong>AI-suggested</strong> candidates ranked by transparent evidence, not confirmed matches.
        The ranking score is an evidence tally, not a probability. A reviewer must investigate and independently
        verify every identity; the system never confirms a match or contacts families on its own.
      </Alert>

      <Card className="mt-5 grid gap-4 sm:grid-cols-[1fr_auto] sm:items-end">
        <Field label="Incident" htmlFor="incident">
          <Select id="incident" value={incidentId} onChange={event => setIncidentId(event.target.value)}>
            {incidents.map(incident => <option key={incident.id} value={incident.id}>{incident.name}</option>)}
          </Select>
        </Field>
        <Button onClick={generate} disabled={generating || !incidentId} className="inline-flex items-center gap-2">
          <Sparkles size={16} />{generating ? 'Generating…' : 'Generate candidates'}
        </Button>
      </Card>

      {error && <div className="mt-5"><Alert tone="error">{error}</Alert></div>}

      <div className="mt-6 grid gap-3">
        {loading ? (
          <p role="status" className="text-slate-600">Loading candidates…</p>
        ) : candidates.length === 0 ? (
          <Card><p className="text-slate-600 text-sm">No candidates yet for this incident. Generate candidates to review AI suggestions, or there may be no supported matches.</p></Card>
        ) : (
          candidates.map(candidate => (
            <Card key={candidate.id} className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusPill status={candidate.status} />
                  <Badge>score {candidate.ranking_score ?? '—'}</Badge>
                </div>
                <div className="mt-2 text-sm text-slate-700">
                  <span className="font-mono text-xs">{candidate.missing_person_id}</span>
                  <span className="mx-2 text-slate-400">↔</span>
                  <span className="font-mono text-xs">{candidate.patient_id}</span>
                </div>
                {candidate.evidence && (
                  <div className="mt-2 flex flex-wrap gap-3 text-xs text-slate-500">
                    <span className="text-emerald-700">{candidate.evidence.supporting.length} supporting</span>
                    <span className="text-red-700">{candidate.evidence.conflicting.length} conflicting</span>
                    <span>{candidate.evidence.missing.length} missing</span>
                  </div>
                )}
              </div>
              <Link href={`/matches/${candidate.id}`}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-800 hover:bg-slate-50">
                Investigate <ArrowRight size={15} />
              </Link>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGate role={['reviewer', 'admin']}>
      <Shell>
        <div className="text-xs font-semibold uppercase tracking-widest text-blue-600">Reviewer · Synthetic demo</div>
        <h1 className="text-3xl md:text-4xl mt-2 font-bold tracking-tight">Match review</h1>
        <p className="text-slate-600 mt-2 max-w-2xl">Review AI-suggested candidates and open any candidate for side-by-side investigation.</p>
        <div className="mt-7"><MatchReview /></div>
      </Shell>
    </RoleGate>
  );
}
