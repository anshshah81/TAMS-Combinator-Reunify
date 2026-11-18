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
const api = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function loadDashboard(signal: AbortSignal): Promise<[Overview, Incident[]]> {
  const responses = await Promise.all([
    fetch(`${api}/api/v1/demo/overview`, { signal }),
    fetch(`${api}/api/v1/incidents`, { signal }),
  ]);
  if (responses.some(response => !response.ok)) throw new Error('API unavailable');
  return Promise.all(responses.map(response => response.json())) as Promise<[Overview, Incident[]]>;
}
