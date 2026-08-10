# docs: add Fly.io and Railway deployment recipes

## Summary

`docs/DEPLOYMENT.md` covers Docker Compose and Render. Add step-by-step
deployment recipes for Fly.io and Railway, including service config, environment
variables, and health-check notes.

## Why it matters

More deployment paths lower the barrier for self-hosting the platform, which
matters for a security project where some teams prefer to run their own
instance.

## Acceptance Criteria

- [ ] Fly.io recipe: `fly.toml` outline, build steps, env vars, health check
- [ ] Railway recipe: service config, env vars, persistent volume note for Postgres
- [ ] Both recipes document the required `SECRET_KEY` and `DATABASE_URL` settings
- [ ] Existing Render/Docker sections are left intact

## Tech Stack

Markdown · fly.toml · Railway config
