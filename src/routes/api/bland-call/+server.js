import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export async function POST({ request }) {
    try {
        const { phoneNumber, seniorName } = await request.json();

        if (!phoneNumber) {
            return json(
                { success: false, error: 'Senior phone number is missing' },
                { status: 400 }
            );
        }

        if (!env.BLAND_AI_API_KEY) {
            return json(
                { success: false, error: 'Bland API key is not configured' },
                { status: 500 }
            );
        }

        const body = {
            phone_number: phoneNumber,

            task: `
You are Vcare, a warm and caring voice companion for ${seniorName || 'the senior'}.

Politely ask whether they have taken their scheduled medicine.

If they say yes, acknowledge it warmly.
If they say no, gently remind them.

Keep the conversation short, natural and supportive.
    `.trim(),



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
            console.error('Bland error:', data);

            return json(
                {
                    success: false,
                    error: data?.message || 'Bland call failed'
                },
                { status: response.status }
            );
        }

        return json({
            success: true,
            callId: data.call_id ?? null
        });
    } catch (error) {
        console.error('Call error:', error);

        return json(
            {
                success: false,
                error: 'Unable to start Vcare call'
            },
            { status: 500 }
        );
    }
}
