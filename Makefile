.PHONY: dev down backend frontend test lint contract e2e git-hooks issues topics

## Install the repo git hooks (commit-msg + pre-commit). Run once after clone.
git-hooks:
	git config core.hooksPath .githooks
	@chmod +x .githooks/commit-msg .githooks/pre-commit
	@echo "Git hooks installed from .githooks/ (Conventional Commits + safety checks)."
	@echo "See docs/GIT_WORKFLOW.md for the full workflow."

## Start the full stack (Postgres, Redis, API, worker, dashboard)
dev:
	docker compose up -d --build

## Stop the stack
down:
	docker compose down

## Backend-only development server (local sqlite + venv)
backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

## Frontend dev server
frontend:
	cd frontend && npm run dev

## Backend test suite
test:
	cd backend && .venv/bin/python -m pytest -q

## Frontend lint + typecheck
lint:
	cd frontend && npm run lint && npx tsc --noEmit

## Soroban contract tests (run in the stellar-threatnet-contract repo)
contract:
	@echo "Soroban contract lives in stellar-threatnet-contract:"
	@echo "  git clone https://github.com/smog123/stellar-threatnet-contract.git && cargo test"

## End-to-end smoke test (backend on :8000 must be running)
e2e:
	PYTHONPATH=cli backend/.venv/bin/python -m stellar_threatnet_cli.cli --api-url http://localhost:8000/api/v1 stats

## Create the planned GitHub issues in one run (requires gh + auth)
issues:
	scripts/create_issues.sh --app smog123/stellar-threatnet-app

## Add discoverability topics to the GitHub repo (requires gh + auth)
topics:
	.github/scripts/add-topics.sh
