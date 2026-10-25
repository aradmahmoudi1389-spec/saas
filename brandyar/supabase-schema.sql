create extension if not exists pgcrypto;

create table if not exists public.leads (
  id uuid primary key default gen_random_uuid(),
  mobile text not null unique,
  consent_follow_up boolean not null default false,
  source_page text,
  source_campaign text,
  status text not null default 'new' check (status in ('new', 'contacted', 'qualified', 'converted', 'archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.assessments (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid references public.leads(id) on delete set null,
  session_id uuid not null unique,
  answers jsonb not null default '{}'::jsonb,
  insight jsonb,
  full_report jsonb,
  current_step text not null default 'started' check (current_step in ('started', 'completed', 'preview_shown', 'report_unlocked')),
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create index if not exists assessments_lead_id_idx on public.assessments(lead_id);
create index if not exists assessments_created_at_idx on public.assessments(created_at desc);
create index if not exists leads_created_at_idx on public.leads(created_at desc);

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end;
$$;

drop trigger if exists leads_set_updated_at on public.leads;
create trigger leads_set_updated_at before update on public.leads
for each row execute function public.set_updated_at();

alter table public.leads enable row level security;
alter table public.assessments enable row level security;
revoke all on public.leads from anon, authenticated;
revoke all on public.assessments from anon, authenticated;
drop policy if exists leads_public_insert on public.leads;
drop policy if exists assessments_public_insert on public.assessments;

-- All reads and writes use the server's service-role key through authenticated admin routes.
