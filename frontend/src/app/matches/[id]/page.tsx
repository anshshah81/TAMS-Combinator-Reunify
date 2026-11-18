'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Check, HelpCircle, Scan, ShieldCheck, X } from 'lucide-react';
import { Shell } from '@/components/Shell';
import { RoleGate } from '@/components/RoleGate';
import { DetectionOverlay, type OverlayBox } from '@/components/DetectionOverlay';
import { Alert, Badge, Button, Card, Field, Textarea } from '@/components/ui';
import {
  ApiError, compareFaces, detectClothing, getInvestigation, imageUrl, listDecisions, recordDecision,
  type ClothingDetection, type DecisionAction, type FaceComparison, type Investigation, type ReviewDecision,
} from '@/lib/api';

const TERMINAL = new Set(['rejected', 'verified']);

function Attr({ label, report, patient }: { label: string; report: unknown; patient: unknown }) {
  const show = (value: unknown) => (value === null || value === undefined || value === '' ? <span className="text-slate-400">not recorded</span> : String(value));
  return (
    <div className="grid grid-cols-3 gap-2 border-b border-slate-100 py-2 text-sm">
      <div className="text-slate-500">{label}</div>
      <div className="text-slate-800">{show(report)}</div>
      <div className="text-slate-800">{show(patient)}</div>
    </div>
  );
}

function EvidenceList({ title, items, tone }: { title: string; items: string[]; tone: 'good' | 'bad' | 'muted' }) {
  const color = { good: 'text-emerald-700', bad: 'text-red-700', muted: 'text-slate-500' }[tone];
  return (
    <div>
      <div className={`text-xs font-semibold uppercase tracking-wide ${color}`}>{title} ({items.length})</div>
      {items.length === 0 ? <p className="mt-1 text-xs text-slate-400">None</p> : (
        <ul className="mt-1 space-y-1 text-sm text-slate-700">{items.map((item, index) => <li key={index}>• {item}</li>)}</ul>
      )}
    </div>
  );
}

