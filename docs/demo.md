# Phase 1 demo

1. Follow the README to migrate, seed, and run both servers.
2. Open the dashboard. Expect 1 active incident, 2 missing-person reports,
   2 unidentified patients, 1 suggested match, 1 needing investigation, 0 verified.
3. Search `Coast` to display the closed storm exercise. Switch status to Active
   to show the empty-filter state. Clear search to see the flood exercise.
4. Follow the navigation links: later workflows visibly remain unavailable.
5. Stop the API and refresh: the dashboard displays an error rather than fake data.
   Restart the API and select Try again to recover.
6. Explain that the candidate is seeded mock data, not inference. No algorithm
   verifies an identity or contacts a family.

The dashboard is responsive across desktop and narrow screens. Totals always cover
all synthetic exercises; filters affect only the incident directory. No real photos
or personal details are used. The human review workflow is a future phase.
