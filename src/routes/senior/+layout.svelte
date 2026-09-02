<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { supabase } from '$lib/supabase';
	import { startSampleCall } from '$lib/senior/sampleCall';
	import './shell.css';

	let { children } = $props();

	const links = [
		{ href: '/senior/dashboard', label: 'Home', hint: 'Your day at a glance', icon: '⌂' },
		{ href: '/senior/medications', label: 'Medicines', hint: 'Your medication plan', icon: '✚' },
		{ href: '/senior/reminder', label: 'Reminders', hint: 'Your routine & plans', icon: '◷' },
		{ href: '/senior/Vcare', label: 'Vcare Calls', hint: 'Calls & summaries', icon: '☎' },
		{ href: '/senior/care-circle', label: 'Care Circle', hint: 'Your trusted people', icon: '♡' }
	];

	let senior = $state({
		firstName: 'User',
		fullName: '',
		phone: '',
		email: ''
	});
	let userId = $state('');
	/** @type {{ id?: string | number, name?: string, dosage?: string, scheduled_time?: string, taken?: boolean } | null} */
	let pendingMedicine = $state(null);
	let currentDate = $state('');
	let currentTime = $state('');
	let timezone = $state('');
	let timezoneLabel = $state('');
	let profileOpen = $state(false);
	let helpOpen = $state(false);
	let sampleCallMessage = $state('');
	let isCalling = $state(false);

	function isActive(/** @type {string} */ href) {
		const path = page.url.pathname;
		if (href === '/senior/dashboard') {
			return path === '/senior/dashboard' || path === '/senior';
		}
		return path === href || path.startsWith(`${href}/`);
	}

	onMount(() => {
		/** @type {ReturnType<typeof setInterval> | undefined} */
		let clock;

		async function initialize() {
			timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
			timezoneLabel = new Intl.DateTimeFormat('en-IN', { timeZoneName: 'short' })
				.formatToParts(new Date())
				.find((part) => part.type === 'timeZoneName')?.value || timezone;

			const {
				data: { user }
			} = await supabase.auth.getUser();

			if (!user) {
				goto('/auth?role=senior');
				return;
			}

			userId = user.id;
			senior.email = user.email || '';

			const { data: profile } = await supabase
				.from('profiles')
				.select('full_name, phone')
				.eq('id', user.id)
				.single();

			senior.fullName =
				profile?.full_name ||
				user.user_metadata?.full_name ||
				user.user_metadata?.name ||
				'User';
			senior.firstName = senior.fullName.split(' ')[0];
			senior.phone = profile?.phone || '';

			const { data: medData } = await supabase
				.from('medications')
				.select('id, name, dosage, scheduled_time, taken')
				.eq('senior_id', user.id)
				.order('scheduled_time', { ascending: true });

			pendingMedicine = (medData || []).find((m) => !m.taken) || null;

			updateClock();
			clock = setInterval(updateClock, 30000);
		}

		initialize();

		return () => {
			if (clock) clearInterval(clock);
		};
	});

	function updateClock() {
		const now = new Date();

		currentDate = new Intl.DateTimeFormat('en-IN', {
			weekday: 'long',
			day: 'numeric',
			month: 'long',
			year: 'numeric',
			timeZone: timezone
		}).format(now);

		currentTime = new Intl.DateTimeFormat('en-IN', {
			hour: 'numeric',
			minute: '2-digit',
			hour12: true,
			timeZone: timezone
		}).format(now);
	}

	async function takeSampleCall() {
		isCalling = true;
		sampleCallMessage = 'Starting your Vcare check-in call...';

		try {
			await startSampleCall({
				phone: senior.phone,
				firstName: senior.firstName,
				userId,
				pendingMedicine
			});
			sampleCallMessage = 'Vcare is calling you now.';
		} catch (error) {
			sampleCallMessage = error instanceof Error
				? error.message
				: 'Could not start the call. Please try again.';
		} finally {
			isCalling = false;
		}
	}

	async function logout() {
		await supabase.auth.signOut();
		goto('/');
	}
</script>

