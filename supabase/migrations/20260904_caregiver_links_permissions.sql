-- Allow authenticated users to access only the caregiver links permitted by RLS.
-- This is required when profile policies inspect caregiver_links during role changes.

GRANT SELECT, DELETE ON TABLE public.caregiver_links TO authenticated;