function Investigate({ candidateId }: { candidateId: string }) {
  const [data, setData] = useState<Investigation | null>(null);
  const [decisions, setDecisions] = useState<ReviewDecision[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [notes, setNotes] = useState('');
  const [attestation, setAttestation] = useState('');
  const [busy, setBusy] = useState(false);
  const [face, setFace] = useState<FaceComparison | null>(null);
  const [clothing, setClothing] = useState<ClothingDetection | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [investigation, history] = await Promise.all([getInvestigation(candidateId), listDecisions(candidateId)]);
      setData(investigation);
      setDecisions(history);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not load this candidate.');
    }
  }, [candidateId]);

  useEffect(() => { void refresh(); }, [refresh]);

  async function decide(decision: DecisionAction) {
    if (busy || !data) return;
    if (decision === 'verify' && (attestation.trim().length < 10 || notes.trim().length === 0)) {
      setError('Recording a verification requires notes and a written attestation (at least 10 characters).');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await recordDecision(candidateId, {
        decision,
        notes: notes.trim() || undefined,
        attestation: decision === 'verify' ? attestation.trim() : undefined,
      });
      setNotes('');
      setAttestation('');
      await refresh();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not record this decision.');
    } finally {
      setBusy(false);
    }
  }

  async function runFace() {
    if (!data?.report.image_id || !data?.patient.image_id) return;
    setError(null);
    try {
      setFace(await compareFaces(data.report.image_id, data.patient.image_id));
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Face comparison failed.');
    }
  }

  async function runClothing() {
    if (!data?.patient.image_id) return;
    const descriptions = (data.report.clothing_description ?? '').split(/[,;]/).map(s => s.trim()).filter(Boolean);
    if (descriptions.length === 0) { setError('The report has no clothing description to search for.'); return; }
    setError(null);
    try {
      setClothing(await detectClothing(data.patient.image_id, descriptions));
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Clothing detection failed.');
    }
  }

  if (error && !data) return <Alert tone="error">{error}</Alert>;
  if (!data) return <p role="status" className="text-slate-600">Loading investigation…</p>;

  const isFinal = TERMINAL.has(data.status);
  const clothingBoxes: OverlayBox[] = clothing
    ? clothing.queries.flatMap(query => query.detections.map(detection => ({ box: detection.box, score: detection.score, label: query.query })))
    : [];

  return (
    <div className="max-w-5xl">
      <Link href="/matches" className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-600 hover:text-slate-900">
        <ArrowLeft size={15} /> Back to match review
      </Link>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <h2 className="text-2xl font-bold tracking-tight">Candidate investigation</h2>
        <Badge>{data.status.replace('_', ' ')}</Badge>
        <Badge>score {data.ranking_score ?? '—'}</Badge>
      </div>

      <Alert tone="info">
        This is an AI suggestion. Confirm identity only with independent human evidence. Facial distance and
        clothing detections are uncertain evidence; a non-detection does not mean a garment is absent.
      </Alert>

      {error && <div className="mt-4"><Alert tone="error">{error}</Alert></div>}

      <Card className="mt-5">
        <div className="grid grid-cols-3 gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          <div>Attribute</div>
          <div>Missing-person report</div>
          <div>Unidentified patient</div>
        </div>
        <div className="mt-2">
          <Attr label="Reference ID" report={data.report.id} patient={data.patient.id} />
          <Attr label="Name / internal ID" report={data.report.name} patient={data.patient.internal_id} />
          <Attr label="Approx. age" report={data.report.approximate_age} patient={data.patient.approximate_age} />
          <Attr label="Height (cm)" report={data.report.height_cm} patient={data.patient.height_cm} />
          <Attr label="Hair color" report={data.report.hair_color} patient={data.patient.hair_color} />
          <Attr label="Eye color" report={data.report.eye_color} patient={data.patient.eye_color} />
          <Attr label="Distinguishing features" report={data.report.distinguishing_features} patient={data.patient.distinguishing_features} />
          <Attr label="Clothing" report={data.report.clothing_description} patient={data.patient.observed_clothing} />
          <Attr label="Location" report={data.report.last_seen_location} patient={data.patient.intake_location} />
          <Attr label="Timestamp" report={data.report.last_seen_time} patient={data.patient.admission_time} />
        </div>
      </Card>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <Card>
          <div className="text-sm font-semibold text-slate-700">Report photo</div>
          {data.report.image_id
            ? <div className="mt-2"><DetectionOverlay src={imageUrl(data.report.image_id)} alt="Report reference (synthetic)" boxes={[]} /></div>
            : <p className="mt-2 text-sm text-slate-400">No photo on file.</p>}
        </Card>
        <Card>
          <div className="text-sm font-semibold text-slate-700">Patient photo</div>
          {data.patient.image_id
            ? <div className="mt-2"><DetectionOverlay src={imageUrl(data.patient.image_id)} alt="Patient (synthetic)" boxes={clothingBoxes} /></div>
            : <p className="mt-2 text-sm text-slate-400">No photo on file.</p>}
        </Card>
      </div>

      <Card className="mt-5">
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="secondary" onClick={runFace} disabled={!data.report.image_id || !data.patient.image_id}
            className="inline-flex items-center gap-2"><Scan size={15} /> Run face comparison</Button>
          <Button variant="secondary" onClick={runClothing} disabled={!data.patient.image_id}
            className="inline-flex items-center gap-2"><Scan size={15} /> Detect reported clothing</Button>
        </div>
        {face && (
          <div className="mt-3 text-sm text-slate-700">
            Face: <strong>{face.status}</strong>{face.distance !== null && <> · distance {face.distance.toFixed(3)}</>}
            {face.mock && <Badge>mock</Badge>} {face.warning && <span className="text-amber-700"> — {face.warning}</span>}
          </div>
        )}
        {clothing && (
          <div className="mt-2 text-sm text-slate-700">
            Clothing: <strong>{clothing.status.replace('_', ' ')}</strong> {clothing.mock && <Badge>mock</Badge>}
            {clothing.warning && <span className="block text-xs text-amber-700 mt-1">{clothing.warning}</span>}
          </div>
        )}
      </Card>

      {data.evidence && (
        <Card className="mt-5 grid gap-4 sm:grid-cols-3">
          <EvidenceList title="Supporting" items={data.evidence.supporting} tone="good" />
          <EvidenceList title="Conflicting" items={data.evidence.conflicting} tone="bad" />
          <EvidenceList title="Missing / not run" items={data.evidence.missing} tone="muted" />
        </Card>
      )}

      <Card className="mt-5">
        <div className="text-sm font-semibold text-slate-700">Reviewer decision</div>
        {isFinal ? (
          <Alert tone="info"><span className="mt-2 block">This candidate has a final decision ({data.status}) and cannot be changed.</span></Alert>
        ) : (
          <>
            <div className="mt-3 grid gap-3">
              <Field label="Reviewer notes" hint="Required to record a verification; recommended for every decision.">
                <Textarea value={notes} onChange={event => setNotes(event.target.value)} maxLength={4000} />
              </Field>
              <Field label="Identity-verification attestation"
                hint="Required only to record a verification. Describe the independent human evidence used (e.g. ID documents, next-of-kin confirmation).">
                <Textarea value={attestation} onChange={event => setAttestation(event.target.value)} maxLength={4000} />
              </Field>
            </div>
            <div className="mt-4 flex flex-wrap gap-3">
              <Button variant="secondary" onClick={() => decide('investigate')} disabled={busy} className="inline-flex items-center gap-2"><Scan size={15} /> Investigate further</Button>
              <Button variant="secondary" onClick={() => decide('request_info')} disabled={busy} className="inline-flex items-center gap-2"><HelpCircle size={15} /> Request more info</Button>
              <Button variant="danger" onClick={() => decide('reject')} disabled={busy} className="inline-flex items-center gap-2"><X size={15} /> Reject candidate</Button>
              <Button onClick={() => decide('verify')} disabled={busy} className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700"><ShieldCheck size={15} /> Record verification</Button>
            </div>
          </>
        )}
      </Card>

      <Card className="mt-5">
        <div className="text-sm font-semibold text-slate-700">Decision history</div>
        {decisions.length === 0 ? <p className="mt-2 text-sm text-slate-400">No decisions recorded yet.</p> : (
          <ul className="mt-2 space-y-2 text-sm">
            {decisions.map(decision => (
              <li key={decision.id} className="border-b border-slate-100 pb-2">
                <div className="flex items-center gap-2">
                  {decision.decision === 'verify' && <Check size={14} className="text-emerald-600" />}
                  <span className="font-semibold capitalize">{decision.decision.replace('_', ' ')}</span>
                  <span className="text-slate-400">by {decision.reviewer_id}</span>
                  <span className="text-slate-400">· {new Date(decision.created_at).toLocaleString()}</span>
                </div>
                {decision.notes && <div className="mt-0.5 text-slate-600">{decision.notes}</div>}
                {decision.attestation && <div className="mt-0.5 text-emerald-800">Attestation: {decision.attestation}</div>}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

export default function Page() {
  const params = useParams<{ id: string }>();
  const candidateId = Array.isArray(params.id) ? params.id[0] : params.id;
  return (
    <RoleGate role={['reviewer', 'admin']}>
      <Shell>
        <Investigate candidateId={candidateId} />
      </Shell>
    </RoleGate>
  );
}