<div class="senior-shell">
	<aside class="senior-sidebar">
		<a class="senior-brand" href="/senior/dashboard">
			<span class="senior-logo">♥</span>
			<span>
				<strong>Vcare.life</strong>
				<small>A Voice That Cares</small>
			</span>
		</a>

		<nav class="senior-nav" aria-label="Senior navigation">
			{#each links as link}
				<a href={link.href} class:active={isActive(link.href)} aria-current={isActive(link.href) ? 'page' : undefined}>
					<span aria-hidden="true">{link.icon}</span>
					<div>
						<strong>{link.label}</strong>
						<small>{link.hint}</small>
					</div>
				</a>
			{/each}
		</nav>

		<div class="sample-card">
			<div class="sample-card-header">
				<div class="sample-call-icon" aria-hidden="true">☎</div>
				<div class="sample-copy">
					<p>TRY VCARE</p>
					<h3>Sample call</h3>
				</div>
			</div>
			<p class="sample-description">Hear how Vcare checks in and supports your day.</p>

			<button type="button" class="sample-button" onclick={takeSampleCall} disabled={isCalling}>
				{isCalling ? 'Calling...' : 'Start sample call'}
			</button>

			{#if sampleCallMessage}
				<p class="sample-message" aria-live="polite">{sampleCallMessage}</p>
			{/if}
		</div>

		<div class="sidebar-footer">
			<span>♡</span>
			<p>Small conversations.<br />A little more care.</p>
		</div>

		<a class="sidebar-settings" href="/senior/settings" aria-current={isActive('/senior/settings') ? 'page' : undefined}>
			<span aria-hidden="true">⚙</span>
			Settings
		</a>
	</aside>

	<div class="senior-main">
		<a class="skip-link" href="#senior-content">Skip to main content</a>
		<header class="senior-topbar">
			<a class="mobile-logo" href="/senior/dashboard">
				<span class="senior-logo" style="width:37px;height:37px;font-size:17px">♥</span>
				<strong>Vcare.life</strong>
			</a>

			<div class="top-date">
				<div>
					<small>TODAY</small>
					<strong>{currentDate}</strong>
					<span class="live-time">{currentTime} · {timezoneLabel}</span>
				</div>
			</div>

			<div class="top-actions">
				<button type="button" class="help-button" onclick={() => (helpOpen = !helpOpen)} aria-expanded={helpOpen} aria-controls="senior-help-dialog">
					?
					<span>Help</span>
				</button>

				<div class="profile-container">
					<button type="button" class="profile-button" onclick={() => (profileOpen = !profileOpen)} aria-expanded={profileOpen} aria-haspopup="menu">
						<div class="avatar">
							{senior.firstName.charAt(0).toUpperCase()}
						</div>
						<div class="profile-name">
							<strong>{senior.firstName}</strong>
							<span>My profile</span>
						</div>
					</button>

					{#if profileOpen}
						<div class="profile-menu" role="menu">
							<div class="profile-menu-header">
								<strong>{senior.fullName || senior.firstName}</strong>
								<small>{senior.phone || senior.email}</small>
							</div>
							<a href="/senior/medications" class="menu-item" onclick={() => (profileOpen = false)}>
								My Medicines
							</a>
							<a href="/senior/reminder" class="menu-item" onclick={() => (profileOpen = false)}>
								My Reminders
							</a>
							<a
								href="/senior/care-circle"
								class="menu-item"
								onclick={() => (profileOpen = false)}
							>
								Care Circle
							</a>
							<a href="/senior/settings" class="menu-item" onclick={() => (profileOpen = false)}>
								Settings
							</a>
							<button type="button" class="menu-item logout" onclick={logout}>Sign Out</button>
						</div>
					{/if}
				</div>
			</div>
		</header>

		<div class="senior-page" id="senior-content">
			{@render children()}
		</div>
	</div>

	<nav class="mobile-nav" aria-label="Senior mobile navigation">
		{#each links as link}
			<a href={link.href} class:active={isActive(link.href)} aria-current={isActive(link.href) ? 'page' : undefined}>
				<span aria-hidden="true">{link.icon}</span>
				{link.label}
			</a>
		{/each}
	</nav>
</div>

{#if helpOpen}
	<div class="help-overlay">
		<div class="help-card" id="senior-help-dialog" role="dialog" aria-modal="true" aria-labelledby="senior-help-title">
			<header class="help-header">
				<div>
					<p class="help-eyebrow">ABOUT VCARE</p>
					<h2 id="senior-help-title">How Vcare Cares for You</h2>
				</div>
				<button type="button" class="modal-close" onclick={() => (helpOpen = false)} aria-label="Close help">×</button>
			</header>

			<div class="help-body">
				<div class="help-item">
					<div class="help-icon">☎</div>
					<div>
						<strong>Daily AI Phone Calls</strong>
						<p>Vcare calls your phone automatically to ask about your medicines, health, and daily mood.</p>
					</div>
				</div>
				<div class="help-item">
					<div class="help-icon">💊</div>
					<div>
						<strong>Medicine Reminders</strong>
						<p>You and your caregiver can schedule prescriptions. When Vcare calls, you can confirm you took them.</p>
					</div>
				</div>
				<div class="help-item">
					<div class="help-icon">♡</div>
					<div>
						<strong>Care Circle & Emergency Alerts</strong>
						<p>If you miss medications or feel unwell, Vcare can alert your trusted family or caregiver.</p>
					</div>
				</div>
			</div>

			<footer>
				<button type="button" class="btn-help-close" onclick={() => (helpOpen = false)}>Got it, thank you!</button>
			</footer>
		</div>
	</div>
{/if}
