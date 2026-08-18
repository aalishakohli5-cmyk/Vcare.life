import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export async function POST({ request }) {
    // Validate environment variables
    if (!env.BLAND_AI_API_KEY) {
        return json(
            { success: false, error: 'Bland API key is not configured' },
            { status: 500 }
        );
    }

    try {
        const {
            phoneNumber,
            seniorName,
            seniorId,
            medicationId,
            medicationName,
            dosage
        } = await request.json();

        if (!phoneNumber) {
            return json(
                { success: false, error: 'Senior phone number is missing' },
                { status: 400 }
            );
        }

        const body = {
            phone_number: phoneNumber,

            task: `
You are Vcare, a warm and caring voice companion for ${seniorName || 'the senior'}.

You are checking on their scheduled medication:
Medicine: ${medicationName || 'their medicine'}
Dosage: ${dosage || 'their prescribed dose'}

Politely ask:
"Have you taken your ${medicationName || 'medicine'}?"

Wait for their answer.

If they clearly say yes or confirm they have taken it,
thank them warmly and end the check-in.

If they say no, gently remind them to take it as prescribed.

Keep this call very short and natural.
            `.trim(),

            metadata: {
                senior_id: seniorId,
                medication_id: medicationId
            },

            ...(env.BLAND_WEBHOOK_URL
                ? { webhook: env.BLAND_WEBHOOK_URL }
                : {})
        };

        const response = await fetch('https://api.bland.ai/v1/calls', {
            method: 'POST',
            headers: {
                authorization: env.BLAND_AI_API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
            console.error('Bland API error:', {
                status: response.status,
                message: data?.message,
                error: data
            });

            return json(
                {
                    success: false,
                    error: data?.message || 'Failed to initiate Vcare call'
                },
                { status: response.status }
            );
        }

        console.info('Call initiated successfully:', {
            callId: data.call_id,
            seniorId: seniorId
        });

        return json({
            success: true,
            callId: data.call_id ?? null
        });
    } catch (error) {
        console.error('Call endpoint error:', error);

        return json(
            {
                success: false,
                error: 'Unable to start Vcare call. Please try again.'
            },
            { status: 500 }
        );
    }
}
