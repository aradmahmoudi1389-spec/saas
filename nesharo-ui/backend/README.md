# Nesharo Backend

Modular REST API for the Nesharo personal-brand intelligence product.

## Architecture

- Fastify application with versioned routes under `/api/v1`.
- PostgreSQL persistence through Prisma.
- HttpOnly session cookie backed by hashed session tokens; short-lived JWTs are returned for API clients.
- Zod boundary validation and a consistent `{ ok, data | error }` response envelope.
- Role middleware for `USER`, `ADMIN`, and `SUPER_ADMIN`.
- Provider adapters remain isolated from domain modules: AI, SMS, Instagram, and payments can be wired without changing route contracts.
- Long-running AI, Instagram sync, report, and notification work should be moved to a Redis-backed worker before production launch.

## Local development

```bash
cp .env.example .env
pnpm install
pnpm prisma generate
pnpm prisma migrate dev --name init
pnpm dev
```

## Supabase PostgreSQL

Create a Supabase project and copy its connection strings into `.env`:

- `DATABASE_URL` should use the Supavisor transaction pooler on port `6543` with `pgbouncer=true` for the API runtime.
- `DIRECT_URL` should use the direct database host on port `5432` for Prisma migrations.
- Keep both values server-side and never expose them through frontend environment variables.

Run migrations against the direct connection:

```bash
pnpm prisma migrate dev --name init
```

For CI or deployment, set `DATABASE_URL` and `DIRECT_URL` as encrypted environment variables before running Prisma commands.

Swagger UI is available at `/docs`; health check is `/health`.

No external provider is active by default. Configure credentials through environment variables or an admin-only secret manager integration. Never put provider keys in frontend code.
