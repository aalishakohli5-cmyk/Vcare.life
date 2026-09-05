<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	let { role, dashboardHref } = $props();

	let loading = $state(true);
	let deleting = $state(false);
	let switchingRole = $state(false);
	let confirmingDelete = $state(false);
	let userId = $state('');
	let email = $state('');
	let fullName = $state('');
	let actualRole = $state('');
	let provider = $state('Email');
	let errorMessage = $state('');
	let roleMessage = $state('');

	const roleDetails = $derived(
		actualRole === 'caregiver'
			? {
				label: 'Caregiver / Family Member',
				description: 'Giving care and staying informed about a loved one.'
			}
			: {
				label: 'Senior / Loved One',
				description: 'Receiving care, reminders, and daily support.'
			}
	);
	const nextRole = $derived(actualRole === 'caregiver' ? 'senior' : 'caregiver');
	const nextRoleLabel = $derived(nextRole === 'caregiver' ? 'Caregiver' : 'Senior');

	onMount(async () => {
		const {
			data: { user },
			error
		} = await supabase.auth.getUser();

		if (error || !user) {
			goto(`/auth?role=${role}`);
			return;
		}

		userId = user.id;
		email = user.email || 'No email address available';
		provider = user.app_metadata?.provider === 'google' ? 'Google' : 'Email';

		const { data: profile } = await supabase
			.from('profiles')
			.select('full_name, role')
			.eq('id', user.id)
			.maybeSingle();

		fullName =
			profile?.full_name ||
			user.user_metadata?.full_name ||
			user.user_metadata?.name ||
			'Vcare member';
		actualRole = profile?.role || role;
		loading = false;
	});

	async function signOut() {
		await supabase.auth.signOut();
		goto('/');
	}

	async function switchRole() {
		switchingRole = true;
		roleMessage = '';

		try {
			const { data, error } = await supabase
				.from('profiles')
				.update({ role: nextRole })
				.eq('id', userId)
				.select('role')
				.maybeSingle();

			if (error || !data?.role) {
				throw new Error(error?.message || 'Your role could not be changed. Please try again.');
			}

			actualRole = data.role;
			await goto(data.role === 'caregiver' ? '/caregiver/dashboard' : '/senior/dashboard');
		} catch (error) {
			const technicalMessage = error instanceof Error ? error.message : '';
			roleMessage = technicalMessage.includes('permission denied')
				? 'Role switching needs a small database permission update. Please ask the site administrator to finish setup.'
				: technicalMessage || 'Your role could not be changed. Please try again.';
			switchingRole = false;
		}
	}

	async function deleteAccount() {
		if (!confirmingDelete) {
			confirmingDelete = true;
			errorMessage = '';
			return;
		}

		deleting = true;
		errorMessage = '';

		try {
			const {
				data: { session }
			} = await supabase.auth.getSession();

			if (!session?.access_token) {
				throw new Error('Your session has expired. Please sign in again before deleting your account.');
			}

			if (!PUBLIC_BACKEND_URL) {
				throw new Error('Account deletion is not available right now. Please try again later.');
			}

			const response = await fetch(`${PUBLIC_BACKEND_URL}/account/`, {
				method: 'DELETE',
				headers: {
					Authorization: `Bearer ${session.access_token}`
				}
			});

			/** @type {{ detail?: string }} */
			let result = {};
			try {
				result = await response.json();
			} catch {
				// The status code still gives a useful fallback if the server returns no JSON.
			}

			if (!response.ok) {
				throw new Error(result.detail || 'We could not delete your account. Please try again.');
			}

			localStorage.removeItem('vcare-reminders');
			await supabase.auth.signOut();
			goto('/?accountDeleted=1');
		} catch (error) {
			errorMessage = error instanceof Error
				? error.message
				: 'We could not delete your account. Please try again.';
			deleting = false;
		}
	}
</script>

<svelte:head>
	<title>Account settings — Vcare.life</title>
	<meta name="description" content="View and manage your Vcare account, sign-in email, care role, and privacy choices." />
</svelte:head>

