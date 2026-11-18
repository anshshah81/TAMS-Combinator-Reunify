# Dependency notes

Direct dependencies are pinned; npm's lockfile records transitive frontend versions.
The foundation retains Next.js 15 and its matching ESLint configuration. React and
Next.js are pinned to patched versions available at implementation time. A PostCSS
override uses 8.5.33 for both the direct and Next.js transitive dependency; rerun the
production build when changing it.

Validation on 2026-11-17:

- `npm audit --omit=dev`: zero reported vulnerabilities.
- Full `npm audit`: 13 high-severity entries in development lint dependencies,
  all tracing to picomatch's repeated-extglob regular-expression denial of service
  advisory, GHSA-fc5q-39xc-vjpf. The registry's latest picomatch was 4.0.7 and the
  advisory includes that version. npm suggests downgrades of lint tooling, including
  a mismatched Next.js 14 configuration. Those breaking changes were not applied.
- ESLint 9 is deprecated upstream but retained for compatibility with this Next.js
  15 setup. Plan a tested toolchain upgrade and revisit the audit before deployment.

These lint dependencies process this repository's developer-controlled source and
patterns, not uploaded user data. Do not accept untrusted lint configuration or glob
patterns. The remaining audit findings are not claimed to be fixed.

No AI dependencies or weights are installed. Future model and checkpoint licensing
must be reviewed independently before inference is enabled. This document is not a
production security certification.
