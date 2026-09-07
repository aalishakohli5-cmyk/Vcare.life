import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

/**
 * Detects whether the routine item is a walk, yoga/exercise, diet/hydration, health check, or medication
 */
function detectCategory(name = '', details = '', explicitCategory = '') {
    if (explicitCategory) return explicitCategory.toLowerCase();
    const text = `${name} ${details}`.toLowerCase();
    if (
        text.includes('sos') ||
        text.includes('emergency') ||
        text.includes('urgent') ||
        text.includes('panic') ||
        text.includes('help')
    ) {
        return 'sos';
    }
    if (
        text.includes('walk') ||
        text.includes('stroll') ||
        text.includes('jog') ||
        text.includes('step')
    ) {
        return 'walk';
    }
    if (
        text.includes('yoga') ||
        text.includes('stretch') ||
        text.includes('breath') ||
        text.includes('pranayam') ||
        text.includes('exercise') ||
        text.includes('workout')
    ) {
        return 'yoga';
    }
    if (
        text.includes('water') ||
        text.includes('hydrat') ||
        text.includes('drink') ||
        text.includes('diet') ||
        text.includes('meal') ||
        text.includes('breakfast') ||
        text.includes('lunch') ||
        text.includes('dinner') ||
        text.includes('fruit') ||
        text.includes('salad') ||
        text.includes('food')
    ) {
        return 'diet';
    }
    if (
        text.includes('bp') ||
        text.includes('blood pressure') ||
        text.includes('sugar') ||
        text.includes('glucose') ||
        text.includes('pulse') ||
        text.includes('vitals') ||
        text.includes('check')
    ) {
        return 'health_check';
    }
    return 'medicine';
}

/**
 * Builds a warm, natural, category-specific prompt for Bland AI
 */
