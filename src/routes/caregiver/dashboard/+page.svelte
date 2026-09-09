<script>
	import { onDestroy, onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import {
		careInviteErrorMessage,
		chooseCareRecipient,
		normalizeCareInviteCode,
		rememberCareRecipient
	} from '$lib/careConnections';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import Badge from '$lib/components/Badge.svelte';
	import '../theme.css';

	/* =====================================================
	   USER / SENIOR
	===================================================== */

	let caregiverName = $state('Caregiver');
	let caregiverInitial = $state('C');
	/** @type {any[]} */
	let linkedSeniors = $state([]);
	let inviteCode = $state('');
	let connectionRelationship = $state('');
	let connecting = $state(false);
	/** @type {{ type: 'success' | 'error', text: string } | null} */
	let connectionMessage = $state(null);

	let senior = $state({
		name: 'Loading...',
		firstName: 'Senior',
		initials: 'S',
		phone: '',
		status: 'Loading...',
		lastCheckIn: '—',
		mood: 'Unknown',
		moodEmoji: '😊'
	});

	/* =====================================================
	   TIME
	===================================================== */

	let currentTime = $state('');
	let currentDate = $state('');
	let greeting = $state('Hello');

	function updateClock() {
		const now = new Date();

		currentTime = now.toLocaleTimeString('en-IN', {
			hour: '2-digit',
			minute: '2-digit',
			hour12: true
		});

		currentDate = now.toLocaleDateString('en-IN', {
			weekday: 'long',
			day: 'numeric',
			month: 'long'
		});

		const hour = now.getHours();

		if (hour < 12) {
			greeting = 'Good morning';
		} else if (hour < 17) {
			greeting = 'Good afternoon';
		} else {
			greeting = 'Good evening';
		}
	}

	/* =====================================================
	   MEDICATIONS
	===================================================== */

	/** @type {any[]} */
	let medications = $state([]);

	/* =====================================================
	   ALERTS
	===================================================== */

	/** @type {any[]} */
	let alerts = $state([]);

	/* =====================================================
	   RECENT CALL
	===================================================== */

	let recentCall = $state({
		date: 'Today',
		time: '—',
		duration: '—',
		status: 'Loading...',
		summary: 'Fetching latest call...'
	});

	let seniorId = $state('');
	/** @type {ReturnType<typeof setInterval> | undefined} */
	let clock;

	/* =====================================================
	   AUTH + PROFILE
	===================================================== */

	onMount(async () => {
		updateClock();

		clock = setInterval(updateClock, 30000);

		const {
			data: { session }
		} = await supabase.auth.getSession();

		const {
			data: { user }
		} = await supabase.auth.getUser();

		if (user) {
			const { data: profile } = await supabase
				.from('profiles')
				.select('*')
				.eq('id', user.id)
				.maybeSingle();

			if (profile?.full_name) {
				caregiverName = profile.full_name;
				caregiverInitial = profile.full_name.charAt(0).toUpperCase();
			}

			let seniors = [];
			const token = session?.access_token;

			// 1. Fast Path: Direct Supabase query (instant ~50ms load)
			try {
				const { data: links } = await supabase
					.from('caregiver_links')
					.select('senior_id')
					.eq('caregiver_id', user.id);

				if (links && links.length > 0) {
					const seniorIds = links.map(l => l.senior_id);
					const { data: profiles } = await supabase
						.from('profiles')
						.select('*')
						.in('id', seniorIds);

					if (profiles && profiles.length > 0) {
						seniors = profiles;
					}
				}

			} catch (err) {
				console.error('Supabase direct senior query error:', err);
			}

			if (seniors && seniors.length > 0) {
				linkedSeniors = seniors;
				const firstSenior = chooseCareRecipient(seniors);
				senior.name = firstSenior.full_name || 'Senior';
				senior.firstName = (firstSenior.full_name || 'Senior').split(' ')[0];
				senior.initials = (firstSenior.full_name || 'S')
					.split(' ')
					.map(/** @param {string} n */ (n) => n.charAt(0))
					.join('')
					.toUpperCase();
				senior.phone = firstSenior.phone || '';
				senior.status = 'Connected';
				senior.lastCheckIn = 'No calls yet';
				senior.mood = 'Happy';
				senior.moodEmoji = '😊';
				seniorId = firstSenior.id;

				// Instant direct Supabase load for medications
				try {
					const { data: sbMeds } = await supabase
						.from('medications')
						.select('*')
						.eq('senior_id', firstSenior.id)
						.order('scheduled_time', { ascending: true });

					if (sbMeds) {
						medications = sbMeds.map(m => ({
							id: m.id,
							name: m.name,
							dosage: m.dosage,
							time: m.scheduled_time,
							status: m.taken ? 'taken' : 'pending'
						}));

						const pendingMeds = medications.filter(m => m.status === 'pending');
						alerts = pendingMeds.map((m, idx) => ({
							id: idx + 1,
							title: `${m.name} is still pending`,
							message: `Scheduled for ${m.time}. Vcare will remind ${senior.firstName}.`
						}));
					}
				} catch (e) {
					console.error('Failed to load medications from Supabase:', e);
				}

				// Instant direct Supabase load for call logs
				try {
					const { data: sbCalls } = await supabase
						.from('call_logs')
						.select('*')
						.eq('senior_id', firstSenior.id)
						.order('created_at', { ascending: false });

					if (sbCalls && sbCalls.length > 0) {
						const latestCall = sbCalls[0];
						recentCall = {
							date: new Date(latestCall.created_at).toLocaleDateString('en-IN'),
							time: new Date(latestCall.created_at).toLocaleTimeString('en-IN', {
								hour: '2-digit',
								minute: '2-digit'
							}),
							duration: latestCall.duration ? `${latestCall.duration}s` : '35s',
							status: latestCall.status || 'completed',
							summary: latestCall.transcript
								? (latestCall.transcript.length > 120 ? latestCall.transcript.substring(0, 120) + '...' : latestCall.transcript)
								: `${senior.firstName} was called for check-in`
						};
						senior.lastCheckIn = `${recentCall.date} at ${recentCall.time}`;
						if (latestCall.distress_detected) {
							senior.mood = 'Needs Attention';
							senior.moodEmoji = '⚠';
						}
					} else {
						recentCall = {
							date: 'Today',
							time: '—',
							duration: '—',
							status: 'Scheduled',
							summary: `Vcare will call ${senior.firstName} based on their medication schedule.`
						};
					}
				} catch (e) {
					console.error('Failed to load calls from Supabase:', e);
				}

				// Non-blocking background sync from backend
				if (token && PUBLIC_BACKEND_URL) {
					const controller = new AbortController();
					const timeoutId = setTimeout(() => controller.abort(), 1500);

					fetch(`${PUBLIC_BACKEND_URL}/caregiver/${user.id}/seniors`, {
						headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
						signal: controller.signal
					}).then(res => res.ok ? res.json() : []).then(/** @param {any[]} backendSeniors */ (backendSeniors) => {
						clearTimeout(timeoutId);
						if (backendSeniors && backendSeniors.length > 0) {
							const bs = backendSeniors.find(person => person.id === seniorId) || backendSeniors[0];
							senior.name = bs.full_name || senior.name;
							senior.firstName = (bs.full_name || senior.name).split(' ')[0];
							senior.phone = bs.phone || senior.phone;
						}
					}).catch(() => {});
				}

				// Subscribe to real-time medication updates
				supabase
					.channel(`caregiver-meds-${firstSenior.id}`)
					.on(
						'postgres_changes',
						{
							event: '*',
							schema: 'public',
							table: 'medications',
							filter: `senior_id=eq.${firstSenior.id}`
						},
						(payload) => {
							if (payload.eventType === 'UPDATE') {
								const updated = payload.new;
								medications = medications.map(m =>
									m.id === updated.id
										? { ...m, status: updated.taken ? 'taken' : 'pending' }
										: m
								);
							} else if (payload.eventType === 'INSERT') {
								const newMed = payload.new;
								medications = [...medications, {
									id: newMed.id,
									name: newMed.name,
									dosage: newMed.dosage,
									time: newMed.scheduled_time,
									status: newMed.taken ? 'taken' : 'pending'
								}].sort((a, b) => a.time.localeCompare(b.time));
							}
							const pending = medications.filter(m => m.status === 'pending');
							alerts = pending.map((m, idx) => ({
								id: idx + 1,
								title: `${m.name} is still pending`,
								message: `Scheduled for ${m.time}. Vcare will remind ${senior.firstName}.`
							}));
						}
					)
					.subscribe();

			} else {
				senior.name = 'No Senior Linked';
				senior.firstName = 'Senior';
				senior.initials = '+';
				senior.status = 'Pending Setup';
				senior.lastCheckIn = '—';
				recentCall = {
					date: 'Today',
					time: '—',
					duration: '—',
					status: 'No senior linked',
					summary: 'Please complete onboarding to link a senior.'
				};
			}
		}

	});

	onDestroy(() => {
		if (clock) clearInterval(clock);
	});

	/* =====================================================
	   ACTIONS
	===================================================== */

	async function logout() {
		await supabase.auth.signOut();
		goto('/');
	}

	function openMedicines() {
		goto('/caregiver/medicines');
	}

	function openCalls() {
		goto('/caregiver/calls');
	}

	function openSenior() {
		goto('/caregiver/senior');
	}

	/** @param {Event & { currentTarget: HTMLSelectElement }} event */
	function switchSenior(event) {
		rememberCareRecipient(event.currentTarget.value);
		window.location.reload();
	}

	async function connectWithCode() {
		connectionMessage = null;
		const code = normalizeCareInviteCode(inviteCode);
		if (!/^VCARE-[A-Z0-9]{6}$/.test(code)) {
			connectionMessage = { type: 'error', text: 'Enter the complete code, for example VCARE-ABC123.' };
			return;
		}

		connecting = true;
		const { data, error } = await supabase.rpc('redeem_care_invite', {
			invite_code: code,
			relationship_to_senior: connectionRelationship.trim() || null
		});
		connecting = false;

		if (error || !data?.[0]?.senior_id) {
			connectionMessage = {
				type: 'error',
				text: careInviteErrorMessage(error, 'redeem')
			};
			return;
		}

		rememberCareRecipient(data[0].senior_id);
		connectionMessage = { type: 'success', text: `Connected to ${data[0].senior_name}.` };
		inviteCode = '';
		connectionRelationship = '';
		setTimeout(() => window.location.reload(), 700);
	}
</script>

<svelte:head>
	<title>Caregiver Dashboard — Vcare.life</title>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..500&family=Public+Sans:wght@300..700&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="app" data-caregiver-portal>

	<!-- =====================================================
	     SIDEBAR
	===================================================== -->

	<aside class="sidebar">

		<a href="/" class="brand">
			<div class="brand-heart">♥</div>
			<div>
				<strong>Vcare.life</strong>
				<span>A Voice That Cares</span>
			</div>
		</a>

		<div class="care-label">
			CAREGIVER SPACE
		</div>

		<nav>
			<a href="/caregiver/dashboard" class="nav-item active">
				<span class="nav-icon" aria-hidden="true">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
						<polyline points="9 22 9 12 15 12 15 22"/>
					</svg>
				</span>
				<span>Home</span>
			</a>

			<a href="/caregiver/medicines" class="nav-item">
				<span class="nav-icon" aria-hidden="true">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
					</svg>
				</span>
				<span>Health Routine</span>
			</a>

			<a href="/caregiver/calls" class="nav-item">
				<span class="nav-icon" aria-hidden="true">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
					</svg>
				</span>
				<span>Vcare Calls</span>
			</a>

			<a href="/caregiver/senior" class="nav-item">
				<span class="nav-icon" aria-hidden="true">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
					</svg>
				</span>
				<span>Senior Profile</span>
			</a>

			<a href="/caregiver/settings" class="nav-item">
				<span class="nav-icon">⚙</span>
				<span>Settings</span>
			</a>

		</nav>

		<div class="sidebar-bottom">
			<a href="/caregiver/senior" class="mini-senior">
				<div class="mini-avatar">
					{senior.initials}

				<div class="mini-avatar" aria-hidden="true">
					♡
				</div>
				<div class="mini-senior-info">
					<small>CARING FOR</small>
					<strong>{senior.name}</strong>
				</div>
			</a>

			<div class="profile">
				<div class="profile-avatar">
					{caregiverInitial}
				</div>
				<div class="profile-copy">
					<strong>{caregiverName}</strong>
					<span>Caregiver</span>
				</div>
				<button
					class="logout"
					onclick={logout}
					aria-label="Sign out"
					title="Sign out"
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
						<polyline points="16 17 21 12 16 7"/>
						<line x1="21" y1="12" x2="9" y2="12"/>
					</svg>
				</button>
			</div>
		</div>

	</aside>

	<!-- =====================================================
	     MAIN
	===================================================== -->

	<main class="main">

		<!-- TOP BAR -->
		<header class="topbar">
			<div>
				<p class="date">
					{currentDate}
				</p>
				<!-- DISPLAY SERIF ONLY HERE FOR GREETING -->
				<h1 class="greeting-serif">
					{greeting}, {caregiverName.split(' ')[0]}!
				</h1>
				<p class="intro">
					Here's how {senior.firstName} is doing today.
				</p>
			</div>

			<!-- CLARIFIED LIVE MONITORING INDICATOR -->
			<div class="live-status-pill" title="System monitoring active">
				<span class="live-pulse-dot" aria-hidden="true"></span>
				<div class="live-status-text">
					<span class="live-status-label">ACTIVE MONITORING</span>
					<strong class="live-status-time">{currentTime}</strong>
				</div>
			</div>
		</header>

		<!-- =================================================
		     SENIOR STATUS CARD
		================================================= -->
		<section class="senior-card">
			<div class="senior-main">
				<div class="senior-avatar">
					{senior.initials}

				<div class="senior-avatar" aria-hidden="true">
					♡
				</div>

				<div class="senior-info">
					<p class="eyebrow">YOUR SENIOR</p>

					<p class="eyebrow">
						CARE RECIPIENT
					</p>

					<div class="senior-name-row">
						<!-- Sans-serif headline for data consistency -->
						<h2>{senior.name}</h2>
						<Badge
							variant={senior.status === 'Connected' ? 'success' : senior.status === 'Loading...' ? 'neutral' : 'warning'}
							dot={true}
						>
							{senior.status}
						</Badge>
					</div>

					<p class="checkin">
						Last Vcare check-in:
						<strong>{senior.lastCheckIn}</strong>
					</p>

					<a
						href="/caregiver/senior"
						class="senior-details-link"
						aria-label={`Review or correct ${senior.name}'s care details`}
					>
						Review or correct details →
					</a>

				</div>
			</div>

			<div class="senior-actions">
				<div class="mood-small">
					<span class="mood-emoji">{senior.moodEmoji}</span>
					<div>
						<small>TODAY'S MOOD</small>
						<strong>{senior.mood}</strong>
					</div>
				</div>

				<!-- Single-line legible button label -->
				<a
					href={`tel:${senior.phone}`}
					class="call-action-button"
					aria-label={`Direct phone call to ${senior.firstName}`}
				>
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
					</svg>
					<span>Call {senior.firstName}</span>
				</a>
			</div>
		</section>

		<section class="connection-panel" aria-labelledby="connection-title">
			<div>
				<p class="eyebrow">CARE CONNECTIONS</p>
				<h2 id="connection-title">Connect with an invitation code</h2>
				<p>A senior generates this private, one-time code from their Care Circle.</p>
			</div>

			{#if linkedSeniors.length > 1}
				<label class="senior-selector">
					<span>Currently viewing</span>
					<select value={seniorId} onchange={switchSenior}>
						{#each linkedSeniors as person}
							<option value={person.id}>{person.full_name || 'Senior'}</option>
						{/each}
					</select>
				</label>
			{/if}

			<form class="connection-form" onsubmit={(event) => { event.preventDefault(); connectWithCode(); }}>
				<label for="connection-relationship">Your relationship to the senior</label>
				<input id="connection-relationship" bind:value={connectionRelationship} placeholder="e.g. Daughter, neighbour" autocomplete="off" />
				<label for="invite-code">Invitation code</label>
				<div>
					<input
						id="invite-code"
						bind:value={inviteCode}
						placeholder="VCARE-ABC123"
						autocomplete="one-time-code"
						spellcheck="false"
						maxlength="12"
						required
					/>
					<button type="submit" disabled={connecting}>{connecting ? 'Connecting…' : 'Connect'}</button>
				</div>
			</form>

			{#if connectionMessage}
				<p class:connection-success={connectionMessage.type === 'success'} class:connection-error={connectionMessage.type === 'error'} role="status">
					{connectionMessage.text}
				</p>
			{/if}
		</section>


		<!-- =================================================
		     MAIN GRID
		================================================= -->
		<section class="dashboard-grid">

			<!-- =================================================
			     HEALTH & DAILY ROUTINE (MEDICATIONS, WALKS, YOGA, DIET)
			================================================= -->
			<article class="panel medication-panel">
				<div class="panel-header">
					<div>
						<p class="eyebrow">TODAY</p>
						<h2>{senior.firstName}'s Daily Routine</h2>
						<span class="panel-subtitle">Today's medicines, walks, yoga, and wellness habits.</span>
					</div>
					<div class="panel-icon medicine-icon" aria-hidden="true">
						🌿
					</div>
				</div>

				<div class="medicine-list">
					{#if medications.length === 0}
						<div class="empty-state">
							<p>No routine items scheduled for today.</p>
						</div>
					{:else}
						{#each medications as item}
							<div class="medicine-row">
								<div
									class="medicine-check"
									class:taken={item.status === 'taken'}
									aria-hidden="true"
								>
									{item.status === 'taken' ? '✓' : '○'}
								</div>

								<div class="medicine-info">
									<strong>{item.name}</strong>
									<span class="medicine-meta">{item.dosage ? `${item.dosage} · ` : ''}{item.time}</span>
								</div>

								<Badge variant={item.status === 'taken' ? 'success' : 'warning'}>
									{item.status === 'taken' ? 'Completed' : 'Pending'}
								</Badge>
							</div>
						{/each}
					{/if}
				</div>

				<div class="panel-actions">
					<button class="add-button" onclick={openMedicines}>
						<span>＋</span> Add routine item
					</button>
					<button class="text-button" onclick={openMedicines}>
						View all routines <span>→</span>
					</button>
				</div>
			</article>

			<!-- =================================================
			     ESCALATED ALERTS / NEEDS ATTENTION
			================================================= -->
			<article class="panel alert-panel" class:has-alerts={alerts.length > 0}>
				<div class="panel-header compact">
					<div>
						<p class="eyebrow" class:orange={alerts.length > 0}>
							{alerts.length > 0 ? 'ACTION REQUIRED' : 'STATUS'}
						</p>
						<h2>Needs Attention</h2>
					</div>
					<div class="panel-icon alert-icon" class:alert-active={alerts.length > 0} aria-hidden="true">
						{alerts.length > 0 ? '⚠️' : '🛡️'}
					</div>
				</div>

				{#if alerts.length > 0}
					<div class="alerts">
						{#each alerts as alert}
							<div class="alert-item">
								<div class="alert-symbol" aria-hidden="true">!</div>
								<div class="alert-body">
									<strong>{alert.title}</strong>
									<p>{alert.message}</p>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="all-good">
						<div class="all-good-icon" aria-hidden="true">✓</div>
						<div class="all-good-copy">
							<strong>Everything looks good.</strong>
							<p>Nothing needs your immediate attention right now.</p>
						</div>
					</div>
				{/if}

				<div class="care-note">
					<span aria-hidden="true">♡</span>
					<p>We'll keep this space quiet unless something actually needs you.</p>
				</div>
			</article>

			<!-- =================================================
			     RECENT VCARE CALL
			================================================= -->
			<article class="panel call-panel">
				<div class="panel-header">
					<div>
						<p class="eyebrow">RECENT CHECK-IN</p>
						<h2>Latest Vcare call</h2>
						<span class="panel-subtitle">A small window into how {senior.firstName} is doing.</span>
					</div>
					<div class="panel-icon call-icon" aria-hidden="true">
						☎
					</div>
				</div>

				<div class="call-summary">
					<div class="call-top">
						<div class="call-time-info">
							<strong>{recentCall.date} · {recentCall.time}</strong>
							<span class="call-duration">Duration: {recentCall.duration}</span>
						</div>
						<Badge variant="success" dot={true}>
							{recentCall.status}
						</Badge>
					</div>

					<div class="call-tags">
						<Badge variant="neutral">💊 Medicine confirmed</Badge>
						<Badge variant="neutral">🙂 Mood good</Badge>
					</div>

					<p class="summary-text">
						"{recentCall.summary}"
					</p>
				</div>

				<button class="wide-button" onclick={openCalls}>
					<span>View call history & transcripts</span>
					<span aria-hidden="true">→</span>
				</button>
			</article>

			<!-- =================================================
			     WELLBEING / MOOD
			================================================= -->
			<article class="panel mood-panel">
				<div class="panel-header">
					<div>
						<p class="eyebrow">WELLBEING</p>
						<h2>How {senior.firstName} has been feeling</h2>
					</div>
					<div class="panel-icon mood-icon" aria-hidden="true">
						🌱
					</div>
				</div>

				<div class="current-mood">
					<div class="big-emoji" aria-hidden="true">
						{senior.moodEmoji}
					</div>
					<div class="current-mood-text">
						<small>TODAY'S ASSESSMENT</small>
						<strong>{senior.mood}</strong>
						<span>From the latest automated voice check-in</span>
					</div>
				</div>

				<div class="mood-history">
					<div class="mood-row">
						<span>Yesterday</span>
						<Badge variant="neutral">🙂 Okay</Badge>
					</div>
					<div class="mood-row">
						<span>14 Aug</span>
						<Badge variant="success">😊 Good</Badge>
					</div>
					<div class="mood-row">
						<span>13 Aug</span>
						<Badge variant="success">😊 Good</Badge>
					</div>
				</div>

				<button class="text-button mood-link" onclick={openCalls}>
					View wellbeing history <span>→</span>
				</button>
			</article>

		</section>

		<!-- =================================================
		     BOTTOM BANNER — DIFFERENTIATED PURPOSE (VOICE CHECK-INS)
		================================================= -->
		<section class="contact-card">
			<div class="contact-card-content">
				<div class="contact-heart" aria-hidden="true">
					🎧
				</div>
				<div>
					<p class="eyebrow">VOICE CHECK-IN ARCHIVE</p>
					<h2>Review {senior.firstName}'s conversations</h2>
					<p>
						Listen to the AI call recordings and read full check-in transcripts anytime.
					</p>
				</div>
			</div>

			<div class="contact-actions">
				<button class="profile-button" onclick={openSenior}>
					Senior profile
				</button>
				<button class="listen-button" onclick={openCalls}>
					<span>Listen to calls</span>
					<span aria-hidden="true">→</span>
				</button>
			</div>
		</section>

		<p class="closing">
			♡ Vcare stays with them, so you can stay close without worrying every minute.
		</p>

	</main>

</div>

<style>
	button,
	a {
		font-family: inherit;
	}

	/* =====================================================
	   APP LAYOUT
	===================================================== */

	.app {
		min-height: 100vh;
		display: grid;
		grid-template-columns: 250px 1fr;
		background: #f8f6f0;
	}

	/* =====================================================
	   SIDEBAR
	===================================================== */

	.sidebar {
		position: sticky;
		top: 0;
		height: 100vh;
		padding: 26px 18px 20px;
		display: flex;
		flex-direction: column;
		background: linear-gradient(180deg, #093325 0%, #0d4633 100%);
		color: white;
		border-right: 1px solid rgba(255, 255, 255, 0.08);
		z-index: 20;
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 0 6px;
		text-decoration: none;
		color: white;
	}

	.brand-heart {
		width: 40px;
		height: 40px;
		display: grid;
		place-items: center;
		border-radius: 12px;
		background: white;
		color: #0b6845;
		font-size: 20px;
		flex-shrink: 0;
	}

	.brand > div:last-child {
		display: flex;
		flex-direction: column;
	}

	.brand strong {
		font-size: 18px;
		font-weight: 700;
		letter-spacing: -0.02em;
	}

	.brand span {
		margin-top: 1px;
		color: rgba(255, 255, 255, 0.65);
		font-size: 10px;
	}

	.care-label {
		margin: 28px 8px 12px;
		color: #dce765;
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.12em;
	}

	nav {
		display: grid;
		gap: 6px;
	}

	.nav-item {
		min-height: 44px;
		padding: 0 14px;
		display: flex;
		align-items: center;
		gap: 12px;
		border-radius: 12px;
		text-decoration: none;
		color: rgba(255, 255, 255, 0.72);
		font-size: 13px;
		font-weight: 600;
		transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
	}

	.nav-item:hover {
		color: white;
		background: rgba(255, 255, 255, 0.08);
		transform: translateX(2px);
	}

	.nav-item.active {
		color: #0d3827;
		background: #dce76a;
		font-weight: 700;
	}

	.nav-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.sidebar-bottom {
		margin-top: auto;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.mini-senior {
		padding: 10px 12px;
		display: flex;
		align-items: center;
		gap: 10px;
		border: 1px solid rgba(255, 255, 255, 0.12);
		border-radius: 13px;
		background: rgba(255, 255, 255, 0.06);
		text-decoration: none;
		color: inherit;
		transition: background 0.2s ease;
	}

	.mini-senior:hover {
		background: rgba(255, 255, 255, 0.12);
	}

	.mini-avatar {
		width: 32px;
		height: 32px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 9px;
		background: #dce76a;
		color: #143d2e;
		font-size: 12px;
		font-weight: 700;
	}

	.mini-senior-info {
		min-width: 0;
		display: flex;
		flex-direction: column;
	}

	.mini-senior small {
		color: rgba(255, 255, 255, 0.55);
		font-size: 9px;
		font-weight: 600;
		letter-spacing: 0.08em;
	}

	.mini-senior strong {
		margin-top: 1px;
		overflow: hidden;
		color: white;
		font-size: 12px;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.profile {
		padding-top: 12px;
		display: flex;
		align-items: center;
		gap: 10px;
		border-top: 1px solid rgba(255, 255, 255, 0.10);
	}

	.profile-avatar {
		width: 34px;
		height: 34px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 50%;
		background: #f3e6c8;
		color: #174631;
		font-size: 13px;
		font-weight: 700;
	}

	.profile-copy {
		min-width: 0;
		display: flex;
		flex: 1;
		flex-direction: column;
	}

	.profile-copy strong {
		overflow: hidden;
		font-size: 13px;
		color: white;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.profile-copy span {
		margin-top: 1px;
		color: rgba(255, 255, 255, 0.55);
		font-size: 11px;
	}

	.logout {
		border: 0;
		background: transparent;
		color: rgba(255, 255, 255, 0.65);
		cursor: pointer;
		padding: 6px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 8px;
		transition: color 0.15s ease, background 0.15s ease;
	}

	.logout:hover {
		color: white;
		background: rgba(255, 255, 255, 0.12);
	}

	/* =====================================================
	   MAIN CONTENT
	===================================================== */

	.main {
		width: 100%;
		max-width: 1380px;
		margin: 0 auto;
		padding: 32px clamp(24px, 3.5vw, 56px) 48px;
	}

	/* =====================================================
	   TOP BAR
	===================================================== */

	.topbar {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 24px;
		margin-bottom: 26px;
	}

	.date {
		margin: 0 0 6px;
		color: #4b6357;
		font-size: 12px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	/* FRAUNCES DISPLAY SERIF ONLY HERE */
	.greeting-serif {
		margin: 0;
		color: #0e3b2c;
		font-family: "Fraunces", Georgia, serif;
		font-size: clamp(30px, 3.2vw, 42px);
		line-height: 1.05;
		font-weight: 500;
		letter-spacing: -0.025em;
	}

	.intro {
		margin: 8px 0 0;
		color: #475569;
		font-size: 14px;
	}

	/* CLARIFIED LIVE INDICATOR */
	.live-status-pill {
		padding: 8px 14px;
		display: flex;
		align-items: center;
		gap: 10px;
		border: 1px solid #d4dec9;
		border-radius: 12px;
		background: #ffffff;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
	}

	.live-pulse-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #16a34a;
		box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
		animation: livePulse 2s infinite ease-in-out;
		flex-shrink: 0;
	}

	@keyframes livePulse {
		0%, 100% {
			transform: scale(1);
			box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
		}
		50% {
			transform: scale(1.15);
			box-shadow: 0 0 0 6px rgba(22, 163, 74, 0.08);
		}
	}

	.live-status-text {
		display: flex;
		flex-direction: column;
	}

	.live-status-label {
		color: #166534;
		font-size: 9px;
		font-weight: 700;
		letter-spacing: 0.08em;
	}

	.live-status-time {
		margin-top: 1px;
		color: #1e293b;
		font-size: 13px;
		font-weight: 600;
	}

	/* =====================================================
	   SENIOR STATUS CARD
	===================================================== */

	.senior-card {
		margin-bottom: 22px;
		padding: 20px 24px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		border: 1px solid #e0e7df;
		border-radius: 18px;
		background: #ffffff;
		box-shadow: 0 2px 12px rgba(15, 60, 40, 0.05);
	}

	.senior-main {
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.senior-avatar {
		width: 58px;
		height: 58px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 16px;
		background: linear-gradient(135deg, #10593a 0%, #1a7a51 100%);
		color: white;
		font-size: 20px;
		font-weight: 700;
		box-shadow: 0 4px 12px rgba(16, 89, 58, 0.2);
	}

	.senior-info {
		display: flex;
		flex-direction: column;
	}

	.eyebrow {
		margin: 0 0 4px;
		color: #2b704c;
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.12em;
	}

	.eyebrow.orange {
		color: #b45309;
	}

	.senior-name-row {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 10px;
	}

	/* Sans-serif for all card data */
	.senior-name-row h2 {
		margin: 0;
		color: #0f382a;
		font-size: 22px;
		font-weight: 700;
		letter-spacing: -0.01em;
	}

	.checkin {
		margin: 6px 0 0;
		color: #4b5563;
		font-size: 13px;
	}

	.checkin strong {
		color: #1e293b;
		font-weight: 600;
	}

	.senior-actions {
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.mood-small {
		padding-right: 16px;
		display: flex;
		align-items: center;
		gap: 10px;
		border-right: 1px solid #e2e8e0;
	}

	.mood-emoji {
		font-size: 26px;
	}

	.mood-small div {
		display: flex;
		flex-direction: column;
	}

	.mood-small small {
		color: #64748b;
		font-size: 10px;
		font-weight: 700;
		letter-spacing: 0.06em;
	}

	.mood-small strong {
		color: #1e293b;
		font-size: 13px;
		font-weight: 600;
	}

	/* SINGLE LINE LEGIBLE CALL BUTTON */
	.call-action-button {
		min-height: 44px;
		padding: 0 18px;
		display: inline-flex;
		align-items: center;
		gap: 8px;
		border-radius: 12px;
		background: #116240;
		color: white;
		text-decoration: none;
		font-size: 13px;
		font-weight: 600;
		box-shadow: 0 4px 12px rgba(17, 98, 64, 0.2);
		transition: background 0.18s ease, transform 0.18s ease;
	}

	.call-action-button:hover {
		background: #0d4e33;
		transform: translateY(-1px);
	}

	/* =====================================================
	   GRID & PANELS
	===================================================== */

	.dashboard-grid {
		display: grid;
		grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.65fr);
		gap: 20px;
	}

	.panel {
		padding: 22px;
		border: 1px solid #e2e8e0;
		border-radius: 18px;
		background: #ffffff;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
	}

	.panel-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
		margin-bottom: 18px;
	}

	.panel-header.compact {
		margin-bottom: 14px;
	}

	.panel-header h2 {
		margin: 0;
		color: #0f382a;
		font-size: 18px;
		font-weight: 700;
		line-height: 1.25;
	}

	.panel-subtitle {
		display: block;
		margin-top: 4px;
		color: #4b5563;
		font-size: 13px;
	}

	.panel-icon {
		width: 38px;
		height: 38px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 11px;
		font-size: 16px;
	}

	.medicine-icon {
		background: #e8f7ee;
		color: #15803d;
	}

	.call-icon {
		background: #f0fdf4;
		color: #166534;
	}

	.alert-icon {
		background: #fef3c7;
		color: #b45309;
	}

	.alert-icon.alert-active {
		background: #fee2e2;
		color: #b91c1c;
	}

	.mood-icon {
		background: #ecfdf5;
		color: #047857;
	}

	/* =====================================================
	   MEDICATIONS LIST
	===================================================== */

	.medicine-list {
		display: grid;
		gap: 8px;
	}

	.empty-state {
		padding: 20px;
		text-align: center;
		color: #64748b;
		font-size: 13px;
		background: #f8faf9;
		border-radius: 12px;
	}

	.medicine-row {
		min-height: 56px;
		padding: 10px 14px;
		display: flex;
		align-items: center;
		gap: 12px;
		border: 1px solid #e9eee8;
		border-radius: 12px;
		background: #fbfdfb;
		transition: border-color 0.15s ease;
	}

	.medicine-row:hover {
		border-color: #cbdad0;
	}

	.medicine-check {
		width: 30px;
		height: 30px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 9px;
		background: #f1f5f2;
		color: #64748b;
		font-size: 14px;
		font-weight: 700;
	}

	.medicine-check.taken {
		background: #dcfce7;
		color: #15803d;
	}

	.medicine-info {
		min-width: 0;
		display: flex;
		flex: 1;
		flex-direction: column;
	}

	.medicine-info strong {
		color: #1e293b;
		font-size: 14px;
		font-weight: 600;
	}

	.medicine-meta {
		margin-top: 2px;
		color: #475569;
		font-size: 12px;
	}

	.panel-actions {
		margin-top: 18px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
	}

	.add-button {
		min-height: 38px;
		padding: 0 16px;
		border: 0;
		border-radius: 10px;
		background: #116240;
		color: white;
		cursor: pointer;
		font-size: 13px;
		font-weight: 600;
		transition: background 0.15s ease;
	}

	.add-button:hover {
		background: #0d4e33;
	}

	.add-button span {
		margin-right: 4px;
		font-size: 14px;
	}

	.text-button {
		padding: 6px 10px;
		border: 0;
		background: transparent;
		color: #166534;
		cursor: pointer;
		font-size: 13px;
		font-weight: 600;
		border-radius: 8px;
		transition: background 0.15s ease;
	}

	.text-button:hover {
		background: #f0fdf4;
	}

	/* =====================================================
	   ESCALATED ALERT PANEL
	===================================================== */

	.alert-panel.has-alerts {
		border: 1.5px solid #fcd34d;
		border-left: 4px solid #f59e0b;
		background: #fffdf9;
		box-shadow: 0 4px 16px rgba(245, 158, 11, 0.08);
	}

	.alerts {
		display: grid;
		gap: 10px;
	}

	.alert-item {
		padding: 12px 14px;
		display: flex;
		align-items: flex-start;
		gap: 12px;
		border: 1px solid #fde68a;
		border-radius: 12px;
		background: #fef3c7;
	}

	.alert-symbol {
		width: 24px;
		height: 24px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 50%;
		background: #d97706;
		color: white;
		font-size: 13px;
		font-weight: 700;
	}

	.alert-body strong {
		color: #78350f;
		font-size: 13px;
		font-weight: 600;
	}

	.alert-body p {
		margin: 3px 0 0;
		color: #92400e;
		font-size: 12px;
		line-height: 1.45;
	}

	.all-good {
		padding: 14px;
		display: flex;
		gap: 12px;
		align-items: center;
		border-radius: 12px;
		background: #f0fdf4;
		border: 1px solid #dcfce7;
	}

	.all-good-icon {
		width: 28px;
		height: 28px;
		display: grid;
		place-items: center;
		border-radius: 50%;
		background: #16a34a;
		color: white;
		font-size: 14px;
		font-weight: 700;
		flex-shrink: 0;
	}

	.all-good-copy strong {
		color: #14532d;
		font-size: 13px;
		font-weight: 600;
	}

	.all-good-copy p {
		margin: 2px 0 0;
		color: #166534;
		font-size: 12px;
	}

	.care-note {
		margin-top: 14px;
		padding-top: 12px;
		display: flex;
		gap: 8px;
		border-top: 1px dashed #e2e8e0;
	}

	.care-note span {
		color: #16a34a;
		font-size: 14px;
	}

	.care-note p {
		margin: 0;
		color: #4b5563;
		font-size: 12px;
		line-height: 1.45;
	}

	/* =====================================================
	   CALL SUMMARY
	===================================================== */

	.call-summary {
		padding: 16px;
		border: 1px solid #e2e8df;
		border-radius: 14px;
		background: #f9fbf9;
	}

	.call-top {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 10px;
	}

	.call-time-info {
		display: flex;
		flex-direction: column;
	}

	.call-time-info strong {
		color: #1e293b;
		font-size: 14px;
		font-weight: 600;
	}

	.call-duration {
		margin-top: 2px;
		color: #4b5563;
		font-size: 12px;
	}

	.call-tags {
		margin-top: 12px;
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
	}

	.summary-text {
		margin: 12px 0 0;
		color: #334155;
		font-size: 13px;
		line-height: 1.55;
		font-style: italic;
	}

	.wide-button {
		width: 100%;
		margin-top: 14px;
		padding: 10px 14px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		border: 1px solid #d1dcd5;
		border-radius: 11px;
		background: #ffffff;
		color: #166534;
		cursor: pointer;
		font-size: 13px;
		font-weight: 600;
		transition: background 0.15s ease, border-color 0.15s ease;
	}

	.wide-button:hover {
		background: #f0fdf4;
		border-color: #bbf7d0;
	}

	/* =====================================================
	   WELLBEING / MOOD
	===================================================== */

	.current-mood {
		margin-top: 14px;
		padding: 14px 16px;
		display: flex;
		align-items: center;
		gap: 14px;
		border-radius: 14px;
		background: #f0fdf4;
		border: 1px solid #dcfce7;
	}

	.big-emoji {
		width: 44px;
		height: 44px;
		display: grid;
		place-items: center;
		border-radius: 12px;
		background: #ffffff;
		font-size: 24px;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
		flex-shrink: 0;
	}

	.current-mood-text {
		display: flex;
		flex-direction: column;
	}

	.current-mood-text small {
		color: #166534;
		font-size: 10px;
		font-weight: 700;
		letter-spacing: 0.08em;
	}

	.current-mood-text strong {
		color: #0f382a;
		font-size: 16px;
		font-weight: 700;
	}

	.current-mood-text span {
		margin-top: 2px;
		color: #4b5563;
		font-size: 12px;
	}

	.mood-history {
		margin-top: 14px;
		display: grid;
		gap: 8px;
	}

	.mood-row {
		padding: 8px 4px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		border-bottom: 1px dashed #e2e8e0;
	}

	.mood-row span {
		color: #4b5563;
		font-size: 13px;
		font-weight: 500;
	}

	.mood-link {
		margin-top: 12px;
		display: inline-block;
	}

	/* =====================================================
	   BOTTOM BANNER — DIFFERENTIATED CHECK-IN CALLS
	===================================================== */

	.contact-card {
		margin-top: 22px;
		padding: 22px 24px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		border-radius: 18px;
		background: linear-gradient(125deg, #093828 0%, #0f543c 100%);
		color: white;
		box-shadow: 0 4px 16px rgba(9, 56, 40, 0.15);
	}

	.contact-card-content {
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.contact-heart {
		width: 48px;
		height: 48px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 14px;
		background: #dce769;
		color: #143d2e;
		font-size: 22px;
	}

	.contact-card .eyebrow {
		color: #dce769;
	}

	.contact-card h2 {
		margin: 0;
		color: white;
		font-size: 18px;
		font-weight: 700;
	}

	.contact-card p:not(.eyebrow) {
		margin: 4px 0 0;
		color: rgba(255, 255, 255, 0.75);
		font-size: 13px;
	}

	.contact-actions {
		display: flex;
		align-items: center;
		gap: 10px;
		flex-shrink: 0;
	}

	.profile-button {
		min-height: 42px;
		padding: 0 16px;
		border: 1px solid rgba(255, 255, 255, 0.28);
		border-radius: 11px;
		background: rgba(255, 255, 255, 0.08);
		color: white;
		cursor: pointer;
		font-size: 13px;
		font-weight: 600;
		transition: background 0.15s ease;
	}

	.profile-button:hover {
		background: rgba(255, 255, 255, 0.16);
	}

	.listen-button {
		min-height: 42px;
		padding: 0 18px;
		display: inline-flex;
		align-items: center;
		gap: 8px;
		border: 0;
		border-radius: 11px;
		background: #dce769;
		color: #113b2c;
		cursor: pointer;
		font-size: 13px;
		font-weight: 700;
		transition: transform 0.18s ease, background 0.18s ease;
	}

	.listen-button:hover {
		background: #e6f07a;
		transform: translateY(-1px);
	}

	.closing {
		margin: 24px 0 0;
		text-align: center;
		color: #64748b;
		font-size: 12px;
	}

	/* =====================================================
	   RESPONSIVE LAYOUT
	===================================================== */

	@media (max-width: 1050px) {
		.app {
			grid-template-columns: 210px 1fr;
		}

		.dashboard-grid {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 768px) {
		.app {
			display: block;
		}

		.sidebar {
			position: relative;
			width: 100%;
			height: auto;
			padding: 16px;
		}

		.care-label,
		.mini-senior {
			display: none;
		}

		nav {
			margin-top: 14px;
			display: flex;
			overflow-x: auto;
			gap: 8px;
		}

		.nav-item {
			flex-shrink: 0;
		}

		.sidebar-bottom {
			margin-top: 14px;
		}

		.profile {
			padding-top: 10px;
		}

		.main {
			padding: 24px 16px 40px;
		}

		.topbar {
			align-items: flex-start;
			flex-direction: column;
		}

		.senior-card {
			align-items: flex-start;
			flex-direction: column;
		}

		.senior-actions {
			width: 100%;
			justify-content: space-between;
		}

		.contact-card {
			align-items: flex-start;
			flex-direction: column;
		}

		.contact-actions {
			width: 100%;
		}
	}

	@media (max-width: 480px) {
		.senior-actions {
			align-items: stretch;
			flex-direction: column;
		}

		.mood-small {
			padding: 0 0 10px;
			border-right: 0;
			border-bottom: 1px solid #e2e8e0;
		}

		.call-action-button {
			justify-content: center;
		}

		.panel-actions {
			align-items: stretch;
			flex-direction: column;
		}

		.contact-actions {
			align-items: stretch;
			flex-direction: column;
		}

		.listen-button,
		.profile-button {
			justify-content: center;
		}
	}
</style>
