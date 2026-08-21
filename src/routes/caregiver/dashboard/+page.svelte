<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';

	/* =====================================================
	   USER / SENIOR
	===================================================== */

	let caregiverName = $state('Caregiver');
	let caregiverInitial = $state('C');

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

	let medications = $state([]);

	/* =====================================================
	   ALERTS
	===================================================== */

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

	/* =====================================================
	   AUTH + PROFILE
	===================================================== */

	onMount(async () => {
		updateClock();

		const clock = setInterval(updateClock, 30000);

		const {
			data: { session }
		} = await supabase.auth.getSession();

		const {
			data: { user }
		} = await supabase.auth.getUser();

		if (user) {
			const { data: profile } = await supabase
				.from('profiles')
				.select('full_name')
				.eq('id', user.id)
				.maybeSingle();

			if (profile?.full_name) {
				caregiverName = profile.full_name;
				caregiverInitial = profile.full_name.charAt(0).toUpperCase();
			}

			// Fetch assigned seniors from backend
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
							// Load first senior's data
							const firstSenior = seniors[0];
							senior.name = firstSenior.full_name || 'Senior';
							senior.firstName = (firstSenior.full_name || 'Senior').split(' ')[0];
							senior.initials = (firstSenior.full_name || 'S')
								.split(' ')
								.map(n => n.charAt(0))
								.join('')
								.toUpperCase();
							senior.phone = firstSenior.phone || '';
							senior.status = 'Connected';
							senior.lastCheckIn = 'No calls yet';
							senior.mood = 'Happy';
							senior.moodEmoji = '😊';
							seniorId = firstSenior.id;

							// Fetch medications for this senior
							if (token) {
								const medResponse = await fetch(
									`${PUBLIC_BACKEND_URL}/medications/${firstSenior.id}`,
									{
										headers: {
											'Authorization': `Bearer ${token}`,
											'Content-Type': 'application/json'
										}
									}
								);

								if (medResponse.ok) {
									const medData = await medResponse.json();
									medications = medData.map(m => ({
										id: m.id,
										name: m.name,
										dosage: m.dosage,
										time: m.scheduled_time,
										status: m.taken ? 'taken' : 'pending'
									}));

									// Generate alerts for pending medications
									const pendingMeds = medications.filter(m => m.status === 'pending');
									alerts = pendingMeds.map((m, idx) => ({
										id: idx + 1,
										title: `${m.name} is still pending`,
										message: `Scheduled for ${m.time}. Vcare will remind ${senior.firstName}.`
									}));

									// Subscribe to real-time medication updates for this senior
									supabase
										.channel(`medications:${firstSenior.id}`)
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
													// Update alerts
													const pendingMeds = medications.filter(m => m.status === 'pending');
													alerts = pendingMeds.map((m, idx) => ({
														id: idx + 1,
														title: `${m.name} is still pending`,
														message: `Scheduled for ${m.time}. Vcare will remind ${senior.firstName}.`
													}));
													console.log('Medication updated in real-time:', updated.id);
												} else if (payload.eventType === 'INSERT') {
													const newMed = payload.new;
													medications = [...medications, {
														id: newMed.id,
														name: newMed.name,
														dosage: newMed.dosage,
														time: newMed.scheduled_time,
														status: newMed.taken ? 'taken' : 'pending'
													}].sort((a, b) => a.time.localeCompare(b.time));
													const pendingMeds = medications.filter(m => m.status === 'pending');
													alerts = pendingMeds.map((m, idx) => ({
														id: idx + 1,
														title: `${m.name} is still pending`,
														message: `Scheduled for ${m.time}. Vcare will remind ${senior.firstName}.`
													}));
												}
											}
										)
										.subscribe();
								}
							}

							// Fetch call history for this senior
							if (token) {
								const callResponse = await fetch(
									`${PUBLIC_BACKEND_URL}/calls/${firstSenior.id}`,
									{
										headers: {
											'Authorization': `Bearer ${token}`,
											'Content-Type': 'application/json'
										}
									}
								);

								if (callResponse.ok) {
									const callData = await callResponse.json();
									if (callData.length > 0) {
										const latestCall = callData[0];
										recentCall = {
											date: new Date(latestCall.created_at).toLocaleDateString('en-IN'),
											time: new Date(latestCall.created_at).toLocaleTimeString('en-IN', {
												hour: '2-digit',
												minute: '2-digit'
											}),
											duration: latestCall.duration ? `${latestCall.duration}s` : '35s',
											status: latestCall.status || 'completed',
											summary: latestCall.transcript
												? latestCall.transcript.substring(0, 100) + '...'
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
								}
							}
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
				}
			} catch (error) {
				console.error('Failed to fetch seniors:', error);
			}
		}

		return () => clearInterval(clock);
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
</script>