function generateTaskPrompt({ seniorName, routineName, details, category }) {
    const sName = seniorName || 'the senior';
    const rName = routineName || 'your scheduled health routine';
    const dNotes = details ? ` (${details})` : '';

    let specificInstructions = '';

    if (category === 'sos') {
        specificInstructions = `
EMERGENCY ALERT CALL:
You are calling ${sName}'s designated caregiver because ${sName} pressed the emergency SOS button on their Vcare dashboard.
1. Immediately deliver the emergency notice with calm, clear urgency:
   "Hello, this is an urgent alert from Vcare. ${sName} just pressed their emergency SOS button on their Vcare dashboard."
2. State the required caregiver action clearly:
   "Please check on ${sName} immediately. If you cannot reach them or believe they are in danger, please contact local emergency services right away."
3. Ask the caregiver to acknowledge:
   "Can you confirm you have received this alert for ${sName}?"
4. When they acknowledge:
   "Thank you. This emergency alert has been recorded. Please reach out to ${sName} as soon as possible."
`;
    } else if (category === 'walk') {
        specificInstructions = `
You are calling to check in on their scheduled walk: "${rName}"${dNotes}.
1. Start with a warm, cheerful greeting:
   "Hello ${sName}! This is Vcare calling. I was just checking in to see if you've had a chance to go for your ${rName} today, or if you're getting ready to head out?"
2. If they say YES (or already finished their walk):
   Celebrate warmly: "That's wonderful! Getting fresh air and a good walk does so much good for your energy, heart, and joints. Keep up the great work!"
3. If they say NO (or haven't gone yet):
   Encourage them gently without any pressure: "No rush at all! Whenever you feel ready and the weather is nice, even a short, relaxed stroll around the house or garden is wonderful. Please wear comfortable shoes and take it easy."
`;
    } else if (category === 'yoga') {
        specificInstructions = `
You are calling to check in on their scheduled yoga or exercise session: "${rName}"${dNotes}.
1. Greet them warmly:
   "Hello ${sName}! This is Vcare with a gentle check-in. Have you had a chance to do your ${rName} practice today?"
2. If they say YES:
   Encourage them warmly: "Fantastic! Taking that quiet time for gentle stretching and deep breathing brings so much peace, flexibility, and good circulation to your day."
3. If they say NO:
   Encourage gently: "Take your time! Whenever you have a quiet moment, a few light stretches and deep breaths at your own pace will feel wonderful. Only do what feels comfortable for your body."
`;
    } else if (category === 'diet') {
        specificInstructions = `
You are calling for their scheduled diet or hydration reminder: "${rName}"${dNotes}.
1. Greet them warmly:
   "Hello ${sName}! This is Vcare with a quick wellness reminder for your ${rName}. Have you had it yet?"
2. If they say YES:
   Thank them warmly: "Wonderful! Staying well-nourished and properly hydrated makes such a big difference in how you feel each day."
3. If they say NO:
   Gently remind them: "Please take a moment to enjoy your ${rName} when convenient. Nourishing your body is so important!"
`;
    } else if (category === 'health_check') {
        specificInstructions = `
You are calling for their scheduled health check: "${rName}"${dNotes}.
1. Greet them respectfully:
   "Hello ${sName}! This is Vcare checking in for your ${rName}. Have you been able to take that reading today?"
2. If they share their reading or confirm yes:
   Thank them warmly: "Thank you for letting me know! Keeping consistent track gives you and your family great peace of mind."
3. If they have not done it:
   Gently remind them: "Please take a few quiet moments to check it when convenient and note down the numbers."
`;
    } else {
        // Medicine / Prescription
        specificInstructions = `
You are checking on their scheduled medication: "${rName}"${dNotes}.
1. Politely ask:
   "Hello ${sName}! This is Vcare checking in on your daily routine. Have you taken your ${rName}?"
2. If they clearly say YES:
   Thank them warmly: "Thank you for letting me know! You're doing great staying on schedule. Keep up the good care!"
3. If they say NO:
   Remind them gently: "Please remember to take your ${rName} with a glass of water when convenient, as prescribed."
`;
    }

    return `
You are Vcare, a warm, polite, and compassionate voice companion for ${sName}.

${specificInstructions}

GENERAL CONVERSATIONAL GUIDELINES:
- Listen attentively to their response and speak with patience, warmth, and respect.
- If they mention feeling tired, unwell, dizzy, or in pain, immediately express genuine empathy: "I'm so sorry you're not feeling well. Please rest comfortably, drink some water, and if you need anything, don't hesitate to reach out to your family or doctor."
- Keep the call brief, cheerful, and natural (under 1-2 minutes).
- Sign off warmly: "Take care, ${sName}, have a peaceful and wonderful day!"
`.trim();
}

export async function POST({ request }) {
    // Validate environment variables
    if (!env.BLAND_AI_API_KEY) {
        return json(
            { success: false, error: 'Bland API key is not configured' },
            { status: 500 }
        );
    }

    try {
        const bodyData = await request.json();
        const {
            phoneNumber,
            seniorName,
            seniorId,
            medicationId,
            routineId,
            medicationName,
            routineName,
            dosage,
            details,
            category
        } = bodyData;

        if (!phoneNumber) {
            return json(
                { success: false, error: 'Senior phone number is missing' },
                { status: 400 }
            );
        }

        const effectiveRoutineName = routineName || medicationName || 'daily health routine';
        const effectiveDetails = details || dosage || '';
        const detectedCat = detectCategory(effectiveRoutineName, effectiveDetails, category);
        const taskPrompt = generateTaskPrompt({
            seniorName,
            routineName: effectiveRoutineName,
            details: effectiveDetails,
            category: detectedCat
        });

        const body = {
            phone_number: phoneNumber,
            task: taskPrompt,
            metadata: {
                senior_id: seniorId,
                medication_id: routineId || medicationId || null,
                routine_name: effectiveRoutineName,
                category: detectedCat
            },
            ...(env.BLAND_WEBHOOK_URL ? { webhook: env.BLAND_WEBHOOK_URL } : {})
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
            seniorId,
            category: detectedCat
        });

        return json({
            success: true,
            callId: data.call_id ?? null,
            category: detectedCat
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
