export type Overview = {
  demo_only: boolean;
  incident_count: number;
  missing_reports: number;
  hospital_records: number;
  suggested_matches: number;
  candidates_needing_review: number;
  verified_resolutions: number;
};

export type Incident = {
  id: string;
  name: string;
  disaster_type: string;
  affected_region: string;
  status: string;
  start_time: string;
};

export type Role = 'family' | 'hospital' | 'reviewer' | 'admin';

export type User = {
  id: string;
  display_name: string;
  role: Role;
  organization_id: string | null;
};

export type DemoAccount = { id: string; display_name: string; role: Role };

export type ReportInput = {
  incident_id: string;
  name: string;
  nickname?: string | null;
  approximate_age?: number | null;
  height_cm?: number | null;
  hair_color?: string | null;
  eye_color?: string | null;
  distinguishing_features?: string | null;
  last_seen_location: string;
  last_seen_time: string;
  clothing_description?: string | null;
  reporter_contact: string;
  consent: true;
  image_id?: string | null;
};

export type ReportCreated = { id: string; status: string; created_at: string };

export type PatientInput = {
  incident_id: string;
  internal_id: string;
  approximate_age?: number | null;
  height_cm?: number | null;
  hair_color?: string | null;
  eye_color?: string | null;
  distinguishing_features?: string | null;
  observed_clothing?: string | null;
  intake_location?: string | null;
  admission_time?: string | null;
  consent: true;
  image_id?: string | null;
};

export type PatientRecord = {
  id: string;
  incident_id: string;
  organization_id: string | null;
  internal_id: string | null;
  approximate_age: number | null;
  height_cm: number | null;
  hair_color: string | null;
  eye_color: string | null;
  distinguishing_features: string | null;
  observed_clothing: string | null;
  intake_location: string | null;
  admission_time: string | null;
  image_id: string | null;
};

const api = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function detail(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (body && typeof body.detail === 'string') return body.detail;
  } catch {
    /* fall through to a generic message */
  }
  return 'The request could not be completed.';
}

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) throw new ApiError(response.status, await detail(response));
  return response.json() as Promise<T>;
}

const MUTATION_HEADERS = { 'content-type': 'application/json', 'x-reunify-csrf': '1' };

function post(path: string, body?: unknown): Promise<Response> {
  return fetch(`${api}${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: MUTATION_HEADERS,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

function get(path: string, signal?: AbortSignal): Promise<Response> {
  return fetch(`${api}${path}`, { credentials: 'include', signal });
}

export async function loadDashboard(signal: AbortSignal): Promise<[Overview, Incident[]]> {
  const responses = await Promise.all([get('/api/v1/demo/overview', signal), get('/api/v1/incidents', signal)]);
  if (responses.some(response => !response.ok)) throw new Error('API unavailable');
  return Promise.all(responses.map(response => response.json())) as Promise<[Overview, Incident[]]>;
}

export async function loadIncidents(signal?: AbortSignal): Promise<Incident[]> {
  return readJson<Incident[]>(await get('/api/v1/incidents', signal));
}

export async function getMe(): Promise<User | null> {
  const response = await get('/api/v1/auth/me');
  if (response.status === 401 || response.status === 503) return null;
  return readJson<User>(response);
}

export async function getDemoAccounts(): Promise<{ accounts: DemoAccount[]; enabled: boolean }> {
  const response = await get('/api/v1/auth/demo-accounts');
  if (response.status === 503) return { accounts: [], enabled: false };
  return { accounts: await readJson<DemoAccount[]>(response), enabled: true };
}

export async function login(userId: string): Promise<User> {
  return readJson<User>(await post('/api/v1/auth/login', { user_id: userId }));
}

export async function logout(): Promise<void> {
  await post('/api/v1/auth/logout');
}

export async function createReport(input: ReportInput): Promise<ReportCreated> {
  return readJson<ReportCreated>(await post('/api/v1/reports', input));
}

export async function listReports(): Promise<ReportCreated[]> {
  return readJson<ReportCreated[]>(await get('/api/v1/reports'));
}

export async function trackReport(id: string): Promise<ReportCreated> {
  return readJson<ReportCreated>(await get(`/api/v1/reports/${id}/tracking`));
}

export async function createPatient(input: PatientInput): Promise<PatientRecord> {
  return readJson<PatientRecord>(await post('/api/v1/patients', input));
}

export async function listPatients(): Promise<PatientRecord[]> {
  return readJson<PatientRecord[]>(await get('/api/v1/patients'));
}

export async function uploadImage(file: File): Promise<string> {
  const form = new FormData();
  form.append('file', file);
  const response = await fetch(`${api}/api/v1/images`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'x-reunify-csrf': '1' },
    body: form,
  });
  const body = await readJson<{ image_id: string }>(response);
  return body.image_id;
}