<svelte:head>
	<title>Caregiver Dashboard — Vcare.life</title>
</svelte:head>


<div class="app">

	<!-- =====================================================
	     SIDEBAR
	===================================================== -->

	<aside class="sidebar">

		<a href="/" class="brand">

			<div class="brand-heart">
				♥
			</div>

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

				<span class="nav-icon">
					⌂
				</span>

				<span>Home</span>

			</a>


			<a href="/caregiver/medicines" class="nav-item">

				<span class="nav-icon">
					✚
				</span>

				<span>Medicines</span>

			</a>


			<a href="/caregiver/calls" class="nav-item">

				<span class="nav-icon">
					☎
				</span>

				<span>Vcare Calls</span>

			</a>


			<a href="/caregiver/senior" class="nav-item">

				<span class="nav-icon">
					♡
				</span>

				<span>Senior Profile</span>

			</a>

		</nav>


		<div class="sidebar-bottom">

			<a href="/caregiver/senior" class="mini-senior">

				<div class="mini-avatar">
					{senior.initials}
				</div>

				<div>
					<small>CARING FOR</small>
					<strong>{senior.name}</strong>
				</div>

			</a>


			<div class="profile">

				<div class="profile-avatar">
					{caregiverInitial}
				</div>

				<div class="profile-copy">

					<strong>
						{caregiverName}
					</strong>

					<span>
						Caregiver
					</span>

				</div>


				<button
					class="logout"
					onclick={logout}
					aria-label="Sign out"
				>
					↗
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

				<h1>
					{greeting}, {caregiverName.split(' ')[0]}!
				</h1>

				<p class="intro">
					Here's how {senior.firstName} is doing today.
				</p>

			</div>


			<div class="live-time">

				<span class="live-dot"></span>

				<div>
					<small>LIVE</small>
					<strong>{currentTime}</strong>
				</div>

			</div>

		</header>


		<!-- =================================================
		     SENIOR STATUS
		================================================= -->

		<section class="senior-card">

			<div class="senior-main">

				<div class="senior-avatar">
					{senior.initials}
				</div>


				<div class="senior-info">

					<p class="eyebrow">
						YOUR SENIOR
					</p>

					<div class="senior-name-row">

						<h2>
							{senior.name}
						</h2>

						<span class="status-pill">
							<span></span>
							{senior.status}
						</span>

					</div>


					<p class="checkin">
						Last Vcare check-in:
						<strong>{senior.lastCheckIn}</strong>
					</p>

				</div>

			</div>


			<div class="senior-actions">

				<div class="mood-small">

					<span class="mood-emoji">
						{senior.moodEmoji}
					</span>

					<div>
						<small>TODAY'S MOOD</small>
						<strong>{senior.mood}</strong>
					</div>

				</div>


				<a
					href={`tel:${senior.phone}`}
					class="call-button"
					aria-label={`Call ${senior.firstName}`}
				>
					<span>☎</span>
					Call {senior.firstName}
				</a>

			</div>

		</section>


		<!-- =================================================
		     MAIN GRID
		================================================= -->

		<section class="dashboard-grid">


			<!-- =================================================
			     MEDICATIONS
			================================================= -->

			<article class="panel medication-panel">

				<div class="panel-header">

					<div>

						<p class="eyebrow">
							TODAY
						</p>

						<h2>
							{senior.firstName}'s medicines
						</h2>

						<span class="panel-subtitle">
							A quick look at today's medication.
						</span>

					</div>


					<div class="medicine-icon">
						✚
					</div>

				</div>


				<div class="medicine-list">

					{#each medications as medicine}

						<div class="medicine-row">

							<div
								class="medicine-check"
								class:taken={medicine.status === 'taken'}
							>
								{medicine.status === 'taken' ? '✓' : '○'}
							</div>


							<div class="medicine-info">

								<strong>
									{medicine.name}
								</strong>

								<span>
									{medicine.dosage} · {medicine.time}
								</span>

							</div>


							<span
								class="medicine-status"
								class:taken={medicine.status === 'taken'}
								class:pending={medicine.status === 'pending'}
							>
								{medicine.status === 'taken'
									? 'Taken'
									: 'Pending'}
							</span>

						</div>

					{/each}

				</div>


				<div class="panel-actions">

					<button
						class="add-button"
						onclick={openMedicines}
					>
						<span>＋</span>
						Add medicine
					</button>


					<button
						class="text-button"
						onclick={openMedicines}
					>
						View all
						<span>→</span>
					</button>

				</div>

			</article>


			<!-- =================================================
			     ALERTS
			================================================= -->

			<article class="panel alert-panel">

				<div class="panel-header compact">

					<div>

						<p class="eyebrow orange">
							NEEDS ATTENTION
						</p>

						<h2>
							Right now
						</h2>

					</div>


					<div class="alert-icon">
						!
					</div>

				</div>


				{#if alerts.length > 0}

					<div class="alerts">

						{#each alerts as alert}

							<div class="alert">

								<div class="alert-symbol">
									!
								</div>

								<div>

									<strong>
										{alert.title}
									</strong>

									<p>
										{alert.message}
									</p>

								</div>

							</div>

						{/each}

					</div>

				{:else}

					<div class="all-good">

						<div>
							✓
						</div>

						<section>

							<strong>
								Everything looks good.
							</strong>

							<p>
								Nothing needs your attention right now.
							</p>

						</section>

					</div>

				{/if}


				<div class="care-note">

					<span>♡</span>

					<p>
						We'll keep this space quiet unless
						something actually needs you.
					</p>

				</div>

			</article>


			<!-- =================================================
			     RECENT VCARE CALL
			================================================= -->

			<article class="panel call-panel">

				<div class="panel-header">

					<div>

						<p class="eyebrow">
							RECENT CHECK-IN
						</p>

						<h2>
							Latest Vcare call
						</h2>

						<span class="panel-subtitle">
							A small window into how
							{senior.firstName} is doing.
						</span>

					</div>


					<div class="call-icon">
						☎
					</div>

				</div>


				<div class="call-summary">

					<div class="call-top">

						<div>

							<strong>
								{recentCall.date} · {recentCall.time}
							</strong>

							<span>
								{recentCall.duration}
							</span>

						</div>


						<span class="completed">
							✓ {recentCall.status}
						</span>

					</div>


					<div class="call-tags">

						<span>
							💊 Medicine confirmed
						</span>

						<span>
							🙂 Mood good
						</span>

					</div>


					<p class="summary-text">
						"{recentCall.summary}"
					</p>

				</div>


				<button
					class="wide-button"
					onclick={openCalls}
				>
					View call history
					<span>→</span>
				</button>

			</article>


			<!-- =================================================
			     MOOD
			================================================= -->

			<article class="panel mood-panel">

				<div>

					<p class="eyebrow">
						WELLBEING
					</p>

					<h2>
						How {senior.firstName} has been feeling
					</h2>

				</div>


				<div class="current-mood">

					<div class="big-emoji">
						{senior.moodEmoji}
					</div>

					<div>

						<small>TODAY</small>

						<strong>
							{senior.mood}
						</strong>

						<span>
							From the latest Vcare check-in
						</span>

					</div>

				</div>


				<div class="mood-history">

					<div>
						<span>Yesterday</span>
						<strong>🙂 Okay</strong>
					</div>

					<div>
						<span>14 Aug</span>
						<strong>😊 Good</strong>
					</div>

					<div>
						<span>13 Aug</span>
						<strong>😊 Good</strong>
					</div>

				</div>


				<button
					class="text-button mood-link"
					onclick={openCalls}
				>
					View wellbeing history
					<span>→</span>
				</button>

			</article>

		</section>


		<!-- =================================================
		     BOTTOM SENIOR CONTACT
		================================================= -->

		<section class="contact-card">

			<div>

				<div class="contact-heart">
					♥
				</div>

				<div>

					<p class="eyebrow">
						ONE TAP AWAY
					</p>

					<h2>
						Want to hear {senior.firstName}'s voice?
					</h2>

					<p>
						Call directly without searching for
						their number.
					</p>

				</div>

			</div>


			<div class="contact-actions">

				<button
					class="profile-button"
					onclick={openSenior}
				>
					View profile
				</button>


				<a
					href={`tel:${senior.phone}`}
					class="big-call-button"
				>
					<span>☎</span>

					<div>
						<small>CALL NOW</small>
						<strong>{senior.firstName}</strong>
					</div>

				</a>

			</div>

		</section>


		<p class="closing">
			♡ Vcare stays with them, so you can stay close without worrying every minute.
		</p>

	</main>

</div>


<style>

	:global(*) {
		box-sizing: border-box;
	}

	:global(html),
	:global(body) {
		margin: 0;
		min-height: 100%;
	}

	:global(body) {
		background: #f7f0e2;

		color: #173f31;

		font-family:
			"Comic Sans MS",
			"Comic Sans",
			"Chalkboard SE",
			"Marker Felt",
			cursive;
	}

	button,
	a {
		font-family: inherit;
	}


	/* =====================================================
	   APP
	===================================================== */

	.app {
		min-height: 100vh;

		display: grid;

		grid-template-columns:
			245px 1fr;

		background:
			radial-gradient(
				circle at 100% 0%,
				rgba(223, 231, 93, 0.12),
				transparent 25%
			),
			#f7f0e2;
	}


	/* =====================================================
	   SIDEBAR
	===================================================== */

	.sidebar {
		position: sticky;

		top: 0;

		height: 100vh;

		padding:
			28px 18px
			22px;

		display: flex;

		flex-direction: column;

		background:
			linear-gradient(
				180deg,
				#073e2c,
				#07563a
			);

		color: white;

		border-right:
			1px solid
			rgba(255,255,255,0.08);
	}


	.brand {
		display: flex;

		align-items: center;

		gap: 11px;

		padding:
			0 8px;

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


	.brand > div:last-child {
		display: flex;

		flex-direction: column;
	}


	.brand strong {
		font-size: 19px;
	}


	.brand span {
		margin-top: 2px;

		color:
			rgba(255,255,255,0.65);

		font-size: 8px;
	}


	.care-label {
		margin:
			35px 10px
			13px;

		color: #dce765;

		font-size: 9px;

		font-weight: bold;

		letter-spacing: 1.4px;
	}


	nav {
		display: grid;

		gap: 6px;
	}


	.nav-item {
		min-height: 47px;

		padding:
			0 13px;

		display: flex;

		align-items: center;

		gap: 12px;

		border-radius: 13px;

		text-decoration: none;

		color:
			rgba(255,255,255,0.68);

		font-size: 12px;

		font-weight: bold;

		transition:
			0.18s ease;
	}


	.nav-item:hover {
		color: white;

		background:
			rgba(255,255,255,0.07);

		transform:
			translateX(3px);
	}


	.nav-item.active {
		color: #143d2e;

		background: #dce76a;
	}


	.nav-icon {
		width: 26px;

		font-size: 17px;

		text-align: center;
	}


	.sidebar-bottom {
		margin-top: auto;
	}


	.mini-senior {
		margin-bottom: 13px;

		padding:
			11px;

		display: flex;

		align-items: center;

		gap: 10px;

		border:
			1px solid
			rgba(255,255,255,0.10);

		border-radius: 14px;

		background:
			rgba(255,255,255,0.06);

		text-decoration: none;

		color: inherit;

		transition: 0.2s ease;
	}

	.mini-senior:hover {
		background: rgba(255,255,255,0.12);
	}


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


	.mini-senior > div:last-child {
		min-width: 0;

		display: flex;

		flex-direction: column;
	}


	.mini-senior small {
		color:
			rgba(255,255,255,0.5);

		font-size: 6px;

		letter-spacing: 1px;
	}


	.mini-senior strong {
		margin-top: 2px;

		overflow: hidden;

		color: white;

		font-size: 10px;

		text-overflow: ellipsis;

		white-space: nowrap;
	}


	.profile {
		padding:
			13px 8px 0;

		display: flex;

		align-items: center;

		gap: 9px;

		border-top:
			1px solid
			rgba(255,255,255,0.10);
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


	.profile-copy {
		min-width: 0;

		display: flex;

		flex: 1;

		flex-direction: column;
	}


	.profile-copy strong {
		overflow: hidden;

		font-size: 10px;

		text-overflow: ellipsis;

		white-space: nowrap;
	}


	.profile-copy span {
		margin-top: 2px;

		color:
			rgba(255,255,255,0.53);

		font-size: 7px;
	}


	.logout {
		border: 0;

		background: transparent;

		color:
			rgba(255,255,255,0.7);

		cursor: pointer;

		font-size: 15px;
	}


	/* =====================================================
	   MAIN
	===================================================== */

	.main {
		width: 100%;

		max-width: 1500px;

		margin: 0 auto;

		padding:
			34px
			clamp(30px, 4vw, 65px)
			45px;
	}


	/* =====================================================
	   TOP
	===================================================== */

	.topbar {
		display: flex;

		align-items: flex-start;

		justify-content: space-between;

		gap: 30px;

		margin-bottom: 26px;
	}


	.date {
		margin:
			0 0 5px;

		color: #85745f;

		font-size: 10px;

		font-weight: bold;

		text-transform: uppercase;

		letter-spacing: 1px;
	}


	.topbar h1 {
		margin: 0;

		color: #154a35;

		font-size:
			clamp(34px, 4vw, 51px);

		line-height: 1;

		letter-spacing: -2px;
	}


	.intro {
		margin:
			9px 0 0;

		color: #756653;

		font-size: 12px;
	}


	.live-time {
		padding:
			10px 14px;

		display: flex;

		align-items: center;

		gap: 9px;

		border:
			1px solid #ddd1b6;

		border-radius: 14px;

		background:
			rgba(255,255,255,0.42);
	}


	.live-dot {
		width: 8px;
		height: 8px;

		border-radius: 50%;

		background: #2c9a59;

		box-shadow:
			0 0 0 4px
			rgba(44,154,89,0.11);

		animation:
			pulse 2s infinite;
	}


	@keyframes pulse {

		50% {
			box-shadow:
				0 0 0 7px
				rgba(44,154,89,0.04);
		}

	}


	.live-time div {
		display: flex;

		flex-direction: column;
	}


	.live-time small {
		color: #2c7a4c;

		font-size: 6px;

		font-weight: bold;

		letter-spacing: 1px;
	}


	.live-time strong {
		margin-top: 1px;

		color: #4c4439;

		font-size: 10px;
	}


	/* =====================================================
	   SENIOR CARD
	===================================================== */

	.senior-card {
		margin-bottom: 20px;

		padding:
			22px 24px;

		display: flex;

		align-items: center;

		justify-content: space-between;

		gap: 25px;

		border:
			1px solid #d9d5a9;

		border-radius: 22px;

		background:
			linear-gradient(
				110deg,
				#f1f2cb,
				#f8edcf
			);

		box-shadow:
			0 12px 30px
			rgba(62,72,38,0.05);
	}


	.senior-main {
		display: flex;

		align-items: center;

		gap: 17px;
	}


	.senior-avatar {
		width: 66px;
		height: 66px;

		display: grid;

		place-items: center;

		flex-shrink: 0;

		border-radius: 20px;

		background:
			linear-gradient(
				145deg,
				#176943,
				#379259
			);

		color: white;

		font-size: 18px;

		font-weight: bold;

		box-shadow:
			0 9px 20px
			rgba(24,104,67,0.15);
	}


	.eyebrow {
		margin:
			0 0 5px;

		color: #57843d;

		font-size: 8px;

		font-weight: 900;

		letter-spacing: 1.2px;
	}


	.orange {
		color: #a86438;
	}


	.senior-name-row {
		display: flex;

		align-items: center;

		flex-wrap: wrap;

		gap: 11px;
	}


	.senior-name-row h2 {
		margin: 0;

		color: #174a35;

		font-size: 24px;
	}


	.status-pill {
		padding:
			5px 9px;

		display: flex;

		align-items: center;

		gap: 5px;

		border-radius: 30px;

		background: #dbe8ae;

		color: #3d6939;

		font-size: 8px;

		font-weight: bold;
	}


	.status-pill > span {
		width: 6px;
		height: 6px;

		border-radius: 50%;

		background: #409652;
	}


	.checkin {
		margin:
			6px 0 0;

		color: #746854;

		font-size: 9px;
	}


	.senior-actions {
		display: flex;

		align-items: center;

		gap: 14px;
	}


	.mood-small {
		padding-right: 15px;

		display: flex;

		align-items: center;

		gap: 8px;

		border-right:
			1px solid #d5ca9d;
	}


	.mood-emoji {
		font-size: 28px;
	}


	.mood-small div {
		display: flex;

		flex-direction: column;
	}


	.mood-small small {
		color: #887d66;

		font-size: 6px;

		font-weight: bold;
	}


	.mood-small strong {
		color: #315a3c;

		font-size: 10px;
	}


	.call-button {
		min-height: 45px;

		padding:
			0 17px;

		display: flex;

		align-items: center;

		gap: 8px;

		border-radius: 13px;

		background: #176a43;

		color: white;

		text-decoration: none;

		font-size: 10px;

		font-weight: bold;

		box-shadow:
			0 9px 20px
			rgba(23,106,67,0.16);

		transition:
			0.18s ease;
	}


	.call-button:hover {
		transform:
			translateY(-2px);

		background: #105a37;
	}


	.call-button span {
		font-size: 15px;
	}


	/* =====================================================
	   GRID
	===================================================== */

	.dashboard-grid {
		display: grid;

		grid-template-columns:
			minmax(0, 1.35fr)
			minmax(270px, 0.65fr);

		gap: 18px;
	}


	.panel {
		padding: 21px;

		border:
			1px solid #ded3b9;

		border-radius: 21px;

		background:
			rgba(255,250,239,0.76);

		box-shadow:
			0 10px 28px
			rgba(91,67,33,0.045);
	}


	.panel-header {
		display: flex;

		align-items: flex-start;

		justify-content: space-between;

		gap: 15px;

		margin-bottom: 17px;
	}


	.panel-header.compact {
		margin-bottom: 14px;
	}


	.panel-header h2,
	.mood-panel h2 {
		margin: 0;

		color: #184a36;

		font-size: 18px;

		line-height: 1.2;
	}


	.panel-subtitle {
		display: block;

		margin-top: 4px;

		color: #8a7963;

		font-size: 8px;
	}


	.medicine-icon,
	.call-icon,
	.alert-icon {
		width: 39px;
		height: 39px;

		display: grid;

		place-items: center;

		flex-shrink: 0;

		border-radius: 12px;

		font-size: 16px;

		font-weight: bold;
	}


	.medicine-icon {
		background: #e7ebbd;

		color: #4f7a3e;
	}


	.call-icon {
		background: #dce9d6;

		color: #287149;
	}


	.alert-icon {
		background: #f7dfbc;

		color: #a45c35;
	}


	/* =====================================================
	   MEDICINES
	===================================================== */

	.medicine-list {
		display: grid;

		gap: 8px;
	}


	.medicine-row {
		min-height: 59px;

		padding:
			9px 11px;

		display: flex;

		align-items: center;

		gap: 11px;

		border:
			1px solid #e3d8c0;

		border-radius: 14px;

		background:
			rgba(255,255,255,0.40);
	}


	.medicine-check {
		width: 34px;
		height: 34px;

		display: grid;

		place-items: center;

		flex-shrink: 0;

		border-radius: 11px;

		background: #f3e8d2;

		color: #9b7d5b;

		font-size: 13px;

		font-weight: bold;
	}


	.medicine-check.taken {
		background: #dce8b6;

		color: #4b7c40;
	}


	.medicine-info {
		min-width: 0;

		display: flex;

		flex: 1;

		flex-direction: column;
	}


	.medicine-info strong {
		color: #3b4d3e;

		font-size: 10px;
	}


	.medicine-info span {
		margin-top: 3px;

		color: #887764;

		font-size: 7px;
	}


	.medicine-status {
		padding:
			5px 8px;

		border-radius: 20px;

		font-size: 7px;

		font-weight: bold;
	}


	.medicine-status.taken {
		background: #e3edc6;

		color: #4a753f;
	}


	.medicine-status.pending {
		background: #f5e5bf;

		color: #956333;
	}


	.panel-actions {
		margin-top: 14px;

		display: flex;

		align-items: center;

		justify-content: space-between;

		gap: 12px;
	}


	.add-button {
		min-height: 38px;

		padding:
			0 13px;

		border: 0;

		border-radius: 11px;

		background: #176b44;

		color: white;

		cursor: pointer;

		font-size: 8px;

		font-weight: bold;
	}


	.add-button span {
		margin-right: 4px;

		font-size: 12px;
	}


	.text-button {
		padding: 5px;

		border: 0;

		background: transparent;

		color: #39724d;

		cursor: pointer;

		font-size: 8px;

		font-weight: bold;
	}


	.text-button span {
		margin-left: 5px;
	}


	/* =====================================================
	   ALERT
	===================================================== */

	.alerts {
		display: grid;

		gap: 8px;
	}


	.alert {
		padding:
			12px;

		display: flex;

		align-items: flex-start;

		gap: 10px;

		border:
			1px solid #eccfa8;

		border-radius: 14px;

		background: #fbebd2;
	}


	.alert-symbol {
		width: 28px;
		height: 28px;

		display: grid;

		place-items: center;

		flex-shrink: 0;

		border-radius: 9px;

		background: #eaa36e;

		color: white;

		font-size: 11px;

		font-weight: bold;
	}


	.alert strong {
		color: #7a4d31;

		font-size: 9px;
	}


	.alert p {
		margin:
			4px 0 0;

		color: #8d6d58;

		font-size: 7px;

		line-height: 1.45;
	}


	.all-good {
		padding: 14px;

		display: flex;

		gap: 10px;

		align-items: center;

		border-radius: 14px;

		background: #e8efc9;
	}


	.all-good > div {
		width: 31px;
		height: 31px;

		display: grid;

		place-items: center;

		border-radius: 50%;

		background: #6f9b4b;

		color: white;
	}


	.all-good strong {
		font-size: 9px;
	}


	.all-good p {
		margin:
			3px 0 0;

		color: #68715d;

		font-size: 7px;
	}


	.care-note {
		margin-top: 13px;

		padding-top: 12px;

		display: flex;

		gap: 8px;

		border-top:
			1px dashed #d9c9ac;
	}


	.care-note span {
		color: #719443;

		font-size: 14px;
	}


	.care-note p {
		margin: 0;

		color: #8a7861;

		font-size: 7px;

		line-height: 1.5;
	}


	/* =====================================================
	   CALL PANEL
	===================================================== */

	.call-summary {
		padding: 14px;

		border:
			1px solid #d9d9b5;

		border-radius: 15px;

		background:
			linear-gradient(
				120deg,
				#f1f1cf,
				#faf0d9
			);
	}


	.call-top {
		display: flex;

		align-items: flex-start;

		justify-content: space-between;

		gap: 10px;
	}


	.call-top > div {
		display: flex;

		flex-direction: column;
	}


	.call-top strong {
		color: #365641;

		font-size: 10px;
	}


	.call-top span {
		margin-top: 2px;

		color: #88765f;

		font-size: 7px;
	}


	.completed {
		padding:
			4px 7px;

		border-radius: 20px;

		background: #dce9b8;

		color: #4b783e !important;

		font-size: 7px !important;

		font-weight: bold;
	}


	.call-tags {
		margin-top: 11px;

		display: flex;

		flex-wrap: wrap;

		gap: 6px;
	}


	.call-tags span {
		padding:
			5px 7px;

		border-radius: 8px;

		background:
			rgba(255,255,255,0.60);

		color: #627056;

		font-size: 7px;
	}


	.summary-text {
		margin:
			11px 0 0;

		color: #685d50;

		font-size: 8px;

		line-height: 1.55;
	}


	.wide-button {
		width: 100%;

		margin-top: 13px;

		padding:
			10px 12px;

		display: flex;

		align-items: center;

		justify-content: space-between;

		border:
			1px solid #d5c8aa;

		border-radius: 11px;

		background: transparent;

		color: #3d704e;

		cursor: pointer;

		font-size: 8px;

		font-weight: bold;
	}


	/* =====================================================
	   MOOD
	===================================================== */

	.current-mood {
		margin-top: 17px;

		padding: 14px;

		display: flex;

		align-items: center;

		gap: 11px;

		border-radius: 15px;

		background:
			linear-gradient(
				120deg,
				#e8efc5,
				#f5edcd
			);
	}


	.big-emoji {
		width: 48px;
		height: 48px;

		display: grid;

		place-items: center;

		border-radius: 14px;

		background:
			rgba(255,255,255,0.65);

		font-size: 28px;
	}


	.current-mood > div:last-child {
		display: flex;

		flex-direction: column;
	}


	.current-mood small {
		color: #829063;

		font-size: 6px;

		font-weight: bold;
	}


	.current-mood strong {
		color: #365e3f;

		font-size: 13px;
	}


	.current-mood span {
		margin-top: 2px;

		color: #7c735f;

		font-size: 6px;
	}


	.mood-history {
		margin-top: 12px;

		display: grid;

		gap: 6px;
	}


	.mood-history > div {
		padding:
			7px 2px;

		display: flex;

		align-items: center;

		justify-content: space-between;

		border-bottom:
			1px dashed #dfd1b8;
	}


	.mood-history span {
		color: #8d7b66;

		font-size: 7px;
	}


	.mood-history strong {
		color: #4d664c;

		font-size: 8px;
	}


	.mood-link {
		margin-top: 10px;
	}


	/* =====================================================
	   CONTACT
	===================================================== */

	.contact-card {
		margin-top: 18px;

		padding:
			18px 21px;

		display: flex;

		align-items: center;

		justify-content: space-between;

		gap: 20px;

		border-radius: 20px;

		background:
			linear-gradient(
				120deg,
				#0c593b,
				#17754b
			);

		color: white;
	}


	.contact-card > div:first-child {
		display: flex;

		align-items: center;

		gap: 13px;
	}


	.contact-heart {
		width: 48px;
		height: 48px;

		display: grid;

		place-items: center;

		flex-shrink: 0;

		border-radius: 14px;

		background: #dce769;

		color: #174a34;

		font-size: 20px;
	}


	.contact-card .eyebrow {
		color: #dce769;
	}


	.contact-card h2 {
		margin: 0;

		color: white;

		font-size: 17px;
	}


	.contact-card p:not(.eyebrow) {
		margin:
			4px 0 0;

		color:
			rgba(255,255,255,0.66);

		font-size: 8px;
	}


	.contact-actions {
		display: flex;

		align-items: center;

		gap: 8px;
	}


	.profile-button {
		min-height: 43px;

		padding:
			0 13px;

		border:
			1px solid
			rgba(255,255,255,0.25);

		border-radius: 12px;

		background:
			rgba(255,255,255,0.08);

		color: white;

		cursor: pointer;

		font-size: 8px;

		font-weight: bold;
	}


	.big-call-button {
		min-height: 46px;

		padding:
			0 15px;

		display: flex;

		align-items: center;

		gap: 9px;

		border-radius: 13px;

		background: #dce769;

		color: #174832;

		text-decoration: none;

		transition:
			0.18s ease;
	}


	.big-call-button:hover {
		transform:
			translateY(-2px)
			scale(1.02);
	}


	.big-call-button > span {
		font-size: 18px;
	}


	.big-call-button > div {
		display: flex;

		flex-direction: column;
	}


	.big-call-button small {
		font-size: 5px;

		font-weight: bold;

		letter-spacing: 1px;
	}


	.big-call-button strong {
		font-size: 9px;
	}


	.closing {
		margin:
			17px 0 0;

		text-align: center;

		color: #897861;

		font-size: 8px;
	}


	/* =====================================================
	   RESPONSIVE
	===================================================== */

	@media (max-width: 1050px) {

		.app {
			grid-template-columns:
				205px 1fr;
		}


		.dashboard-grid {
			grid-template-columns: 1fr;
		}

	}


	@media (max-width: 760px) {

		.app {
			display: block;
		}


		.sidebar {
			position: relative;

			width: 100%;
			height: auto;

			padding:
				17px 15px;
		}


		.care-label,
		.mini-senior {
			display: none;
		}


		nav {
			margin-top: 15px;

			display: flex;

			overflow-x: auto;
		}


		.nav-item {
			flex-shrink: 0;
		}


		.sidebar-bottom {
			margin-top: 15px;
		}


		.profile {
			padding-top: 10px;
		}


		.main {
			padding:
				25px 15px
				40px;
		}


		.topbar {
			align-items: center;
		}


		.topbar h1 {
			font-size: 35px;
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

		.live-time {
			display: none;
		}


		.senior-actions {
			align-items: stretch;

			flex-direction: column;
		}


		.mood-small {
			padding:
				0 0 10px;

			border-right: 0;

			border-bottom:
				1px solid #d5ca9d;
		}


		.call-button {
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


		.big-call-button {
			justify-content: center;
		}

	}

</style>
