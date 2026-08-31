/**
 * @param {{
 *   phone: string,
 *   firstName: string,
 *   userId: string,
 *   pendingMedicine: { id?: string | number, name?: string, dosage?: string } | null
 * }} options
 */
export async function startSampleCall({
	phone,
	firstName,
	userId,
	pendingMedicine
}) {
	if (!phone) {
		throw new Error(
			'No phone number found for this account. Please update your profile.'
		);
	}

	const response = await fetch('/api/bland-call', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			phoneNumber: phone,
			seniorName: firstName,
			seniorId: userId,
			medicationId: pendingMedicine?.id || null,
			medicationName: pendingMedicine?.name || 'daily health check-in',
			dosage: pendingMedicine?.dosage || 'prescribed dose'
		})
	});

	const data = await response.json();

	if (!response.ok) {
		throw new Error(data.error || 'Could not start the call');
	}

	return data;
}
