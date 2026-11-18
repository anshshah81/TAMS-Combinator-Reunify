'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { CheckCircle2 } from 'lucide-react';
import { Shell } from '@/components/Shell';
import { RoleGate } from '@/components/RoleGate';
import { Alert, Button, Card, Field, Input, Select, Textarea } from '@/components/ui';
import { ApiError, createReport, loadIncidents, uploadImage, type Incident, type ReportCreated, type ReportInput } from '@/lib/api';

const EMPTY = {
  incident_id: '', name: '', nickname: '', approximate_age: '', height_cm: '',
  hair_color: '', eye_color: '', distinguishing_features: '', last_seen_location: '',
  last_seen_time: '', clothing_description: '', reporter_contact: '', consent: false,
};

function trimmed(value: string): string | undefined {
  const text = value.trim();
  return text ? text : undefined;
}

function toNumber(value: string): number | undefined {
  const text = value.trim();
  return text ? Number(text) : undefined;
}

function ReportForm() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [form, setForm] = useState({ ...EMPTY });
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<ReportCreated | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadIncidents().then(setIncidents).catch(() => setError('Could not load incidents. Is the API running?'));
  }, []);

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm(previous => ({ ...previous, [key]: value }));
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (submitting) return;
    setError(null);
    if (!form.consent) { setError('Please confirm you are authorized to submit this report.'); return; }
    setSubmitting(true);
    try {
      let imageId: string | undefined;
      if (file) imageId = await uploadImage(file);
      const payload: ReportInput = {
        incident_id: form.incident_id,
        name: form.name.trim(),
        nickname: trimmed(form.nickname),
        approximate_age: toNumber(form.approximate_age),
        height_cm: toNumber(form.height_cm),
        hair_color: trimmed(form.hair_color),
        eye_color: trimmed(form.eye_color),
        distinguishing_features: trimmed(form.distinguishing_features),
        last_seen_location: form.last_seen_location.trim(),
        last_seen_time: new Date(form.last_seen_time).toISOString(),
        clothing_description: trimmed(form.clothing_description),
        reporter_contact: form.reporter_contact.trim(),
        consent: true,
        image_id: imageId,
      };
      const result = await createReport(payload);
      setCreated(result);
      setForm({ ...EMPTY });
      setFile(null);
      if (fileRef.current) fileRef.current.value = '';
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Submission failed. Please check your details and try again.');
    } finally {
      setSubmitting(false);
    }
  }

  if (created) {
    return (
      <Card className="max-w-2xl">
        <div className="flex items-center gap-2 text-emerald-700 font-semibold"><CheckCircle2 size={20} /> Report received</div>
        <p className="mt-3 text-slate-700 text-sm leading-6">
          Keep this tracking ID to check your report status. It is the only reference you need. Reunify will never
          share patient records or match details through this family view.
        </p>
        <div className="mt-4 rounded-lg bg-slate-50 border border-slate-200 p-4">
          <div className="text-xs uppercase tracking-widest text-slate-500 font-semibold">Tracking ID</div>
          <div className="text-lg font-bold mt-1 break-all">{created.id}</div>
          <div className="text-sm text-slate-600 mt-1 capitalize">Status: {created.status}</div>
        </div>
        <div className="mt-5 flex gap-3">
          <Button onClick={() => setCreated(null)}>Submit another report</Button>
          <Link href="/tracking"><Button type="button" variant="secondary">Go to tracking</Button></Link>
        </div>
      </Card>
    );
  }

  return (
    <form onSubmit={submit} className="max-w-2xl">
      {error && <div className="mb-5"><Alert tone="error">{error}</Alert></div>}
      <Card className="grid gap-5">
        <Field label="Incident" required htmlFor="incident">
          <Select id="incident" required value={form.incident_id} onChange={event => update('incident_id', event.target.value)}>
            <option value="" disabled>Select an incident</option>
            {incidents.map(incident => <option key={incident.id} value={incident.id}>{incident.name}</option>)}
          </Select>
        </Field>
        <div className="grid sm:grid-cols-2 gap-5">
          <Field label="Full name" required htmlFor="name">
            <Input id="name" required maxLength={200} value={form.name} onChange={event => update('name', event.target.value)} />
          </Field>
          <Field label="Nickname" htmlFor="nickname">
            <Input id="nickname" maxLength={120} value={form.nickname} onChange={event => update('nickname', event.target.value)} />
          </Field>
          <Field label="Approximate age" htmlFor="age">
            <Input id="age" type="number" min={0} max={120} value={form.approximate_age} onChange={event => update('approximate_age', event.target.value)} />
          </Field>
          <Field label="Height (cm)" htmlFor="height">
            <Input id="height" type="number" min={30} max={250} value={form.height_cm} onChange={event => update('height_cm', event.target.value)} />
          </Field>
          <Field label="Hair color" htmlFor="hair">
            <Input id="hair" maxLength={50} value={form.hair_color} onChange={event => update('hair_color', event.target.value)} />
          </Field>
          <Field label="Eye color" htmlFor="eye">
            <Input id="eye" maxLength={50} value={form.eye_color} onChange={event => update('eye_color', event.target.value)} />
          </Field>
        </div>
        <Field label="Distinguishing characteristics" htmlFor="features" hint="Scars, tattoos, glasses, mobility aids, and similar details.">
          <Textarea id="features" maxLength={2000} value={form.distinguishing_features} onChange={event => update('distinguishing_features', event.target.value)} />
        </Field>
        <div className="grid sm:grid-cols-2 gap-5">
          <Field label="Last-known location" required htmlFor="place">
            <Input id="place" required maxLength={200} value={form.last_seen_location} onChange={event => update('last_seen_location', event.target.value)} />
          </Field>
          <Field label="Last seen" required htmlFor="seen">
            <Input id="seen" type="datetime-local" required value={form.last_seen_time} onChange={event => update('last_seen_time', event.target.value)} />
          </Field>
        </div>
        <Field label="Last-seen clothing" htmlFor="clothing">
          <Textarea id="clothing" maxLength={2000} value={form.clothing_description} onChange={event => update('clothing_description', event.target.value)} />
        </Field>
        <Field label="Reference photo" htmlFor="photo" hint="Optional. Use only a photo you are authorized to share (JPEG or PNG, up to 5 MB).">
          <input ref={fileRef} id="photo" type="file" accept="image/png,image/jpeg"
            onChange={event => setFile(event.target.files?.[0] ?? null)} className="text-sm" />
        </Field>
        <Field label="Your contact information" required htmlFor="contact" hint="How reviewers can reach you if needed.">
          <Input id="contact" required maxLength={200} value={form.reporter_contact} onChange={event => update('reporter_contact', event.target.value)} />
        </Field>
        <label className="flex items-start gap-3 text-sm text-slate-700">
          <input type="checkbox" className="mt-1" checked={form.consent} onChange={event => update('consent', event.target.checked)} />
          <span>I confirm I am authorized to submit this information and any attached photo for reunification purposes.</span>
        </label>
        <div>
          <Button type="submit" disabled={submitting}>{submitting ? 'Submitting…' : 'Submit report'}</Button>
        </div>
      </Card>
    </form>
  );
}

export default function Page() {
  return (
    <RoleGate role="family">
      <Shell>
        <div className="text-xs font-semibold uppercase tracking-widest text-blue-600">Family · Synthetic demo</div>
        <h1 className="text-3xl md:text-4xl mt-2 font-bold tracking-tight">Report a missing person</h1>
        <p className="text-slate-600 mt-2 max-w-2xl">Provide what you know. Required fields are marked. You will receive a tracking ID after submitting.</p>
        <div className="mt-7"><ReportForm /></div>
      </Shell>
    </RoleGate>
  );
}
