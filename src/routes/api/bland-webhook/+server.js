import { json } from '@sveltejs/kit';
import { createClient } from '@supabase/supabase-js';
import { env } from '$env/dynamic/private';

export async function POST({ request }) {
    try {
        const payload = await request.json();

        console.log('Bland webhook received:', payload.call_id);

        const transcript =
            payload.concatenated_transcript ||
            payload.transcript ||
            '';

        const metadata = payload.metadata || {};

        const seniorId = metadata.senior_id;
        const medicationId = metadata.medication_id;

        if (!seniorId || !medicationId) {
            console.error('Missing medication metadata');

            return json({
                success: false,
                error: 'Missing medication metadata'
            });
        }

        /*
            For our demo:
            check the HUMAN portion of the conversation for
            a clear medication confirmation.
        */
        const text = transcript.toLowerCase();

        const confirmed =
            text.includes('yes') ||
            text.includes('i took it') ||
            text.includes('i have taken') ||
            text.includes('already took');

        if (!confirmed) {
            console.log('Medication was not confirmed');

            return json({
                success: true,
                updated: false
            });
        }
        if (!env.SUPABASE_URL || !env.SUPABASE_SECRET_KEY) {
            console.error('Missing Supabase server environment variables');

            return json(
                {
                    success: false,
                    error: 'Supabase server configuration is missing'
                },
                { status: 500 }
            );
        }

        const supabaseAdmin = createClient(
            env.SUPABASE_URL,
            env.SUPABASE_SECRET_KEY
        );

        const { data, error } = await supabaseAdmin
            .from('medications')
            .update({
                taken: true,
                taken_at: new Date().toISOString()
            })
            .eq('id', medicationId)
            .eq('senior_id', seniorId)
            .select()
            .single();

        if (error) {
            console.error('Medication update error:', error);

            return json(
                {
                    success: false,
                    error: 'Medication could not be updated'
                },
                { status: 500 }
            );
        }

        console.log('Medication marked taken:', data?.id);

        return json({
            success: true,
            updated: true
        });
    } catch (error) {
        console.error('Webhook error:', error);

        return json(
            {
                success: false,
                error: 'Webhook processing failed'
            },
            { status: 500 }
        );
    }
}
