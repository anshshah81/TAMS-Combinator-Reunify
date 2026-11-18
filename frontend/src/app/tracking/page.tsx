'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Shell } from '@/components/Shell';
import { RoleGate } from '@/components/RoleGate';
import { Alert, Badge, Card } from '@/components/ui';
import { listReports, type ReportCreated } from '@/lib/api';

const STATUS_LABEL: Record<string, string> = {
  received: 'Received — awaiting review',
  under_review: 'Under review',
  needs_more_info: 'More information requested',
  resolved: 'Resolved',
};

function TrackingList() {
  const [reports, setReports] = useState<ReportCreated[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listReports().then(setReports).catch(() => setError('Could not load your reports. Please try again later.'));
  }, []);

  if (error) return <Alert tone="error">{error}</Alert>;
  if (reports === null) return <p role="status" className="text-slate-600">Loading your reports…</p>;

  return (
    <div className="max-w-2xl">
      <Alert tone="info">
        This view shows only the status of reports you submitted. For privacy and safety, it never reveals patient
        records, candidate matches, or any identifying details beyond your own report.
      </Alert>
      {reports.length === 0 ? (
        <Card className="mt-5">
          <p className="text-slate-600 text-sm">You have not submitted any reports yet.</p>
          <Link href="/report" className="mt-3 inline-block text-blue-600 font-semibold text-sm">Report a missing person →</Link>
        </Card>
      ) : (
        <ul className="mt-5 grid gap-4">
          {reports.map(report => (
            <li key={report.id}>
              <Card>
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div className="min-w-0">
                    <div className="text-xs uppercase tracking-widest text-slate-500 font-semibold">Tracking ID</div>
                    <div className="font-bold break-all">{report.id}</div>
                    <div className="text-xs text-slate-500 mt-1">
                      Submitted <time dateTime={report.created_at}>{report.created_at.slice(0, 10)}</time>
                    </div>
                  </div>
                  <Badge>{STATUS_LABEL[report.status] ?? report.status}</Badge>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Page() {
  return (
    <RoleGate role="family">
      <Shell>
        <div className="text-xs font-semibold uppercase tracking-widest text-blue-600">Family · Synthetic demo</div>
        <h1 className="text-3xl md:text-4xl mt-2 font-bold tracking-tight">Report tracking</h1>
        <p className="text-slate-600 mt-2 max-w-2xl">Check the status of the reports you submitted.</p>
        <div className="mt-7"><TrackingList /></div>
      </Shell>
    </RoleGate>
  );
}
