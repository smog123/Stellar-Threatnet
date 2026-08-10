# Planned Issue Registry

Each file in this directory is a scoped, human-readable issue definition:
Summary, why it matters, Acceptance Criteria, and Tech Stack. They are the
source material for the "planned issues" section of the Wave submission and
for contributors looking for scoped work.

The executable issue-creation tool is `scripts/create_issues.sh` (top-level
`scripts/`), which creates this batch on GitHub in one run — see the
[Makefile](../../Makefile) `issues` target. Issue files here are the written
registry; the script is the action.
