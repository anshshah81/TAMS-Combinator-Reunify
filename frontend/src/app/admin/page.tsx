'use client';

import { useEffect, useState } from 'react';
import { Shell } from '@/components/Shell';
import { RoleGate } from '@/components/RoleGate';
import { Alert, Badge, Button, Card, Select } from '@/components/ui';
import {
  ApiError, listAuditLogs, listUsers, loadIncidents, setIncidentStatus,
  type AdminUser, type AuditEntry, type Incident,
} from '@/lib/api';

const INCIDENT_STATUSES = ['active', 'monitoring', 'closed'];

function Admin() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [audit, setAudit] = useState<AuditEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  async function load() {
    try {
      const [incidentList, userList, auditList] = await Promise.all([loadIncidents(), listUsers(), listAuditLogs()]);
      setIncidents(incidentList);
      setUsers(userList);
      setAudit(auditList);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not load administration data.');
    }
  }

  useEffect(() => { void load(); }, []);

  async function changeStatus(incidentId: string, status: string) {
    setBusy(incidentId);
    setError(null);
    try {
      await setIncidentStatus(incidentId, status);
      await load();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Could not update the incident.');
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="max-w-5xl">
      <Alert tone="info">
        Administration covers synthetic incidents, demo accounts, and the immutable audit trail. The audit log
        records only who did what to which record — never medical or biometric detail.
      </Alert>
      {error && <div className="mt-5"><Alert tone="error">{error}</Alert></div>}

      <h2 className="mt-7 text-xl font-bold tracking-tight">Incidents</h2>
      <div className="mt-3 grid gap-3">
        {incidents.map(incident => (
          <Card key={incident.id} className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="font-semibold text-slate-800">{incident.name}</div>
              <div className="text-xs text-slate-500">{incident.id} · <span className="capitalize">{incident.status}</span></div>
            </div>
            <div className="flex items-center gap-2">
              <Select aria-label={`Status for ${incident.name}`} value={incident.status}
                disabled={busy === incident.id}
                onChange={event => changeStatus(incident.id, event.target.value)}>
                {INCIDENT_STATUSES.map(status => <option key={status} value={status}>{status}</option>)}
                {!INCIDENT_STATUSES.includes(incident.status) && <option value={incident.status}>{incident.status}</option>}
              </Select>
            </div>
          </Card>
        ))}
      </div>

      <h2 className="mt-8 text-xl font-bold tracking-tight">Demo accounts</h2>
      <Card className="mt-3 overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500">
            <th className="py-2 pr-4">User</th><th className="py-2 pr-4">Role</th><th className="py-2 pr-4">Organization</th><th className="py-2">Active</th>
          </tr></thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} className="border-t border-slate-100">
                <td className="py-2 pr-4 font-medium text-slate-800">{user.display_name}<div className="font-mono text-xs text-slate-400">{user.id}</div></td>
                <td className="py-2 pr-4"><Badge>{user.role}</Badge></td>
                <td className="py-2 pr-4 text-slate-600">{user.organization_id ?? '—'}</td>
                <td className="py-2">{user.active ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <div className="mt-8 flex items-center justify-between">
        <h2 className="text-xl font-bold tracking-tight">Audit trail</h2>
        <Button variant="secondary" onClick={() => void load()}>Refresh</Button>
      </div>
      <Card className="mt-3 overflow-x-auto">
        {audit.length === 0 ? <p className="text-sm text-slate-400">No audit entries yet.</p> : (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs uppercase tracking-wide text-slate-500">
              <th className="py-2 pr-4">When</th><th className="py-2 pr-4">Actor</th><th className="py-2 pr-4">Action</th><th className="py-2">Record</th>
            </tr></thead>
            <tbody>
              {audit.map(entry => (
                <tr key={entry.id} className="border-t border-slate-100">
                  <td className="py-2 pr-4 text-slate-600">{new Date(entry.occurred_at).toLocaleString()}</td>
                  <td className="py-2 pr-4 font-mono text-xs">{entry.actor_id}</td>
                  <td className="py-2 pr-4 font-medium text-slate-800">{entry.action}</td>
                  <td className="py-2 font-mono text-xs text-slate-500">{entry.record_id ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}

export default function Page() {
  return (
    <RoleGate role="admin">
      <Shell>
        <div className="text-xs font-semibold uppercase tracking-widest text-blue-600">Administrator · Synthetic demo</div>
        <h1 className="text-3xl md:text-4xl mt-2 font-bold tracking-tight">Administration</h1>
        <p className="text-slate-600 mt-2 max-w-2xl">Manage synthetic incidents and accounts and review the immutable audit trail.</p>
        <div className="mt-7"><Admin /></div>
      </Shell>
    </RoleGate>
  );
}
