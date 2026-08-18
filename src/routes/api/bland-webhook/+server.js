import { json } from '@sveltejs/kit';
import { createClient } from '@supabase/supabase-js';
import { env } from '$env/dynamic/private';
import crypto from 'crypto';

/**
 * Verify webhook signature from Bland AI
 * Prevents unauthorized call log manipulation
 */
function verifyWebhookSignature(payload, signature) {
    const secret = env.BLAND_WEBHOOK_SECRET || 'dev-secret';
    const computedSignature = crypto
        .createHmac('sha256', secret)
        .update(JSON.stringify(payload))
        .digest('hex');
    
    return crypto.timingSafeEqual(
        Buffer.from(signature || ''),
        Buffer.from(computedSignature)
    );
}

export async function POST({ request }) {
    try {
        const payload = await request.json();
        const signature = request.headers.get('x-bland-signature');

        // Verify webhook authenticity
        if (!verifyWebhookSignature(payload, signature)) {
            console.warn('Webhook signature verification failed');
            return json(
                { success: false, error: 'Unauthorized webhook' },
                { status: 401 }
            );
        }

        console.info('Webhook received and verified:', {
            callId: payload.call_id,
            timestamp: new Date().toISOString()
        });

        const transcript =
            payload.concatenated_transcript ||
            payload.transcript ||
            '';

        const metadata = payload.metadata || {};
        const seniorId = metadata.senior_id;
        const medicationId = metadata.medication_id;

        if (!seniorId || !medicationId) {
            console.error('Webhook missing required metadata:', { metadata });
            return json(
                {
                    success: false,
                    error: 'Missing medication metadata'
                },
                { status: 400 }
            );
        }

        // Check for medication confirmation in transcript
        const text = transcript.toLowerCase();
        const confirmed =
            text.includes('yes') ||
            text.includes('i took it') ||
            text.includes('i have taken') ||
            text.includes('already took');

        if (!confirmed) {
            console.info('Medication not confirmed in call:', {
                seniorId,
                medicationId
            });
            return json({
                success: true,
                updated: false
            });
        }

        // Validate Supabase credentials
        if (!env.SUPABASE_URL || !env.SUPABASE_SECRET_KEY) {
            console.error(
                'Missing Supabase server environment variables'
            );
            return json(
                {
                    success: false,
                    error: 'Server misconfiguration'
                },
                { status: 500 }
            );
        }

        // Initialize Supabase admin client (server-side only)
        const supabaseAdmin = createClient(
            env.SUPABASE_URL,
            env.SUPABASE_SECRET_KEY
        );

        // Update medication record
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
            console.error('Medication update failed:', {
                error: error.message,
                medicationId,
                seniorId
            });
            return json(
                {
                    success: false,
                    error: 'Failed to update medication status'
                },
                { status: 500 }
            );
        }

        console.info('Medication marked as taken:', {
            medicationId,
            seniorId,
            timestamp: data?.taken_at
        });

        return json({
            success: true,
            updated: true,
            medicationId: data?.id
        });
    } catch (error) {
        console.error('Webhook processing failed:', {
            error: error.message,
            stack: error.stack
        });
        return json(
            {
                success: false,
                error: 'Webhook processing failed'
            },
            { status: 500 }
        );
    }
}
