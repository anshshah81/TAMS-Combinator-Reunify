'use client';

import { useEffect, useRef, useState } from 'react';
import { CheckCircle2 } from 'lucide-react';
import { Shell } from '@/components/Shell';
import { RoleGate } from '@/components/RoleGate';
import { useSession } from '@/components/SessionProvider';
import { Alert, Button, Card, Field, Input, Select, Textarea } from '@/components/ui';
import { ApiError, createPatient, loadIncidents, uploadImage, type Incident, type PatientInput, type PatientRecord } from '@/lib/api';

const EMPTY = {
  incident_id: '', internal_id: '', approximate_age: '', height_cm: '', hair_color: '',
  eye_color: '', distinguishing_features: '', observed_clothing: '', intake_location: '',
  admission_time: '', consent: false,
};

function trimmed(value: string): string | undefined {
  const text = value.trim();
  return text ? text : undefined;
}

function toNumber(value: string): number | undefined {
  const text = value.trim();
  return text ? Number(text) : undefined;
}

function HospitalForm() {
  const { user } = useSession();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [form, setForm] = useState({ ...EMPTY });
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<PatientRecord | null>(null);
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
    if (!form.consent) { setError('Please confirm this record is authorized synthetic demo data.'); return; }
    setSubmitting(true);
    try {
      let imageId: string | undefined;
      if (file) imageId = await uploadImage(file);
      const payload: PatientInput = {
        incident_id: form.incident_id,
        internal_id: form.internal_id.trim(),
        approximate_age: toNumber(form.approximate_age),
        height_cm: toNumber(form.height_cm),
        hair_color: trimmed(form.hair_color),
        eye_color: trimmed(form.eye_color),
        distinguishing_features: trimmed(form.distinguishing_features),
        observed_clothing: trimmed(form.observed_clothing),
        intake_location: trimmed(form.intake_location),
        admission_time: form.admission_time ? new Date(form.admission_time).toISOString() : undefined,
        consent: true,
        image_id: imageId,
      };
      const result = await createPatient(payload);
      setCreated(result);
      setForm({ ...EMPTY });
      setFile(null);
      if (fileRef.current) fileRef.current.value = '';
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not save this record. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }

  if (created) {
    return (
      <Card className="max-w-2xl">
        <div className="flex items-center gap-2 text-emerald-700 font-semibold"><CheckCircle2 size={20} /> Patient record saved</div>
        <p className="mt-3 text-slate-700 text-sm leading-6">Record created within your organization. Reviewers can use it during investigation.</p>
        <div className="mt-4 rounded-lg bg-slate-50 border border-slate-200 p-4 text-sm">
          <div><span className="text-slate-500">Record ID:</span> <span className="font-semibold break-all">{created.id}</span></div>
          <div className="mt-1"><span className="text-slate-500">Internal ID:</span> <span className="font-semibold">{created.internal_id}</span></div>
          <div className="mt-1"><span className="text-slate-500">Organization:</span> <span className="font-semibold">{created.organization_id}</span></div>
        </div>
        <div className="mt-5"><Button onClick={() => setCreated(null)}>Add another record</Button></div>
      </Card>
    );
  }

  return (
    <form onSubmit={submit} className="max-w-2xl">
      {error && <div className="mb-5"><Alert tone="error">{error}</Alert></div>}
      <Card className="grid gap-5">
        <Alert tone="info">
          Submitting as <strong>{user?.display_name}</strong>. The hospital organization
          (<strong>{user?.organization_id ?? 'none'}</strong>) is taken from your session, not this form.
        </Alert>
        <Field label="Incident" required htmlFor="incident">
          <Select id="incident" required value={form.incident_id} onChange={event => update('incident_id', event.target.value)}>
            <option value="" disabled>Select an incident</option>
            {incidents.map(incident => <option key={incident.id} value={incident.id}>{incident.name}</option>)}
          </Select>
        </Field>
        <Field label="Internal patient record identifier" required htmlFor="internal" hint="Unique within your organization (e.g. ward and bed).">
          <Input id="internal" required maxLength={100} value={form.internal_id} onChange={event => update('internal_id', event.target.value)} />
        </Field>
        <p className="text-xs text-slate-500">Leave any field blank when the information is unknown. Blank means &ldquo;not recorded&rdquo;, not &ldquo;absent&rdquo;.</p>
        <div className="grid sm:grid-cols-2 gap-5">
          <Field label="Estimated age" htmlFor="age">
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
        <Field label="Distinguishing characteristics" htmlFor="features">
          <Textarea id="features" maxLength={2000} value={form.distinguishing_features} onChange={event => update('distinguishing_features', event.target.value)} />
        </Field>
        <Field label="Observed clothing" htmlFor="clothing">
          <Textarea id="clothing" maxLength={2000} value={form.observed_clothing} onChange={event => update('observed_clothing', event.target.value)} />
        </Field>
        <div className="grid sm:grid-cols-2 gap-5">
          <Field label="Intake location" htmlFor="place">
            <Input id="place" maxLength={200} value={form.intake_location} onChange={event => update('intake_location', event.target.value)} />
          </Field>
          <Field label="Admission date/time" htmlFor="admit">
            <Input id="admit" type="datetime-local" value={form.admission_time} onChange={event => update('admission_time', event.target.value)} />
          </Field>
        </div>
        <Field label="Patient photograph" htmlFor="photo" hint="Optional. Authorized synthetic/consented images only (JPEG or PNG, up to 5 MB).">
          <input ref={fileRef} id="photo" type="file" accept="image/png,image/jpeg"
            onChange={event => setFile(event.target.files?.[0] ?? null)} className="text-sm" />
        </Field>
        <label className="flex items-start gap-3 text-sm text-slate-700">
          <input type="checkbox" className="mt-1" checked={form.consent} onChange={event => update('consent', event.target.checked)} />
          <span>I confirm this is authorized synthetic demonstration data and any photo is cleared for this use.</span>
        </label>
        <div>
          <Button type="submit" disabled={submitting}>{submitting ? 'Saving…' : 'Save patient record'}</Button>
        </div>
      </Card>
    </form>
  );
}

export default function Page() {
  return (
    <RoleGate role="hospital">
      <Shell>
        <div className="text-xs font-semibold uppercase tracking-widest text-blue-600">Hospital · Synthetic demo</div>
        <h1 className="text-3xl md:text-4xl mt-2 font-bold tracking-tight">Unidentified patient intake</h1>
        <p className="text-slate-600 mt-2 max-w-2xl">Record an unidentified patient for your organization. Unknown details may be left blank.</p>
        <div className="mt-7"><HospitalForm /></div>
      </Shell>
    </RoleGate>
  );
}
