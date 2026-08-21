<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

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
			.select('full_name')
			.eq('id', user.id)
			.maybeSingle();

		if (profile?.full_name) {
			caregiverName = profile.full_name;
			caregiverInitial = profile.full_name.charAt(0).toUpperCase();
		}

		// Fetch assigned senior
		try {
			const token = session?.access_token;
			if (token && PUBLIC_BACKEND_URL) {
				const response = await fetch(
					`${PUBLIC_BACKEND_URL}/caregiver/${user.id}/seniors`,
					{
						headers: {
							'Authorization': `Bearer ${token}`,
							'Content-Type': 'application/json'
						}
					}
				);

				if (response.ok) {
					const seniors = await response.json();
					if (seniors.length > 0) {
						const firstSenior = seniors[0];
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
				}
			}
		} catch (err) {
			console.error('Error fetching senior/calls:', err);
		} finally {
			loading = false;
		}

		return () => {
			clearInterval(clock);
			if (callChannel) supabase.removeChannel(callChannel);
		};
	});

	async function loadCalls(seniorId, token) {
		try {
			const response = await fetch(
				`${PUBLIC_BACKEND_URL}/calls/${seniorId}`,
				{
					headers: {
						'Authorization': `Bearer ${token}`,
						'Content-Type': 'application/json'
					}
				}
			);

			if (response.ok) {
				const data = await response.json();
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
		} catch (e) {
			console.error('Failed to load calls:', e);
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
					medicationName: 'afternoon medicines',
					dosage: 'prescribed dosage'
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

<div class="app">

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
				<span class="nav-icon">⌂</span>
				<span>Home</span>
			</a>
			<a href="/caregiver/medicines" class="nav-item">
				<span class="nav-icon">✚</span>
				<span>Medicines</span>
			</a>
			<a href="/caregiver/calls" class="nav-item active">
				<span class="nav-icon">☎</span>
				<span>Vcare Calls</span>
			</a>
			<a href="/caregiver/senior" class="nav-item">
				<span class="nav-icon">♡</span>
				<span>Senior Profile</span>
			</a>
		</nav>

		<div class="sidebar-bottom">
			<a href="/caregiver/senior" class="mini-senior">
				<div class="mini-avatar">{senior.initials}</div>
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
				<button class="logout" onclick={logout} aria-label="Sign out">↗</button>
			</div>
		</div>
	</aside>

	<!-- MAIN CONTENT -->
	<main class="main">

		<!-- TOP BAR -->
		<header class="topbar">
			<div>
				<p class="date">{currentDate}</p>
				<h1>Vcare Calls with {senior.firstName}</h1>
				<p class="intro">Review daily AI phone check-ins, listen-in summaries, and conversation transcripts.</p>
			</div>

			<div class="top-actions">
				<a href={`tel:${senior.phone}`} class="btn-secondary">
					<span>☎</span>
					<span>Direct Call</span>
				</a>
				<button class="btn-primary" onclick={triggerCheckInCall}>
					<span>✨</span>
					<span>Trigger AI Check-In Call</span>
				</button>
			</div>
		</header>

		<!-- CALL STATUS TOAST -->
		{#if callStatus}
			<div class="call-banner" class:calling={callStatus.type === 'calling'} class:success={callStatus.type === 'success'} class:error={callStatus.type === 'error'}>
				<span>{callStatus.type === 'calling' ? '⏳' : callStatus.type === 'success' ? '✓' : '⚠'}</span>
				<p>{callStatus.message}</p>
			</div>
		{/if}

		<!-- METRICS STRIP -->
		<section class="metrics-grid">
			<div class="metric-card">
				<div class="metric-icon total">☎</div>
				<div>
					<small>TOTAL CHECK-IN CALLS</small>
					<strong>{calls.length}</strong>
				</div>
			</div>
			<div class="metric-card">
				<div class="metric-icon sentiment">😊</div>
				<div>
					<small>WELLBEING STATUS</small>
					<strong>{distressCount === 0 ? 'Peaceful & Normal' : `${distressCount} Attention Needed`}</strong>
				</div>
			</div>
			<div class="metric-card">
				<div class="metric-icon latest">⏰</div>
				<div>
					<small>LATEST CHECK-IN</small>
					<strong>{calls.length > 0 ? calls[0].formattedTime : 'None yet'}</strong>
				</div>
			</div>
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
				<div class="empty-icon">☎</div>
				<h3>No call history yet</h3>
				<p>Vcare will automatically call {senior.firstName} for daily medication check-ins. You can also trigger a call right now.</p>
				<button class="btn-primary" onclick={triggerCheckInCall}>
					<span>✨</span> Trigger First Vcare Check-In
				</button>
			</div>
		{:else}
			<div class="calls-list">
				{#each filteredCalls as call (call.id)}
					<div class="call-card" class:distress={call.distress_detected}>
						<div class="call-header">
							<div class="call-lead">
								<div class="call-avatar" class:distress={call.distress_detected}>
									{call.distress_detected ? '!' : '☎'}
								</div>
								<div>
									<h3>Check-in with {senior.firstName}</h3>
									<span class="call-timestamp">
										{call.formattedDate} at {call.formattedTime} · Duration: {call.duration}
									</span>
								</div>
							</div>

							<div class="call-badges">
								{#if call.distress_detected}
									<span class="badge distress">⚠ Distress Detected</span>
								{:else}
									<span class="badge normal">✓ Normal Check-in</span>
								{/if}
								<span class="badge status">{call.status}</span>
							</div>
						</div>

						<div class="call-summary-box">
							<p class="summary-title">Summary & Insight:</p>
							<p class="summary-content">
								"{call.transcript.substring(0, 160)}{call.transcript.length > 160 ? '...' : ''}"
							</p>
						</div>

						{#if expandedCallId === call.id}
							<div class="transcript-box">
								<h4>Full Conversation Transcript:</h4>
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
								<span>☎</span>
								<span>Follow Up with {senior.firstName}</span>
							</a>
						</div>
					</div>
				{/each}
			</div>
		{/if}

	</main>

</div>

<style>
	:global(*) { box-sizing: border-box; }
	:global(html), :global(body) { margin: 0; min-height: 100%; }
	:global(body) {
		background: #f7f0e2;
		color: #173f31;
		font-family: "Comic Sans MS", "Comic Sans", "Chalkboard SE", "Marker Felt", cursive;
	}

	button, a { font-family: inherit; }

	.app {
		min-height: 100vh;
		display: grid;
		grid-template-columns: 245px 1fr;
		background: radial-gradient(circle at 100% 0%, rgba(223, 231, 93, 0.12), transparent 25%), #f7f0e2;
	}

	/* SIDEBAR */
	.sidebar {
		position: sticky;
		top: 0;
		height: 100vh;
		padding: 28px 18px 22px;
		display: flex;
		flex-direction: column;
		background: linear-gradient(180deg, #073e2c, #07563a);
		color: white;
		border-right: 1px solid rgba(255,255,255,0.08);
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 11px;
		padding: 0 8px;
		text-decoration: none;
		color: white;
	}

	.brand-heart {
		width: 42px;
		height: 42px;
		display: grid;
		place-items: center;
		border-radius: 13px;
		background: white;
		color: #0b6845;
		font-size: 22px;
	}

	.brand > div:last-child { display: flex; flex-direction: column; }
	.brand strong { font-size: 19px; }
	.brand span { margin-top: 2px; color: rgba(255,255,255,0.65); font-size: 8px; }

	.care-label {
		margin: 35px 10px 13px;
		color: #dce765;
		font-size: 9px;
		font-weight: bold;
		letter-spacing: 1.4px;
	}

	nav { display: grid; gap: 6px; }

	.nav-item {
		min-height: 47px;
		padding: 0 13px;
		display: flex;
		align-items: center;
		gap: 12px;
		border-radius: 13px;
		text-decoration: none;
		color: rgba(255,255,255,0.68);
		font-size: 12px;
		font-weight: bold;
		transition: 0.18s ease;
	}

	.nav-item:hover {
		color: white;
		background: rgba(255,255,255,0.07);
		transform: translateX(3px);
	}

	.nav-item.active { color: #143d2e; background: #dce76a; }
	.nav-icon { width: 26px; font-size: 17px; text-align: center; }
	.sidebar-bottom { margin-top: auto; }

	.mini-senior {
		margin-bottom: 13px;
		padding: 11px;
		display: flex;
		align-items: center;
		gap: 10px;
		border: 1px solid rgba(255,255,255,0.10);
		border-radius: 14px;
		background: rgba(255,255,255,0.06);
		text-decoration: none;
		color: inherit;
		transition: 0.2s ease;
	}

	.mini-senior:hover { background: rgba(255,255,255,0.12); }

	.mini-avatar {
		width: 36px;
		height: 36px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 11px;
		background: #dce76a;
		color: #16402e;
		font-size: 10px;
		font-weight: bold;
	}

	.mini-senior small { color: rgba(255,255,255,0.5); font-size: 6px; letter-spacing: 1px; }
	.mini-senior strong { color: white; font-size: 10px; }

	.profile {
		padding: 13px 8px 0;
		display: flex;
		align-items: center;
		gap: 9px;
		border-top: 1px solid rgba(255,255,255,0.10);
	}

	.profile-avatar {
		width: 36px;
		height: 36px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 50%;
		background: #f3e6c8;
		color: #174631;
		font-size: 12px;
		font-weight: bold;
	}

	.profile-copy { min-width: 0; display: flex; flex: 1; flex-direction: column; }
	.profile-copy strong { font-size: 10px; color: white; }
	.profile-copy span { color: rgba(255,255,255,0.53); font-size: 7px; }

	.logout {
		border: 0;
		background: transparent;
		color: rgba(255,255,255,0.7);
		cursor: pointer;
		font-size: 15px;
	}

	/* MAIN */
	.main {
		width: 100%;
		max-width: 1500px;
		margin: 0 auto;
		padding: 34px clamp(30px, 4vw, 65px) 45px;
	}

	.topbar {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 30px;
		margin-bottom: 26px;
	}

	.date { margin: 0 0 5px; color: #85745f; font-size: 11px; }
	.topbar h1 { margin: 0; font-size: clamp(24px, 2.5vw, 34px); color: #0b3d2b; }
	.intro { margin: 6px 0 0; color: #72624d; font-size: 13px; }

	.top-actions { display: flex; gap: 12px; align-items: center; }

	.btn-primary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: #0d5438;
		color: white;
		padding: 12px 22px;
		border-radius: 14px;
		border: none;
		font-weight: bold;
		cursor: pointer;
		transition: 0.2s ease;
		box-shadow: 0 4px 14px rgba(13,84,56,0.18);
	}

	.btn-primary:hover {
		background: #08402a;
		transform: translateY(-2px);
	}

	.btn-secondary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: #f0e6d2;
		color: #174631;
		padding: 12px 20px;
		border-radius: 14px;
		text-decoration: none;
		border: 1px solid #dfd1b8;
		font-weight: bold;
		cursor: pointer;
		transition: 0.2s ease;
	}

	.btn-secondary:hover { background: #e6d8c0; transform: translateY(-2px); }

	/* CALL BANNER */
	.call-banner {
		padding: 14px 20px;
		border-radius: 14px;
		margin-bottom: 22px;
		display: flex;
		align-items: center;
		gap: 12px;
		font-weight: bold;
		animation: slideDown 0.3s ease;
	}

	.call-banner.calling { background: #fff5e0; color: #9c6500; border: 1px solid #ffd880; }
	.call-banner.success { background: #e3fae8; color: #0f6828; border: 1px solid #a6e8b4; }
	.call-banner.error { background: #fde8e8; color: #b81414; border: 1px solid #f8b4b4; }
	.call-banner p { margin: 0; font-size: 13px; }

	@keyframes slideDown {
		from { opacity: 0; transform: translateY(-10px); }
		to { opacity: 1; transform: translateY(0); }
	}

	/* METRICS */
	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 18px;
		margin-bottom: 26px;
	}

	.metric-card {
		background: white;
		padding: 20px;
		border-radius: 18px;
		display: flex;
		align-items: center;
		gap: 16px;
		border: 1px solid #ebe0cc;
		box-shadow: 0 4px 18px rgba(23,63,49,0.04);
	}

	.metric-icon {
		width: 46px;
		height: 46px;
		border-radius: 14px;
		display: grid;
		place-items: center;
		font-size: 20px;
	}

	.metric-icon.total { background: #e8f0fe; color: #1a73e8; }
	.metric-icon.sentiment { background: #e6f7eb; color: #137333; }
	.metric-icon.latest { background: #fef7e0; color: #b06000; }

	.metric-card small { display: block; font-size: 10px; color: #8a7a66; letter-spacing: 0.8px; }
	.metric-card strong { font-size: 22px; color: #173f31; }

	/* FILTER BAR */
	.filter-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20px;
	}

	.filter-pills {
		display: flex;
		gap: 8px;
		background: #eae0cd;
		padding: 4px;
		border-radius: 14px;
	}

	.pill {
		background: transparent;
		border: none;
		padding: 8px 18px;
		border-radius: 10px;
		font-weight: bold;
		color: #61523e;
		cursor: pointer;
		font-size: 12px;
		transition: 0.2s ease;
	}

	.pill.active {
		background: white;
		color: #173f31;
		box-shadow: 0 2px 8px rgba(0,0,0,0.06);
	}

	/* CALLS LIST */
	.calls-list {
		display: flex;
		flex-direction: column;
		gap: 18px;
	}

	.call-card {
		background: white;
		border-radius: 20px;
		padding: 24px;
		border: 1px solid #ebe0cc;
		box-shadow: 0 4px 18px rgba(23,63,49,0.04);
		transition: 0.2s ease;
	}

	.call-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 24px rgba(23,63,49,0.08);
	}

	.call-card.distress {
		border-color: #f5c4c4;
		background: #fffafa;
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
		border-radius: 14px;
		background: #e8f5ec;
		color: #0b6845;
		display: grid;
		place-items: center;
		font-size: 20px;
	}

	.call-avatar.distress {
		background: #fae8e8;
		color: #c91818;
		font-weight: bold;
	}

	.call-lead h3 { margin: 0; font-size: 18px; color: #173f31; }
	.call-timestamp { color: #85745f; font-size: 12px; margin-top: 3px; display: block; }

	.call-badges {
		display: flex;
		gap: 8px;
	}

	.badge {
		padding: 6px 12px;
		border-radius: 10px;
		font-size: 11px;
		font-weight: bold;
		text-transform: capitalize;
	}

	.badge.normal { background: #d7f5dd; color: #0b6845; }
	.badge.distress { background: #fae0e0; color: #b81414; }
	.badge.status { background: #f4ecdc; color: #4b3e2d; }

	.call-summary-box {
		background: #fdfbf7;
		border: 1px solid #eee5d3;
		border-radius: 14px;
		padding: 14px 18px;
		margin-bottom: 16px;
	}

	.summary-title { margin: 0 0 4px; font-size: 11px; font-weight: bold; color: #85745f; }
	.summary-content { margin: 0; font-size: 14px; color: #173f31; line-height: 1.5; font-style: italic; }

	.transcript-box {
		background: #f3edd8;
		border-radius: 14px;
		padding: 16px 20px;
		margin-bottom: 16px;
		animation: slideDown 0.2s ease;
	}

	.transcript-box h4 { margin: 0 0 10px; font-size: 13px; color: #0b3d2b; }

	.transcript-text {
		font-size: 13px;
		color: #29382e;
		line-height: 1.6;
		white-space: pre-wrap;
		font-family: inherit;
	}

	.call-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 14px;
		border-top: 1px dashed #ede2cf;
	}

	.expand-btn {
		background: transparent;
		border: none;
		color: #0b6845;
		font-weight: bold;
		cursor: pointer;
		font-size: 12px;
		padding: 6px 0;
	}

	.expand-btn:hover { text-decoration: underline; }

	.call-senior-btn {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		background: #ebf5b8;
		color: #174631;
		text-decoration: none;
		padding: 8px 16px;
		border-radius: 10px;
		font-size: 12px;
		font-weight: bold;
		transition: 0.2s ease;
	}

	.call-senior-btn:hover { background: #dce76a; }

	/* EMPTY / LOADING */
	.loading-state, .empty-card {
		background: white;
		border-radius: 24px;
		padding: 60px 30px;
		text-align: center;
		border: 1px solid #ebe0cc;
	}

	.empty-icon {
		width: 60px;
		height: 60px;
		background: #f4ecdc;
		color: #0b6845;
		border-radius: 20px;
		display: grid;
		place-items: center;
		font-size: 28px;
		margin: 0 auto 16px;
	}

	.empty-card h3 { margin: 0 0 6px; color: #173f31; }
	.empty-card p { margin: 0 0 20px; color: #72624d; max-width: 460px; margin-left: auto; margin-right: auto; }
</style>
