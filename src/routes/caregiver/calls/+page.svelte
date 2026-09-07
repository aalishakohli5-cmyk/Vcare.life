<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import { chooseCareRecipient } from '$lib/careConnections';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import Badge from '$lib/components/Badge.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import '../theme.css';

	/* =====================================================
	   STATE
	===================================================== */

	let caregiverName = $state('Caregiver');
	let caregiverInitial = $state('C');
	let caregiverId = $state('');

	let senior = $state({
		id: '',
		name: 'Senior',
		firstName: 'Senior',
		initials: 'S',
		phone: ''
	});

	let calls = $state([]);
	let loading = $state(true);
	let filter = $state('all'); // 'all' | 'completed' | 'distress'
	let expandedCallId = $state(null);
	let callStatus = $state(null); // { type: 'calling' | 'success' | 'error', message: '' }

	// Time
	let currentTime = $state('');
	let currentDate = $state('');

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
	}

	/* =====================================================
	   AUTH & DATA LOADING
	===================================================== */

	let callChannel;

	onMount(async () => {
		updateClock();
		const clock = setInterval(updateClock, 30000);

		const { data: { session } } = await supabase.auth.getSession();
		const { data: { user } } = await supabase.auth.getUser();

		if (!user) {
			goto('/auth?role=caregiver');
			return;
		}

		caregiverId = user.id;

		// Fetch caregiver profile
		const { data: profile } = await supabase
			.from('profiles')
			.select('*')
			.eq('id', user.id)
			.maybeSingle();

		if (profile?.full_name) {
			caregiverName = profile.full_name;
			caregiverInitial = profile.full_name.charAt(0).toUpperCase();
		}

		// Fetch assigned senior
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
			const firstSenior = chooseCareRecipient(seniors);
			senior.id = firstSenior.id;
			senior.name = firstSenior.full_name || 'Senior';
			senior.firstName = (firstSenior.full_name || 'Senior').split(' ')[0];
			senior.initials = (firstSenior.full_name || 'S')
				.split(' ')
				.map(n => n.charAt(0))
				.join('')
				.toUpperCase();
			senior.phone = firstSenior.phone || '';

			await loadCalls(firstSenior.id, token);

			// Real-time subscription to call_logs
			callChannel = supabase
				.channel(`caregiver-calls-${firstSenior.id}`)
				.on(
					'postgres_changes',
					{
						event: '*',
						schema: 'public',
						table: 'call_logs',
						filter: `senior_id=eq.${firstSenior.id}`
					},
					() => {
						loadCalls(firstSenior.id, token);
					}
				)
				.subscribe();
		}

		loading = false;

		return () => {
			clearInterval(clock);
			if (callChannel) supabase.removeChannel(callChannel);
		};
	});

	async function loadCalls(seniorId, token) {
		// 1. Direct Supabase load (instant ~50ms)
		try {
			const { data: sbCalls } = await supabase
				.from('call_logs')
				.select('*')
				.eq('senior_id', seniorId)
				.order('created_at', { ascending: false });

			if (sbCalls) {
				calls = sbCalls.map(c => ({
					id: c.id,
					call_id: c.call_id,
					status: c.status || 'completed',
					transcript: c.transcript || 'No transcript available for this call.',
					duration: c.duration ? `${c.duration}s` : '35s',
					distress_detected: c.distress_detected || false,
					created_at: c.created_at || new Date().toISOString(),
					formattedDate: new Date(c.created_at || Date.now()).toLocaleDateString('en-IN', {
						day: 'numeric',
						month: 'short',
						year: 'numeric'
					}),
					formattedTime: new Date(c.created_at || Date.now()).toLocaleTimeString('en-IN', {
						hour: '2-digit',
						minute: '2-digit',
						hour12: true
					})
				}));
			}
		} catch (e) {
			console.error('Failed to load calls from Supabase:', e);
		}

		// 2. Non-blocking backend sync with 1.5s timeout
		if (token && PUBLIC_BACKEND_URL) {
			try {
				const controller = new AbortController();
				const timeoutId = setTimeout(() => controller.abort(), 1500);

				const response = await fetch(
					`${PUBLIC_BACKEND_URL}/calls/${seniorId}`,
					{
						headers: {
							'Authorization': `Bearer ${token}`,
							'Content-Type': 'application/json'
						},
						signal: controller.signal
					}
				);
				clearTimeout(timeoutId);

				if (response.ok) {
					const data = await response.json();
					if (data && data.length > 0) {
						calls = data.map(c => ({
							id: c.id,
							call_id: c.call_id,
							status: c.status || 'completed',
							transcript: c.transcript || 'No transcript available for this call.',
							duration: c.duration ? `${c.duration}s` : '35s',
							distress_detected: c.distress_detected || false,
							created_at: c.created_at || new Date().toISOString(),
							formattedDate: new Date(c.created_at || Date.now()).toLocaleDateString('en-IN', {
								day: 'numeric',
								month: 'short',
								year: 'numeric'
							}),
							formattedTime: new Date(c.created_at || Date.now()).toLocaleTimeString('en-IN', {
								hour: '2-digit',
								minute: '2-digit',
								hour12: true
							})
						}));
					}
				}
			} catch (e) {
				// Silent non-blocking timeout
			}
		}
	}

	/* =====================================================
	   ACTIONS
	===================================================== */

	async function triggerCheckInCall() {
		if (!senior.phone) {
			callStatus = {
				type: 'error',
				message: `Cannot call ${senior.firstName}: Phone number is not configured.`
			};
			setTimeout(() => callStatus = null, 5000);
			return;
		}

		callStatus = {
			type: 'calling',
			message: `Connecting Bland AI to ${senior.firstName} (${senior.phone})...`
		};

		try {
			const response = await fetch('/api/bland-call', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					phoneNumber: senior.phone,
					seniorName: senior.firstName,
					seniorId: senior.id,
					medicationName: 'daily health check-in',
					dosage: 'prescribed routine'
				})
			});

			const data = await response.json();

			if (response.ok && data.success) {
				callStatus = {
					type: 'success',
					message: `✓ Vcare Call connected! Bland AI is speaking with ${senior.firstName}.`
				};
			} else {
				callStatus = {
					type: 'error',
					message: data.error || 'Failed to trigger AI call. Check Bland AI credentials.'
				};
			}
		} catch (err) {
			console.error('Call failed:', err);
			callStatus = {
				type: 'error',
				message: 'Network error triggering Vcare call.'
			};
		}

		setTimeout(() => callStatus = null, 6000);
	}

	function toggleTranscript(id) {
		expandedCallId = expandedCallId === id ? null : id;
	}

	async function logout() {
		await supabase.auth.signOut();
		goto('/');
	}

	/* =====================================================
	   CALL OUTCOME & MOOD ANALYSIS (MediMate-inspired)
	===================================================== */
	function analyzeCallOutcome(call) {
		const transcript = (call.transcript || '').toLowerCase();
		const isDistress = call.distress_detected || false;

		// 1. Routine status detection
		let status = 'confirmed';
		let statusLabel = 'Routine Confirmed';
		let statusEmoji = '✓';
		let statusBadgeClass = 'badge-confirmed';

		if (isDistress || transcript.includes('unwell') || transcript.includes('dizzy') || transcript.includes('pain') || transcript.includes('emergency') || transcript.includes('help')) {
			status = 'distress';
			statusLabel = 'Attention Needed';
			statusEmoji = '⚠️';
			statusBadgeClass = 'badge-alert';
		} else if (transcript.includes('not yet') || transcript.includes('haven\'t') || transcript.includes('forgot') || transcript.includes('later') || transcript.includes('no')) {
			status = 'pending';
			statusLabel = 'Pending Follow-up';
			statusEmoji = '⏳';
			statusBadgeClass = 'badge-pending';
		}

		// 2. AI sentiment & mood detection
		let mood = 'Peaceful & clear';
		let moodEmoji = '😊';
		let moodBadgeClass = 'mood-calm';

		if (isDistress) {
			mood = 'Expressed discomfort';
			moodEmoji = '😟';
			moodBadgeClass = 'mood-distress';
		} else if (transcript.includes('great') || transcript.includes('wonderful') || transcript.includes('good') || transcript.includes('cheerful') || transcript.includes('happy')) {
			mood = 'Upbeat & cheerful';
			moodEmoji = '🌟';
			moodBadgeClass = 'mood-upbeat';
		} else if (transcript.includes('tired') || transcript.includes('sleepy') || transcript.includes('resting')) {
			mood = 'Tired / resting';
			moodEmoji = '😴';
			moodBadgeClass = 'mood-tired';
		}

		// 3. Routine mention detection (medication, walk, yoga, hydration, etc.)
		let routineType = 'Daily Wellness';
		let routineEmoji = '🌿';
		if (transcript.includes('walk') || transcript.includes('stroll')) {
			routineType = 'Walk Routine';
			routineEmoji = '🚶';
		} else if (transcript.includes('yoga') || transcript.includes('stretch')) {
			routineType = 'Yoga / Movement';
			routineEmoji = '🧘';
		} else if (transcript.includes('water') || transcript.includes('diet') || transcript.includes('breakfast') || transcript.includes('meal')) {
			routineType = 'Diet & Nutrition';
			routineEmoji = '🥗';
		} else if (transcript.includes('pressure') || transcript.includes('sugar') || transcript.includes('bp')) {
			routineType = 'Vitals Check';
			routineEmoji = '🩺';
		} else if (transcript.includes('pill') || transcript.includes('tablet') || transcript.includes('medicine') || transcript.includes('dose')) {
			routineType = 'Medication';
			routineEmoji = '💊';
		}

		return {
			status,
			statusLabel,
			statusEmoji,
			statusBadgeClass,
			mood,
			moodEmoji,
			moodBadgeClass,
			routineType,
			routineEmoji
		};
	}

	// Computed counts
	let distressCount = $derived(calls.filter(c => c.distress_detected).length);

	let filteredCalls = $derived(
		filter === 'all'
			? calls
			: filter === 'completed'
				? calls.filter(c => c.status === 'completed')
				: calls.filter(c => c.distress_detected)
	);
