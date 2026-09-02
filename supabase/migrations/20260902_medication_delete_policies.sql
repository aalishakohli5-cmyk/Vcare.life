-- Allow authenticated seniors and their linked caregivers to delete medications.
-- This migration is idempotent and can be safely run in the Supabase SQL editor.

DROP POLICY IF EXISTS "Seniors can delete own medications" ON public.medications;
CREATE POLICY "Seniors can delete own medications"
    ON public.medications FOR DELETE
    USING (auth.uid() = senior_id);

DROP POLICY IF EXISTS "Caregivers can delete medications for linked seniors" ON public.medications;
CREATE POLICY "Caregivers can delete medications for linked seniors"
    ON public.medications FOR DELETE
    USING (
        EXISTS (
            SELECT 1
            FROM public.caregiver_links
            WHERE caregiver_links.caregiver_id = auth.uid()
              AND caregiver_links.senior_id = medications.senior_id
        )
    );
