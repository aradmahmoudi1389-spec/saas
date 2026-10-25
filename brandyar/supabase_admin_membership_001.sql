BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';
CREATE TABLE IF NOT EXISTS public.admin_memberships (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL UNIQUE REFERENCES auth.users(id),
 role text NOT NULL CHECK(role IN ('owner','admin','crm_manager','content_manager','analyst')),
 active boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE public.admin_memberships ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.admin_memberships FROM anon, authenticated;
GRANT SELECT ON public.admin_memberships TO authenticated;
GRANT ALL ON public.admin_memberships TO service_role;
DROP POLICY IF EXISTS admin_membership_read_self ON public.admin_memberships;
CREATE POLICY admin_membership_read_self ON public.admin_memberships
 FOR SELECT TO authenticated USING (user_id=auth.uid() AND active);
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assessments ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.leads, public.assessments FROM anon, authenticated;
COMMIT;
