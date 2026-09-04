const ACTIVE_SENIOR_KEY = 'vcare-active-senior-id';

/**
 * @template {{ id: string }} T
 * @param {T[]} seniors
 * @returns {T | null}
 */
export function chooseCareRecipient(seniors) {
	if (!Array.isArray(seniors) || seniors.length === 0) return null;

	let savedId = '';
	if (typeof window !== 'undefined') {
		savedId = window.localStorage.getItem(ACTIVE_SENIOR_KEY) || '';
	}

	const selected = seniors.find((person) => person.id === savedId) || seniors[0];
	rememberCareRecipient(selected.id);
	return selected;
}

/** @param {string} seniorId */
export function rememberCareRecipient(seniorId) {
	if (typeof window !== 'undefined' && seniorId) {
		window.localStorage.setItem(ACTIVE_SENIOR_KEY, seniorId);
	}
}

export function clearCareRecipient() {
	if (typeof window !== 'undefined') {
		window.localStorage.removeItem(ACTIVE_SENIOR_KEY);
	}
}

/** @param {string} value */
export function normalizeCareInviteCode(value) {
	const compact = String(value || '')
		.toUpperCase()
		.replace(/[^A-Z0-9]/g, '');

	if (compact.startsWith('VCARE')) {
		return `VCARE-${compact.slice(5, 11)}`;
	}

	return compact.length === 6 ? `VCARE-${compact}` : String(value || '').trim().toUpperCase();
}

/**
 * Converts database/RPC errors into language that is useful to a person using Vcare.
 * @param {{ message?: string } | null | undefined} error
 * @param {'generate' | 'redeem'} action
 */
export function careInviteErrorMessage(error, action) {
	const message = error?.message || '';
	const databaseIsMissingInviteFunctions =
		message.includes('schema cache') ||
		message.includes('generate_care_invite') ||
		message.includes('redeem_care_invite');

	if (databaseIsMissingInviteFunctions) {
		return 'Caregiver invitations are being set up. Please try again after the database update is installed.';
	}

	return action === 'generate'
		? 'We could not create an invitation code. Please try again.'
		: 'This code is invalid, expired, or already used. Ask the senior to generate a new one.';
}