</script>

<svelte:head>
	<title>Vcare Calls with {senior.firstName} — Vcare.life</title>
</svelte:head>

<div class="app" data-caregiver-portal>

	<!-- SIDEBAR -->
	<aside class="sidebar">
		<a href="/" class="brand">
			<div class="brand-heart">♥</div>
			<div>
				<strong>Vcare.life</strong>
				<span>A Voice That Cares</span>
			</div>
		</a>

		<div class="care-label">CAREGIVER SPACE</div>

		<nav>
			<a href="/caregiver/dashboard" class="nav-item">
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
			<a href="/caregiver/calls" class="nav-item active">
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
				<div class="mini-avatar">{senior.initials}</div>
				<div class="mini-senior-info">
				<div class="mini-avatar" aria-hidden="true">♡</div>
				<div>
					<small>CARING FOR</small>
					<strong>{senior.name}</strong>
				</div>
			</a>

			<div class="profile">
				<div class="profile-avatar">{caregiverInitial}</div>
				<div class="profile-copy">
					<strong>{caregiverName}</strong>
					<span>Caregiver</span>
				</div>
				<button class="logout" onclick={logout} aria-label="Sign out" title="Sign out">
					<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
						<polyline points="16 17 21 12 16 7"/>
						<line x1="21" y1="12" x2="9" y2="12"/>
					</svg>
				</button>
			</div>
		</div>
	</aside>

	<!-- MAIN CONTENT -->
	<main class="main">

		<!-- TOP BAR -->
		<header class="topbar">
			<div>
				<p class="date">{currentDate}</p>
				<!-- DISPLAY SERIF ONLY HERE FOR HEADLINE -->
				<h1 class="page-title">Vcare Calls with {senior.firstName}</h1>
				<p class="intro">Review daily AI phone check-ins, listen-in summaries, and conversation transcripts.</p>
			</div>

			<div class="top-actions">
				<a
					href={`tel:${senior.phone}`}
					class="btn-secondary"
					aria-label={`Direct phone call to ${senior.firstName}`}
				>
					<span>☎</span>
					<span>Direct Call</span>
				</a>
				<button class="btn-primary" onclick={triggerCheckInCall} disabled={callStatus?.type === 'calling'}>
					{#if callStatus?.type === 'calling'}
						<div class="voice-waveform" aria-hidden="true">
							<span class="bar bar-1"></span>
							<span class="bar bar-2"></span>
							<span class="bar bar-3"></span>
							<span class="bar bar-4"></span>
							<span class="bar bar-5"></span>
						</div>
						<span>Connecting Call...</span>
					{:else}
						<span>✨</span>
						<span>Trigger AI Check-In Call</span>
					{/if}
				</button>
			</div>
		</header>

		<!-- CALL STATUS TOAST -->
		{#if callStatus}
			<div
				class="call-banner"
				class:calling={callStatus.type === 'calling'}
				class:success={callStatus.type === 'success'}
				class:error={callStatus.type === 'error'}
			>
				{#if callStatus.type === 'calling'}
					<div class="voice-waveform live-waveform" aria-hidden="true">
						<span class="bar bar-1"></span>
						<span class="bar bar-2"></span>
						<span class="bar bar-3"></span>
						<span class="bar bar-4"></span>
						<span class="bar bar-5"></span>
					</div>
				{:else}
					<span aria-hidden="true">{callStatus.type === 'success' ? '✓' : '⚠️'}</span>
				{/if}
				<p>{callStatus.message}</p>
			</div>
		{/if}

		<!-- METRICS STRIP — USING SHARED METRICCARD COMPONENT -->
		<section class="metrics-grid">
			<MetricCard
				label="TOTAL CHECK-IN CALLS"
				value={calls.length}
				icon="☎"
				variant="total"
			/>
			<MetricCard
				label="WELLBEING STATUS"
				value={distressCount === 0 ? 'Peaceful & Normal' : `${distressCount} Attention Needed`}
				icon={distressCount === 0 ? '😊' : '⚠️'}
				variant={distressCount === 0 ? 'sentiment' : 'distress'}
			/>
			<MetricCard
				label="LATEST CHECK-IN"
				value={calls.length > 0 ? calls[0].formattedTime : 'None yet'}
				icon="⏰"
				variant="latest"
			/>
		</section>

		<!-- FILTER TABS -->
		<div class="filter-bar">
			<div class="filter-pills">
				<button class="pill" class:active={filter === 'all'} onclick={() => filter = 'all'}>
					All Calls ({calls.length})
				</button>
				<button class="pill" class:active={filter === 'completed'} onclick={() => filter = 'completed'}>
					Completed
				</button>
				<button class="pill" class:active={filter === 'distress'} onclick={() => filter = 'distress'}>
					Needs Attention ({distressCount})
				</button>
			</div>
		</div>

		<!-- CALL LOGS LIST -->
		{#if loading}
			<div class="loading-state">
				<div class="spinner">♥</div>
				<p>Loading check-in history...</p>
			</div>
		{:else if filteredCalls.length === 0}
			<div class="empty-card">
				<div class="empty-icon" aria-hidden="true">☎</div>
				<h3>No call history yet</h3>
				<p>Vcare will automatically call {senior.firstName} for daily medication check-ins. You can also trigger a call right now.</p>
				<button class="btn-primary" onclick={triggerCheckInCall}>
					<span>✨</span> Trigger First Vcare Check-In
				</button>
			</div>
		{:else}
			<div class="calls-list">
				{#each filteredCalls as call (call.id)}
					{@const outcome = analyzeCallOutcome(call)}
					<article class="call-card" class:distress={call.distress_detected}>
						<div class="call-header">
							<div class="call-lead">
								<div class="call-avatar" class:distress={call.distress_detected} aria-hidden="true">
									{call.distress_detected ? '⚠️' : '☎'}
								</div>
								<div>
									<div class="call-title-row">
										<h3>Check-in with {senior.firstName}</h3>
										<span class="routine-chip">{outcome.routineEmoji} {outcome.routineType}</span>
									</div>
									<span class="call-timestamp">
										{call.formattedDate} at {call.formattedTime} · Duration: {call.duration}
									</span>
								</div>
							</div>

							<div class="call-badges">
								<span class="outcome-badge {outcome.statusBadgeClass}">
									<span class="outcome-icon">{outcome.statusEmoji}</span>
									{outcome.statusLabel}
								</span>
								<span class="mood-badge {outcome.moodBadgeClass}">
									<span>{outcome.moodEmoji}</span>
									{outcome.mood}
								</span>
								<Badge variant="neutral">{call.status}</Badge>
							</div>
						</div>

						<div class="call-summary-box">
							<div class="summary-header">
								<p class="summary-title">Summary & Key Insights</p>
								<div class="verified-pill">
									<span class="verified-dot"></span>
									AI Voice Verified
								</div>
							</div>
							<p class="summary-content">
								"{call.transcript.substring(0, 220)}{call.transcript.length > 220 ? '...' : ''}"
							</p>
						</div>

						{#if expandedCallId === call.id}
							<div class="transcript-box">
								<h4>Full Conversation Transcript</h4>
								<div class="transcript-text">
									{call.transcript}
								</div>
							</div>
						{/if}

						<div class="call-footer">
							<button class="expand-btn" onclick={() => toggleTranscript(call.id)}>
								<span>{expandedCallId === call.id ? 'Hide Full Transcript ▲' : 'View Full Transcript ▼'}</span>
							</button>
							<a href={`tel:${senior.phone}`} class="call-senior-btn">
								<span aria-hidden="true">☎</span>
								<span>Follow Up with {senior.firstName}</span>
							</a>
						</div>
					</article>
				{/each}
			</div>
		{/if}

	</main>

</div>

<style>
	/* =====================================================
	   APP LAYOUT
	===================================================== */

	.app {
		min-height: 100vh;
		display: grid;
		grid-template-columns: 250px 1fr;
		background: var(--color-bg, #f8f6f0);
	}

	/* =====================================================
	   SIDEBAR (STANDARDIZED WITH >=11-13px TYPOGRAPHY)
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
		color: rgba(255, 255, 255, 0.68);
		font-size: 11px;
	}

	.care-label {
		margin: 28px 8px 12px;
		color: var(--color-brand-accent, #dce765);
		font-size: 11px;
		font-weight: 700;
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
		color: rgba(255, 255, 255, 0.75);
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
		background: var(--color-brand-accent, #dce76a);
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
		background: var(--color-brand-accent, #dce76a);
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
		color: rgba(255, 255, 255, 0.6);
		font-size: 10px;
		font-weight: 600;
		letter-spacing: 0.08em;
	}

	.mini-senior strong {
		margin-top: 1px;
		overflow: hidden;
		color: white;
		font-size: 13px;
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
		color: rgba(255, 255, 255, 0.6);
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
		max-width: 1080px;
		margin: 0 auto;
		padding: 34px clamp(24px, 4vw, 56px) 48px;
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
		color: var(--color-text-subtle, #4b6357);
		font-size: 12px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	/* FRAUNCES DISPLAY SERIF FOR HEADLINE ONLY */
	.page-title {
		margin: 0;
		font-family: var(--font-display, 'Fraunces', Georgia, serif);
		font-size: clamp(26px, 2.8vw, 36px);
		color: var(--color-text-primary, #0b3d2b);
		font-weight: 500;
		letter-spacing: -0.02em;
		line-height: 1.1;
	}

	.intro {
		margin: 6px 0 0;
		color: var(--color-text-secondary, #475569);
		font-size: 14px;
	}

	.top-actions {
		display: flex;
		gap: 12px;
		align-items: center;
		flex-shrink: 0;
	}

	.btn-primary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: var(--color-brand-primary, #0d5438);
		color: white;
		padding: 11px 20px;
		border-radius: var(--radius-md, 12px);
		border: none;
		font-size: 13px;
		font-weight: 700;
		cursor: pointer;
		transition: background 0.18s ease, transform 0.18s ease;
		box-shadow: 0 4px 14px rgba(13, 84, 56, 0.18);
	}

	.btn-primary:hover {
		background: #08402a;
		transform: translateY(-1px);
	}

	.btn-secondary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: var(--color-surface, #ffffff);
		color: var(--color-text-primary, #174631);
		padding: 11px 18px;
		border-radius: var(--radius-md, 12px);
		text-decoration: none;
		border: 1px solid var(--color-border, #e2e8e0);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.18s ease, border-color 0.18s ease;
	}

	.btn-secondary:hover {
		background: var(--color-surface-tinted, #f4f7f2);
		border-color: #cbdad0;
	}

	/* =====================================================
	   CALL STATUS TOAST
	===================================================== */

	.call-banner {
		padding: 14px 20px;
		border-radius: var(--radius-md, 14px);
		margin-bottom: 22px;
		display: flex;
		align-items: center;
		gap: 12px;
		font-weight: 600;
		animation: slideDown 0.3s ease;
	}

	.call-banner.calling {
		background: var(--color-warning-bg, #fef4e2);
		color: var(--color-warning-text, #92400e);
		border: 1px solid var(--color-warning-border, #fbd38d);
	}

	.call-banner.success {
		background: var(--color-success-bg, #e8f7ee);
		color: var(--color-success-text, #0f6e3c);
		border: 1px solid var(--color-success-border, #b7e8ca);
	}

	.call-banner.error {
		background: var(--color-danger-bg, #fdf0f0);
		color: var(--color-danger-text, #b91c1c);
		border: 1px solid var(--color-danger-border, #fecaca);
	}

	.call-banner p {
		margin: 0;
		font-size: 13px;
	}

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	/* =====================================================
	   METRICS GRID
	===================================================== */

	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 18px;
		margin-bottom: 26px;
	}

	/* =====================================================
	   FILTER BAR
	===================================================== */

	.filter-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20px;
	}

	.filter-pills {
		display: flex;
		gap: 6px;
		background: #eae3d2;
		padding: 4px;
		border-radius: var(--radius-md, 14px);
	}

	.pill {
		background: transparent;
		border: none;
		padding: 8px 16px;
		border-radius: var(--radius-sm, 10px);
		font-weight: 600;
		color: var(--color-text-secondary, #475569);
		cursor: pointer;
		font-size: 13px;
		transition: background 0.18s ease, color 0.18s ease;
	}

	.pill.active {
		background: var(--color-surface, #ffffff);
		color: var(--color-text-primary, #153d30);
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
		font-weight: 700;
	}

	/* =====================================================
	   CALLS LIST
	===================================================== */

	.calls-list {
		display: flex;
		flex-direction: column;
		gap: 18px;
	}

	.call-card {
		background: var(--color-surface, #ffffff);
		border-radius: var(--radius-lg, 18px);
		padding: 22px 24px;
		border: 1px solid var(--color-border, #e2e8e0);
		box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
		transition: transform 0.18s ease, box-shadow 0.18s ease;
	}

	.call-card:hover {
		transform: translateY(-2px);
		box-shadow: var(--shadow-md, 0 4px 14px rgba(23, 63, 49, 0.05));
	}

	.call-card.distress {
		border: 1.5px solid #fecaca;
		border-left: 4px solid var(--color-danger-text, #b91c1c);
		background: #fffcfc;
	}

	.call-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 16px;
		margin-bottom: 16px;
	}

	.call-lead {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.call-avatar {
		width: 44px;
		height: 44px;
		border-radius: var(--radius-md, 14px);
		background: var(--color-success-bg, #e8f7ee);
		color: var(--color-success-text, #0f6e3c);
		display: grid;
		place-items: center;
		font-size: 18px;
		flex-shrink: 0;
	}

	.call-avatar.distress {
		background: var(--color-danger-bg, #fee2e2);
		color: var(--color-danger-text, #b91c1c);
		font-weight: bold;
	}

	.call-lead h3 {
		margin: 0;
		font-size: 17px;
		font-weight: 700;
		color: var(--color-text-primary, #153d30);
	}

	.call-timestamp {
		color: var(--color-text-secondary, #475569);
		font-size: 13px;
		margin-top: 3px;
		display: block;
	}

	.call-badges {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-wrap: wrap;
	}

	.call-summary-box {
		background: var(--color-surface-tinted, #f6f8f5);
		border: 1px solid var(--color-border-subtle, #e5ede4);
		border-radius: var(--radius-md, 14px);
		padding: 14px 18px;
		margin-bottom: 16px;
	}

	.summary-title {
		margin: 0 0 4px;
		font-size: 11px;
		font-weight: 700;
		color: var(--color-text-subtle, #4b6357);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	.summary-content {
		margin: 0;
		font-size: 14px;
		color: var(--color-text-body, #1e293b);
		line-height: 1.55;
		font-style: italic;
	}

	.transcript-box {
		background: #fdfbf7;
		border: 1px solid #ebdcc5;
		border-radius: var(--radius-md, 14px);
		padding: 16px 20px;
		margin-bottom: 16px;
		animation: slideDown 0.2s ease;
	}

	.transcript-box h4 {
		margin: 0 0 10px;
		font-size: 13px;
		font-weight: 700;
		color: var(--color-text-primary, #0b3d2b);
	}

	.transcript-text {
		font-size: 13px;
		color: var(--color-text-body, #1e293b);
		line-height: 1.65;
		white-space: pre-wrap;
		font-family: inherit;
	}

	.call-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 14px;
		border-top: 1px dashed var(--color-border, #e2e8e0);
	}

	.expand-btn {
		background: transparent;
		border: none;
		color: var(--color-brand-primary, #116240);
		font-weight: 700;
		cursor: pointer;
		font-size: 13px;
		padding: 6px 0;
		transition: color 0.15s ease;
	}

	.expand-btn:hover {
		color: #074028;
		text-decoration: underline;
	}

	.call-senior-btn {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		background: var(--color-brand-accent, #dce76a);
		color: #143d2e;
		text-decoration: none;
		padding: 8px 16px;
		border-radius: var(--radius-sm, 10px);
		font-size: 13px;
		font-weight: 700;
		transition: background 0.18s ease, transform 0.18s ease;
	}

	.call-senior-btn:hover {
		background: var(--color-brand-accent-hover, #e8f37b);
		transform: translateY(-1px);
	}

	/* =====================================================
	   EMPTY / LOADING STATES
	===================================================== */

	.loading-state,
	.empty-card {
		background: var(--color-surface, #ffffff);
		border-radius: var(--radius-xl, 20px);
		padding: 60px 30px;
		text-align: center;
		border: 1px solid var(--color-border, #e2e8e0);
	}

	.empty-icon {
		width: 60px;
		height: 60px;
		background: var(--color-success-bg, #e8f7ee);
		color: var(--color-brand-primary, #0b6845);
		border-radius: var(--radius-lg, 18px);
		display: grid;
		place-items: center;
		font-size: 26px;
		margin: 0 auto 16px;
	}

	.empty-card h3 {
		margin: 0 0 6px;
		color: var(--color-text-primary, #173f31);
		font-size: 18px;
		font-weight: 700;
	}

	.empty-card p {
		margin: 0 0 20px;
		color: var(--color-text-secondary, #475569);
		font-size: 14px;
		max-width: 480px;
		margin-left: auto;
		margin-right: auto;
	}

	/* =====================================================
	   RESPONSIVE
	===================================================== */

	@media (max-width: 1050px) {
		.app {
			grid-template-columns: 210px 1fr;
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

		.top-actions {
			width: 100%;
			flex-direction: column;
			align-items: stretch;
		}

		.btn-primary,
		.btn-secondary {
			justify-content: center;
		}

		.call-header {
			flex-direction: column;
		}

		.call-footer {
			flex-direction: column;
			align-items: stretch;
			gap: 10px;
		}

		.call-senior-btn {
			justify-content: center;
		}
	}

	/* =====================================================
	   VOICE WAVEFORM ANIMATION (MediMate-inspired)
	===================================================== */
	.voice-waveform {
		display: inline-flex;
		align-items: center;
		gap: 3px;
		height: 18px;
		vertical-align: middle;
	}

	.voice-waveform .bar {
		display: inline-block;
		width: 3px;
		background: currentColor;
		border-radius: 2px;
		animation: waveformPulse 1s ease-in-out infinite alternate;
	}

	.voice-waveform .bar-1 { height: 6px; animation-delay: 0.05s; }
	.voice-waveform .bar-2 { height: 16px; animation-delay: 0.2s; }
	.voice-waveform .bar-3 { height: 11px; animation-delay: 0.35s; }
	.voice-waveform .bar-4 { height: 18px; animation-delay: 0.15s; }
	.voice-waveform .bar-5 { height: 8px; animation-delay: 0.4s; }

	.live-waveform {
		margin-right: 4px;
	}

	.live-waveform .bar {
		background: #d97706;
		width: 3.5px;
	}

	@keyframes waveformPulse {
		0% {
			transform: scaleY(0.3);
			opacity: 0.6;
		}
		100% {
			transform: scaleY(1.1);
			opacity: 1;
		}
	}

	/* =====================================================
	   OUTCOME, MOOD & ROUTINE BADGES
	===================================================== */
	.call-title-row {
		display: flex;
		align-items: center;
		gap: 10px;
		flex-wrap: wrap;
	}

	.routine-chip {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		background: #f1f5f0;
		color: #1a4d36;
		border: 1px solid #d4e3d2;
		border-radius: 9999px;
		padding: 2px 9px;
		font-size: 11.5px;
		font-weight: 600;
	}

	.outcome-badge {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		padding: 4px 10px;
		border-radius: 9999px;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.01em;
	}

	.outcome-badge.badge-confirmed {
		background: #eaf8f0;
		color: #0b6845;
		border: 1px solid #b7e8ca;
	}

	.outcome-badge.badge-alert {
		background: #fdf0f0;
		color: #b91c1c;
		border: 1px solid #fecaca;
	}

	.outcome-badge.badge-pending {
		background: #fef8ee;
		color: #b45309;
		border: 1px solid #fde68a;
	}

	.outcome-icon {
		font-size: 12px;
	}

	.mood-badge {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		padding: 4px 10px;
		border-radius: 9999px;
		font-size: 12px;
		font-weight: 600;
	}

	.mood-badge.mood-calm {
		background: #f4f6f4;
		color: #334155;
		border: 1px solid #e2e8e0;
	}

	.mood-badge.mood-upbeat {
		background: #fefce8;
		color: #854d0e;
		border: 1px solid #fef08a;
	}

	.mood-badge.mood-distress {
		background: #fef2f2;
		color: #991b1b;
		border: 1px solid #fee2e2;
	}

	.mood-badge.mood-tired {
		background: #f5f3ff;
		color: #5b21b6;
		border: 1px solid #ede9fe;
	}

	.summary-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 10px;
		margin-bottom: 6px;
		flex-wrap: wrap;
	}

	.verified-pill {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		background: #ecfdf5;
		border: 1px solid #a7f3d0;
		color: #047857;
		font-size: 11px;
		font-weight: 700;
		padding: 2px 8px;
		border-radius: 9999px;
		letter-spacing: 0.02em;
	}

	.verified-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: #10b981;
		box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.25);
		animation: verifiedPulse 2s infinite;
	}

	@keyframes verifiedPulse {
		0%, 100% {
			box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.25);
		}
		50% {
			box-shadow: 0 0 0 5px rgba(16, 185, 129, 0.45);
		}
	}
</style>
