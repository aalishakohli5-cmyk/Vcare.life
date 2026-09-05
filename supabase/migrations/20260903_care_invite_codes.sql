-- Secure, short-lived pairing codes for linking seniors and caregivers.
-- Run through the Supabase migration workflow before deploying the UI.

CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;

ALTER TABLE public.caregiver_links
    ADD COLUMN IF NOT EXISTS relationship TEXT;

CREATE TABLE IF NOT EXISTS public.care_invites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    senior_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    code_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    used_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS care_invites_senior_active_idx
    ON public.care_invites (senior_id, expires_at DESC)
    WHERE used_at IS NULL;

ALTER TABLE public.care_invites ENABLE ROW LEVEL SECURITY;

-- Invite rows and hashes are intentionally unavailable through direct table access.
-- Only the validated SECURITY DEFINER functions below can create or redeem them.

-- The app reads and removes links directly; RLS below still limits each person
-- to links they belong to. Direct INSERT remains blocked and goes through the RPC.
GRANT SELECT, DELETE ON TABLE public.caregiver_links TO authenticated;

DROP POLICY IF EXISTS "Caregivers can insert links" ON public.caregiver_links;

CREATE OR REPLACE FUNCTION public.generate_care_invite()
RETURNS TABLE (code TEXT, expires_at TIMESTAMPTZ)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, extensions
AS $$
DECLARE
    current_user_id UUID := auth.uid();
    plain_code TEXT;
    expiry TIMESTAMPTZ := timezone('utc'::text, now()) + interval '15 minutes';
BEGIN
    IF current_user_id IS NULL THEN
        RAISE EXCEPTION 'You must be signed in to create a care invitation.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM public.profiles
        WHERE id = current_user_id
          AND role = 'senior'
          AND onboarding_complete = TRUE
    ) THEN
        RAISE EXCEPTION 'Complete your senior profile before inviting a caregiver.';
    END IF;

    UPDATE public.care_invites AS invite
       SET expires_at = timezone('utc'::text, now())
     WHERE invite.senior_id = current_user_id
       AND invite.used_at IS NULL
       AND invite.expires_at > timezone('utc'::text, now());

    LOOP
        plain_code := 'VCARE-' || upper(substr(replace(gen_random_uuid()::text, '-', ''), 1, 6));
        BEGIN
            INSERT INTO public.care_invites (senior_id, code_hash, expires_at)
            VALUES (
                current_user_id,
                encode(digest(plain_code, 'sha256'), 'hex'),
                expiry
            );
            EXIT;
        EXCEPTION WHEN unique_violation THEN
            -- Extremely unlikely; generate a fresh code without exposing collisions.
        END;
    END LOOP;

    RETURN QUERY SELECT plain_code, expiry;
END;
$$;

CREATE OR REPLACE FUNCTION public.redeem_care_invite(
    invite_code TEXT,
    relationship_to_senior TEXT DEFAULT NULL
)
RETURNS TABLE (senior_id UUID, senior_name TEXT)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, extensions
AS $$
DECLARE
    current_user_id UUID := auth.uid();
    normalized_code TEXT;
    matched_invite public.care_invites%ROWTYPE;
    matched_name TEXT;
BEGIN
    IF current_user_id IS NULL THEN
        RAISE EXCEPTION 'You must be signed in to connect to a senior.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM public.profiles
        WHERE id = current_user_id
          AND role = 'caregiver'
          AND onboarding_complete = TRUE
    ) THEN
        RAISE EXCEPTION 'Complete your caregiver profile before using an invitation code.';
    END IF;

    normalized_code := regexp_replace(upper(coalesce(invite_code, '')), '[^A-Z0-9]', '', 'g');
    IF normalized_code LIKE 'VCARE%' THEN
        normalized_code := 'VCARE-' || substr(normalized_code, 6);
    END IF;

    IF length(normalized_code) <> 12 THEN
        RAISE EXCEPTION 'Enter a valid Vcare invitation code.';
    END IF;

    SELECT * INTO matched_invite
      FROM public.care_invites
     WHERE code_hash = encode(digest(normalized_code, 'sha256'), 'hex')
       AND used_at IS NULL
       AND expires_at > timezone('utc'::text, now())
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'This invitation code is invalid, expired, or already used.';
    END IF;

    IF matched_invite.senior_id = current_user_id THEN
        RAISE EXCEPTION 'Use a different caregiver account to redeem this code.';
    END IF;

    INSERT INTO public.caregiver_links (caregiver_id, senior_id, relationship)
    VALUES (
        current_user_id,
        matched_invite.senior_id,
        nullif(trim(relationship_to_senior), '')
    )
    ON CONFLICT (caregiver_id, senior_id) DO UPDATE
       SET relationship = coalesce(EXCLUDED.relationship, caregiver_links.relationship);

    UPDATE public.care_invites
       SET used_at = timezone('utc'::text, now()), used_by = current_user_id
     WHERE id = matched_invite.id;

    SELECT full_name INTO matched_name
      FROM public.profiles
     WHERE id = matched_invite.senior_id;

    RETURN QUERY SELECT matched_invite.senior_id, coalesce(matched_name, 'Senior');
END;
$$;

REVOKE ALL ON FUNCTION public.generate_care_invite() FROM PUBLIC;
REVOKE ALL ON FUNCTION public.redeem_care_invite(TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.generate_care_invite() TO authenticated;
GRANT EXECUTE ON FUNCTION public.redeem_care_invite(TEXT, TEXT) TO authenticated;

DROP POLICY IF EXISTS "Seniors can view linked caregiver profiles" ON public.profiles;
CREATE POLICY "Seniors can view linked caregiver profiles"
    ON public.profiles FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.caregiver_links
            WHERE caregiver_links.senior_id = auth.uid()
              AND caregiver_links.caregiver_id = profiles.id
        )
    );

DROP POLICY IF EXISTS "Care circle members can remove links" ON public.caregiver_links;
CREATE POLICY "Care circle members can remove links"
    ON public.caregiver_links FOR DELETE
    USING (auth.uid() = caregiver_id OR auth.uid() = senior_id);
