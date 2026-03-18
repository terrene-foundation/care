# Task 6061: Add Frontend CI Job to GitHub Actions

**Milestone**: M43
**Priority**: High
**Effort**: Medium
**Status**: Active

## Description

The GitHub Actions CI pipeline currently only tests the Python backend. The React/TypeScript frontend has no CI coverage — lint failures, build errors, and test failures go undetected until a developer notices them locally. This task adds a `frontend` CI job that runs on every push and PR.

Job steps:

1. `npm ci` — clean install
2. `npm run lint` — ESLint
3. `npm run build` — TypeScript compilation + Vite/Next.js build
4. `npm test -- --watchAll=false` — Jest unit tests (non-interactive)

## Acceptance Criteria

- [ ] `.github/workflows/ci.yml` has a `frontend` job (or the existing CI file has a `frontend` step)
- [ ] Job runs on: `push` to main, `pull_request` to main
- [ ] Job uses Node.js version pinned to match the version in `.nvmrc` or `package.json` engines field
- [ ] `npm ci` step uses dependency caching (actions/cache or actions/setup-node with cache)
- [ ] Build artifacts are not uploaded (CI only, no deployment)
- [ ] Job fails fast on lint errors
- [ ] Job fails if TypeScript compilation has errors
- [ ] Existing Python CI job is unaffected
- [ ] CI passes on the current main branch (no pre-existing failures introduced)

## Dependencies

- Task 6050+ (M42 data wiring, so that the frontend builds cleanly against real data expectations)