<main class="settings-page" aria-labelledby="settings-title">
	<a class="back-link" href={dashboardHref}>← Back to dashboard</a>

	<header class="settings-header">
		<p class="eyebrow">YOUR ACCOUNT</p>
		<h1 id="settings-title">Settings</h1>
		<p>See how you are signed in and manage your Vcare account.</p>
	</header>

	{#if loading}
		<div class="loading-card" aria-live="polite">Loading your account…</div>
	{:else}
		<section class="settings-card" aria-labelledby="account-heading">
			<div class="section-heading">
				<span class="section-icon" aria-hidden="true">●</span>
				<div>
					<p class="eyebrow">PERSONAL DETAILS</p>
					<h2 id="account-heading">Your account</h2>
				</div>
			</div>

			<dl class="details-list">
				<div>
					<dt>Name</dt>
					<dd>{fullName}</dd>
				</div>
				<div>
					<dt>Gmail attached</dt>
					<dd>{email}</dd>
					<small>Signed in with {provider}</small>
				</div>
				<div class="role-row">
					<dt>Your role</dt>
					<dd>{roleDetails.label}</dd>
					<small>{roleDetails.description}</small>
					<button type="button" class="switch-role-button" onclick={switchRole} disabled={switchingRole}>
						{switchingRole ? 'Switching role…' : `Switch to ${nextRoleLabel}`}
						<span aria-hidden="true">→</span>
					</button>
				</div>
			</dl>

			{#if roleMessage}
				<p class="error-message account-error" role="alert">{roleMessage}</p>
			{/if}

			<button type="button" class="secondary-button" onclick={signOut}>Sign out</button>
		</section>

		<section class="settings-card danger-card" aria-labelledby="delete-heading">
			<div>
				<p class="eyebrow danger-label">PRIVACY & DATA</p>
				<h2 id="delete-heading">Delete your account</h2>
				<p class="danger-copy">
					This permanently removes your profile and associated Vcare data. The next time you sign in,
					you can choose a new role and set up a new account.
				</p>
			</div>

			{#if confirmingDelete}
				<div class="confirmation" role="alert">
					<strong>Are you sure?</strong>
					<p>This cannot be undone. Your care links, medicines, and call history will also be removed.</p>
					<div class="confirmation-actions">
						<button
							type="button"
							class="secondary-button"
							onclick={() => (confirmingDelete = false)}
							disabled={deleting}
						>
							Cancel
						</button>
						<button type="button" class="delete-button" onclick={deleteAccount} disabled={deleting}>
							{deleting ? 'Deleting account…' : 'Yes, delete permanently'}
						</button>
					</div>
				</div>
			{:else}
				<button type="button" class="delete-button" onclick={deleteAccount}>Delete account</button>
			{/if}

			{#if errorMessage}
				<p class="error-message" role="alert">{errorMessage}</p>
			{/if}
		</section>
	{/if}
</main>

<style>
	.settings-page {
		width: min(920px, calc(100% - 40px));
		margin: 0 auto;
		padding: clamp(36px, 6vw, 76px) 0 80px;
		color: #173f31;
	}

	.back-link {
		display: inline-flex;
		margin-bottom: 34px;
		color: #176d4a;
		font-size: 1.05rem;
		font-weight: 800;
		text-decoration: none;
	}

	.back-link:hover { text-decoration: underline; }

	.settings-header { margin-bottom: 34px; }
	.eyebrow {
		margin: 0 0 8px;
		color: #287653;
		font-size: 0.88rem;
		font-weight: 900;
		letter-spacing: 0.13em;
	}
	.settings-header h1 {
		margin: 0;
		font-size: clamp(2.6rem, 6vw, 4.5rem);
		line-height: 1;
	}
	.settings-header > p:last-child,
	.danger-copy {
		max-width: 690px;
		margin: 16px 0 0;
		color: #53675f;
		font-size: 1.13rem;
		line-height: 1.6;
	}

	.settings-card,
	.loading-card {
		margin-top: 22px;
		padding: clamp(24px, 4vw, 38px);
		border: 1px solid #d9e3dc;
		border-radius: 24px;
		background: #fff;
		box-shadow: 0 14px 34px rgba(21, 67, 50, 0.07);
	}

	.section-heading {
		display: flex;
		align-items: center;
		gap: 16px;
	}
	.section-icon {
		display: grid;
		width: 48px;
		height: 48px;
		place-items: center;
		border-radius: 14px;
		background: #e6f4ca;
		color: #4f892f;
	}
	h2 { margin: 0; font-size: clamp(1.7rem, 3vw, 2.25rem); }

	.details-list { margin: 28px 0; }
	.details-list > div {
		display: grid;
		grid-template-columns: minmax(140px, 0.45fr) 1fr;
		gap: 4px 26px;
		padding: 20px 0;
		border-top: 1px solid #e8eee9;
	}
	dt { color: #596d64; font-size: 1rem; font-weight: 750; }
	dd { margin: 0; color: #133f30; font-size: 1.18rem; font-weight: 850; overflow-wrap: anywhere; }
	.details-list small { grid-column: 2; color: #677a72; font-size: 0.96rem; line-height: 1.45; }
	.switch-role-button {
		grid-column: 2;
		justify-self: start;
		display: inline-flex;
		min-height: 48px;
		align-items: center;
		gap: 12px;
		margin-top: 12px;
		padding: 10px 18px;
		border: 1.5px solid #75a05f;
		border-radius: 13px;
		background: #eaf6cc;
		color: #174b37;
		font-size: 1rem;
		font-weight: 900;
		cursor: pointer;
	}
	.switch-role-button:hover { background: #d7ee78; }
	.switch-role-button span { font-size: 1.35rem; line-height: 1; }
	.account-error { margin: -8px 0 24px; }

	.secondary-button,
	.delete-button {
		min-height: 50px;
		padding: 12px 22px;
		border-radius: 13px;
		font-size: 1rem;
		font-weight: 850;
		cursor: pointer;
	}
	.secondary-button { border: 1.5px solid #6a927d; background: #fff; color: #174b37; }
	.secondary-button:hover { background: #f1f7f3; }

	.danger-card { border-color: #efd0cb; }
	.danger-label { color: #a43c32; }
	.delete-button { border: 1.5px solid #b63f35; background: #fff5f3; color: #982f27; }
	.delete-button:hover { background: #b63f35; color: #fff; }
	.confirmation {
		margin-top: 26px;
		padding: 20px;
		border-radius: 16px;
		background: #fff1ee;
		color: #70251f;
	}
	.confirmation strong { font-size: 1.2rem; }
	.confirmation p { margin: 8px 0 18px; line-height: 1.5; }
	.confirmation-actions { display: flex; flex-wrap: wrap; gap: 12px; }
	.error-message {
		margin: 18px 0 0;
		padding: 14px 16px;
		border-radius: 12px;
		background: #fde8e4;
		color: #84291f;
		font-weight: 750;
	}

	@media (max-width: 620px) {
		.settings-page { width: min(100% - 24px, 920px); padding-top: 28px; }
		.details-list > div { grid-template-columns: 1fr; }
		.details-list small { grid-column: 1; }
		.switch-role-button { grid-column: 1; width: 100%; justify-content: center; }
		.secondary-button,
		.delete-button { width: 100%; }
	}
</style>
