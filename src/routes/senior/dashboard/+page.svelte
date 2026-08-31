<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import { startSampleCall } from '$lib/senior/sampleCall';

	let senior = $state({
		firstName: 'User',
		fullName: '',
		phone: '',
		email: ''
	});

	let medicines = $state([]);
	let recentCalls = $state([]);
	let loadingMedicines = $state(true);
	let loadingCalls = $state(true);
	let medicinesError = $state('');
	let callsError = $state('');
	let mood = $state('good');

	let reminders = $state([
		{
			id: 1,
			time: '11:00 AM',
			title: 'Morning walk',
			category: 'routine',
			icon: '🚶',
			status: 'done'
		},
		{
			id: 2,
			time: '3:30 PM',
			title: 'Doctor appointment',
			category: 'appointment',
			icon: '🩺',
			status: 'upcoming'
		},
		{
			id: 3,
			time: '5:30 PM',
			title: 'Singing practice',
			category: 'routine',
			icon: '🎵',
			status: 'upcoming'
		}
	]);

	let caregivers = $state([]);

	let sampleCallMessage = $state('');
	let isCalling = $state(false);
	let seniorPhone = $state('');
	let userId = $state('');
	let pendingMedicine = $state(null);

	onMount(async () => {
		const {
			data: { session }
		} = await supabase.auth.getSession();

		const {
			data: { user }
		} = await supabase.auth.getUser();

		if (!user) {
			goto('/auth?role=senior');
			return;
		}
		userId = user.id;
		senior.email = user.email || '';

		const { data: profile, error: profileError } = await supabase
			.from('profiles')
			.select('full_name, phone, emergency_contact_name, emergency_contact_phone, emergency_contact_relationship')
			.eq('id', user.id)
			.single();

		if (profileError) {
			console.error('Profile fetch error:', profileError);
		}

		if (profile) {
			senior.fullName =
				profile.full_name ||
				user.user_metadata?.full_name ||
				user.user_metadata?.name ||
				'User';

			senior.firstName =
				senior.fullName.split(' ')[0];

			seniorPhone = profile.phone || '';
			senior.phone = profile.phone || '';

			// Load real Care Circle
			const loadedCaregivers = [];
			if (profile.emergency_contact_name) {
				loadedCaregivers.push({
					id: 'primary',
					name: profile.emergency_contact_name,
					relation: profile.emergency_contact_relationship || 'Emergency Contact',
					phone: profile.emergency_contact_phone || '',
					initial: profile.emergency_contact_name.charAt(0).toUpperCase(),
					primary: true
				});
			}

			try {
				const { data: links } = await supabase
					.from('caregiver_links')
					.select('caregiver_id')
					.eq('senior_id', user.id);

				if (links && links.length > 0) {
					for (const link of links) {
						const { data: cgProfile } = await supabase
							.from('profiles')
							.select('id, full_name, phone, emergency_contact_relationship')
							.eq('id', link.caregiver_id)
							.maybeSingle();

						if (cgProfile && !loadedCaregivers.some(c => c.name === cgProfile.full_name)) {
							loadedCaregivers.push({
								id: cgProfile.id,
								name: cgProfile.full_name || 'Caregiver',
								relation: 'Linked Caregiver',
								phone: cgProfile.phone || '',
								initial: (cgProfile.full_name || 'C').charAt(0).toUpperCase(),
								primary: loadedCaregivers.length === 0
							});
						}
					}
				}
			} catch (e) {
				console.warn('Could not load extra caregiver links:', e);
			}

			caregivers = loadedCaregivers;
		}

		// Load medicines
		loadingMedicines = true;
		medicinesError = '';
		try {
			const { data: medData, error: medError } = await supabase
				.from('medications')
				.select('id, name, dosage, scheduled_time, taken')
				.eq('senior_id', user.id)
				.order('scheduled_time', { ascending: true });

			if (medError) {
				medicinesError = 'Failed to load medications';
				console.error('Medications error:', medError);
			} else if (medData) {
				medicines = medData.map(m => ({
					id: m.id,
					name: m.name,
					dosage: m.dosage,
					time: m.scheduled_time,
					status: m.taken ? 'taken' : 'pending'
				}));
				pendingMedicine = medicines.find(m => m.status === 'pending') || null;
			}
		} catch (error) {
			medicinesError = 'Error loading medications';
			console.error('Medications exception:', error);
		} finally {
			loadingMedicines = false;
		}

		// Subscribe to real-time medication updates
		const medicationSubscription = supabase
			.channel(`medications:${user.id}`)
			.on(
				'postgres_changes',
				{
					event: '*',
					schema: 'public',
					table: 'medications',
					filter: `senior_id=eq.${user.id}`
				},
				(payload) => {
					if (payload.eventType === 'UPDATE') {
						const updated = payload.new;
						medicines = medicines.map(m =>
							m.id === updated.id
								? { ...m, status: updated.taken ? 'taken' : 'pending' }
								: m
						);
						pendingMedicine = medicines.find(m => m.status === 'pending') || null;
					} else if (payload.eventType === 'INSERT') {
						const newMed = payload.new;
						medicines = [...medicines, {
							id: newMed.id,
							name: newMed.name,
							dosage: newMed.dosage,
							time: newMed.scheduled_time,
							status: newMed.taken ? 'taken' : 'pending'
						}].sort((a, b) => a.time.localeCompare(b.time));
						pendingMedicine = medicines.find(m => m.status === 'pending') || null;
					}
				}
			)
			.subscribe();

		// Fetch call history from backend
		loadingCalls = true;
		callsError = '';
		try {
			if (session?.access_token && PUBLIC_BACKEND_URL) {
				const callResponse = await fetch(`${PUBLIC_BACKEND_URL}/calls/${user.id}`, {
					headers: {
						'Authorization': `Bearer ${session.access_token}`,
						'Content-Type': 'application/json'
					}
				});

				if (callResponse.ok) {
					const callData = await callResponse.json();
					recentCalls = callData.map(call => ({
						id: call.id,
						date: new Date(call.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
						time: new Date(call.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
						status: call.status,
						duration: call.duration ? `${call.duration}s` : '35s',
						mood: call.distress_detected ? 'Needs Care' : 'Good',
						summary: call.transcript ? (call.transcript.substring(0, 100) + '...') : 'Call completed'
					}));
				}
			}
		} catch (error) {
			callsError = 'Failed to load call history';
			console.error('Failed to fetch call history:', error);
		} finally {
			loadingCalls = false;
		}

		return () => {
			medicationSubscription.unsubscribe();
		};
	});

	function setMood(value) {
		mood = value;
	}

	async function markMedicineTaken(id) {
		medicines = medicines.map((medicine) =>
			medicine.id === id
				? { ...medicine, status: 'taken' }
				: medicine
		);
		pendingMedicine = medicines.find(m => m.status === 'pending') || null;

		try {
			const { data: { session } } = await supabase.auth.getSession();
			const token = session?.access_token;

			let updated = false;
			if (PUBLIC_BACKEND_URL && token) {
				try {
					const res = await fetch(`${PUBLIC_BACKEND_URL}/medications/${id}`, {
						method: 'PUT',
						headers: {
							'Authorization': `Bearer ${token}`,
							'Content-Type': 'application/json'
						},
						body: JSON.stringify({
							taken: true,
							taken_at: new Date().toISOString()
						})
					});
					if (res.ok) updated = true;
				} catch (e) {
					console.warn('Backend update failed:', e);
				}
			}

			if (!updated) {
				await supabase
					.from('medications')
					.update({
						taken: true,
						taken_at: new Date().toISOString()
					})
					.eq('id', id)
					.eq('senior_id', userId);
			}
		} catch (err) {
			console.error('Error marking medicine taken:', err);
		}
	}

	async function takeSampleCall() {
		isCalling = true;
		sampleCallMessage = 'Starting your Vcare check-in call...';

		try {
			await startSampleCall({
				phone: seniorPhone || senior.phone,
				firstName: senior.firstName,
				userId,
				pendingMedicine
			});
			sampleCallMessage = 'Vcare is calling you now.';
		} catch (error) {
			sampleCallMessage = error.message || 'Could not start the call. Please try again.';
		} finally {
			isCalling = false;
		}
	}

	// Computed alerts
	let alerts = $derived(
		medicines
			.filter(m => m.status === 'pending')
			.map((m, idx) => ({
				id: idx + 1,
				type: 'medicine',
				title: `${m.name} is scheduled for ${m.time}`,
				message: `Please remember to take your ${m.dosage}. Vcare will check in with you.`
			}))
	);
</script>


<svelte:head>
	<title>Home — Vcare.life</title>
	<meta
		name="description"
		content="Your personal Vcare companion dashboard"
	/>
</svelte:head>


<div class="app">
		<main class="content">


			<!-- ===================================================
			     GREETING
			     =================================================== -->

			<section class="welcome">

				<div>
					<p class="section-label">
						YOUR DAY WITH VCARE
					</p>

					<h1>
						Good morning,
						<span>{senior.firstName}!</span>
					</h1>

					<p>
						We're here to care for you,
						one little step at a time.
					</p>
				</div>


				<div class="welcome-badge" role="status" aria-label="Vcare status: You are all set">
					<span class="status-mark" aria-hidden="true">✓</span>

					<div>
						<small>Vcare status</small>
						<strong>You’re all set</strong>
					</div>
				</div>

			</section>



			<!-- ===================================================
			     NEXT VCARE CALL
			     =================================================== -->

			<section class="call-banner">


				<div class="call-phone">

					<div class="phone-top"></div>

					<div class="phone-display">
						<small>VCARE CALLING</small>

						<strong>Hello there!</strong>

						<span>♡</span>
					</div>

					<div class="phone-controls">
						<div class="answer">☎</div>
						<div class="center-button">•</div>
						<div class="decline">×</div>
					</div>

				</div>


				<div class="call-info">

					<p class="lime-label">
						YOUR NEXT VCARE CHECK-IN
					</p>

					<h2>
						Today at
						<span>6:00 PM</span>
					</h2>

					<p class="call-description">
						We'll call you for your daily check-in,
						talk about your medicines, how your day
						has been and anything you asked Vcare
						to remember.
					</p>


					<div class="call-chips">

						<span>
							♡ Daily check-in
						</span>

						<span>
							✚ Medicine
						</span>

						<span>
							◷ 2 reminders
						</span>

					</div>

				</div>


				<div class="call-countdown">

					<small>TIME REMAINING</small>

					<div class="countdown">
						<div>
							<strong>05</strong>
							<span>HRS</span>
						</div>

						<b>:</b>

						<div>
							<strong>42</strong>
							<span>MINS</span>
						</div>

						<b>:</b>

						<div>
							<strong>18</strong>
							<span>SECS</span>
						</div>
					</div>


					<div class="scheduled">
						<i></i>
						Scheduled
					</div>

				</div>

			</section>



			<!-- ===================================================
			     TOP GRID
			     =================================================== -->

			<section class="top-grid">


				<!-- MEDICATION -->

				<article class="panel medicines-panel">

					<div class="panel-header">

						<div>
							<p class="section-label">
								TODAY
							</p>

							<h2>Your medicines</h2>

							<span class="panel-subtitle">
								Stay on track with today's medication.
							</span>
						</div>


						<div class="panel-icon medicine-panel-icon">
							✚
						</div>

					</div>


					<div class="medicine-list">

						{#if medicines.length === 0}
							<div class="empty-inline-state">
								<p>No medicines scheduled for today.</p>
							</div>
						{:else}
							{#each medicines as medicine}

								<div
									class="medicine-row"
									class:completed={medicine.status === 'taken'}
								>

									<div class="medicine-time">
										<strong>
											{medicine.time.split(' ')[0]}
										</strong>

										<span>
											{medicine.time.split(' ')[1]}
										</span>
									</div>


									<div class="medicine-pill-icon">
										💊
									</div>


									<div class="medicine-content">

										<strong>
											{medicine.name}
										</strong>

										<span>
											{medicine.dosage}
										</span>

									</div>


									{#if medicine.status === 'taken'}

										<div class="status-complete">
											✓ Taken
										</div>

									{:else}

										<button
											class="medicine-action"
											onclick={() =>
												markMedicineTaken(medicine.id)}
										>
											I took this
										</button>

									{/if}

								</div>

							{/each}
						{/if}

					</div>


					<div class="panel-footer">

						<button class="plain-button" onclick={() => goto('/senior/medications')}>
							View medicines
							<span>→</span>
						</button>

						<button class="add-button" onclick={() => goto('/senior/medications')}>
							＋ Add medicine
						</button>

					</div>

				</article>



				<!-- MOOD -->

				<article class="panel mood-panel">

					<div class="panel-header">

						<div>
							<p class="section-label">
								A LITTLE CHECK-IN
							</p>

							<h2>
								How are you feeling today?
							</h2>

							<span class="panel-subtitle">
								Let Vcare know how you're doing.
							</span>
						</div>


						<div class="panel-icon mood-icon">
							♡
						</div>

					</div>


					<div class="moods">

						<button
							class:chosen={mood === 'good'}
							onclick={() => setMood('good')}
						>
							<span class="face green-face">
								☺
							</span>

							<strong>Good</strong>
						</button>


						<button
							class:chosen={mood === 'okay'}
							onclick={() => setMood('okay')}
						>
							<span class="face yellow-face">
								●
							</span>

							<strong>Okay</strong>
						</button>


						<button
							class:chosen={mood === 'low'}
							onclick={() => setMood('low')}
						>
							<span class="face red-face">
								☹
							</span>

							<strong>Not great</strong>
						</button>

					</div>


					<div class="mood-result">

						<div class="mood-result-icon">
							♥
						</div>

						<div>
							<strong>
								Today's check-in:
								{mood === 'good'
									? 'Good'
									: mood === 'okay'
										? 'Okay'
										: 'Not great'}
							</strong>

							<span>
								Vcare will remember this for your next call.
							</span>
						</div>

					</div>

				</article>

			</section>



			<!-- ===================================================
			     MIDDLE GRID
			     =================================================== -->

			<section class="middle-grid">


				<!-- TODAY -->

				<article class="panel routine-panel" id="routine-section">

					<div class="panel-header">

						<div>
							<p class="section-label">
								MY DAY
							</p>

							<h2>Today's routine</h2>

							<span class="panel-subtitle">
								Everything you've asked Vcare to remember.
							</span>
						</div>


						<button class="outline-button" onclick={() => goto('/senior/reminder')}>
							＋ Add reminder
						</button>

					</div>



					<div class="timeline">


						<!-- medicine items -->

						{#each medicines as med}
							<div class="timeline-row">

								<div class="timeline-time">
									<strong>{med.time.split(' ')[0]}</strong>
									<span>{med.time.split(' ')[1] || 'AM'}</span>
								</div>

								<div class="timeline-line">
									<i class:done-dot={med.status === 'taken'} class:future-dot={med.status !== 'taken'}></i>
								</div>

								<div class="timeline-icon medicine-bg">
									💊
								</div>

								<div class="timeline-content">
									<strong>{med.name}</strong>
									<span>{med.dosage}</span>
								</div>

								<div class="timeline-status" class:done={med.status === 'taken'} class:upcoming={med.status !== 'taken'}>
									{med.status === 'taken' ? '✓ Taken' : '• Upcoming'}
								</div>

							</div>
						{/each}

						{#each reminders as reminder}

							<div class="timeline-row">

								<div class="timeline-time">

									<strong>
										{reminder.time.split(' ')[0]}
									</strong>

									<span>
										{reminder.time.split(' ')[1]}
									</span>

								</div>


								<div class="timeline-line">
									<i
										class:done-dot={reminder.status === 'done'}
										class:future-dot={reminder.status !== 'done'}
									></i>
								</div>


								<div
									class="timeline-icon"
									class:walk-bg={reminder.category === 'routine'}
									class:doctor-bg={reminder.category === 'appointment'}
								>
									{reminder.icon}
								</div>


								<div class="timeline-content">

									<strong>
										{reminder.title}
									</strong>

									<span>
										{reminder.category === 'appointment'
											? 'Upcoming plan'
											: 'Daily reminder'}
									</span>

								</div>


								<div
									class="timeline-status"
									class:done={reminder.status === 'done'}
									class:upcoming={reminder.status === 'upcoming'}
								>

									{reminder.status === 'done'
										? '✓ Done'
										: '• Upcoming'}

								</div>

							</div>

						{/each}



						<!-- VCARE call -->

						<div class="timeline-row">

							<div class="timeline-time">
								<strong>6:00</strong>
								<span>PM</span>
							</div>

							<div class="timeline-line last">
								<i class="future-dot"></i>
							</div>

							<div class="timeline-icon vcare-bg">
								☎
							</div>

							<div class="timeline-content">
								<strong>Vcare Check-in</strong>
								<span>Daily companion call</span>
							</div>

							<div class="timeline-status upcoming">
								• Upcoming
							</div>

						</div>

					</div>


					<button class="wide-link" onclick={() => goto('/senior/reminder')}>
						View & edit all reminders
						<span>→</span>
					</button>

				</article>



				<!-- RECENT CALLS -->

				<article class="panel calls-panel" id="calls-section">

					<div class="panel-header">

						<div>
							<p class="section-label">
								YOUR CONVERSATIONS
							</p>

							<h2>Recent Vcare calls</h2>

							<span class="panel-subtitle">
								Your latest check-ins with Vcare.
							</span>
						</div>


						<button class="small-link" onclick={() => scrollToSection('calls-section')}>
							View all
						</button>

					</div>



					<div class="calls-list">

						{#if recentCalls.length === 0}
							<div class="empty-inline-state">
								<p>No check-in calls recorded yet. Vcare will call you daily to check in!</p>
							</div>
						{:else}
							{#each recentCalls as call}

								<div class="call-row">

									<div
										class="call-status-icon"
										class:missed-call={call.status === 'missed'}
									>
										☎
									</div>


									<div class="call-row-content">

										<div class="call-row-top">

											<div>
												<strong>
													{call.date},
													{call.time}
												</strong>

												<span>
													Daily Vcare check-in
												</span>
											</div>


											<span
												class="call-badge"
												class:missed-badge={call.status === 'missed'}
											>

												{call.status === 'completed'
													? 'Completed'
													: 'Missed'}

											</span>

										</div>


										<div class="call-summary">

											{#if call.status === 'completed'}

												<span>
													Duration:
													{call.duration}
												</span>

												<i>•</i>

												<span>
													Mood:
													{call.mood}
												</span>

											{/if}

										</div>


										<p>
											"{call.summary}"
										</p>

									</div>

								</div>

							{/each}
						{/if}

					</div>


					<button class="wide-link" onclick={takeSampleCall}>
						Take a sample call now
						<span>→</span>
					</button>

				</article>

			</section>



			<!-- ===================================================
			     LOWER GRID
			     =================================================== -->

			<section class="lower-grid">


				<!-- CARE CIRCLE -->

				<article class="panel care-panel" id="care-section">

					<div class="panel-header">

						<div>
							<p class="section-label">
								YOUR PEOPLE
							</p>

							<h2>Your Care Circle</h2>

							<span class="panel-subtitle">
								People you trust and want to keep close.
							</span>
						</div>


						<div class="panel-icon care-icon">
							♡
						</div>

					</div>


					<div class="caregiver-list">

						{#if caregivers.length === 0}
							<div class="empty-inline-state">
								<p>No contacts configured yet. Add your emergency contact in your profile.</p>
							</div>
						{:else}
							{#each caregivers as caregiver}

								<div class="caregiver-row">

									<div class="caregiver-avatar">
										{caregiver.initial}
									</div>


									<div class="caregiver-info">

										<div class="caregiver-name">

											<strong>
												{caregiver.name}
											</strong>

											{#if caregiver.primary}
												<span>
													Primary
												</span>
											{/if}

										</div>

										<p>
											{caregiver.relation}
										</p>

									</div>


									<a
										class="call-caregiver"
										href={`tel:${caregiver.phone}`}
										aria-label={`Call ${caregiver.name}`}
									>
										☎
									</a>

								</div>

							{/each}
						{/if}

					</div>


					<div class="care-note">
						<span>♡</span>

						<p>
							Vcare can keep your chosen people
							informed when something needs their attention.
						</p>
					</div>


					<button class="wide-link" onclick={() => profileOpen = true}>
						View profile & care circle
						<span>→</span>
					</button>

				</article>



				<!-- ALERTS -->

				<article class="panel alerts-panel" id="alerts-section">

					<div class="panel-header">

						<div>
							<p class="section-label">
								IMPORTANT
							</p>

							<h2>Things needing attention</h2>

							<span class="panel-subtitle">
								Only what matters right now.
							</span>
						</div>


						<div class="panel-icon alert-icon">
							!
						</div>

					</div>


					{#if alerts.length > 0}

						<div class="alerts-list">

							{#each alerts as alert}

								<div class="alert-card">

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
							<span>✓</span>

							<div>
								<strong>
									You're all caught up.
								</strong>

								<p>
									Nothing needs your attention right now.
								</p>
							</div>
						</div>

					{/if}

				</article>

			</section>



			<!-- ===================================================
			     FINAL MESSAGE
			     =================================================== -->

			<section class="closing-card">

				<div class="closing-heart">
					♡
				</div>


				<div>
					<h2>
						Vcare is here for you,
						every day.
					</h2>

					<p>
						We call. We listen. We remember.
					</p>
				</div>


				<div class="closing-decoration">
					<span>♡</span>
					<span>✦</span>
				</div>

			</section>

		</main>

	</div>



<style>

	/* =========================================================
	   GLOBAL
	   ========================================================= */

	:global(*) {
		box-sizing: border-box;
	}

	:global(html) {
		background: #f9f0e0;
	}

	:global(body) {
		margin: 0;

		background: #f9f0e0;
		color: #30291f;

		font-family:
			"Comic Sans MS",
			"Comic Sans",
			cursive;

		-webkit-font-smoothing: antialiased;
	}

	button,
	a {
		font-family: inherit;
	}

	button {
		cursor: pointer;
	}


	/* =========================================================
	   APP
	   ========================================================= */

	.app {
		min-height: 100vh;

		display: grid;
		grid-template-columns: 245px minmax(0, 1fr);

		background:
			radial-gradient(
				circle at 85% 3%,
				rgba(215, 231, 80, 0.12),
				transparent 28%
			),
			#f9f0e0;
	}


	/* =========================================================
	   SIDEBAR
	   ========================================================= */

	.sidebar {
		position: sticky;

		top: 0;

		height: 100vh;

		padding: 24px 18px;

		background: #fffaf0;

		border-right: 1px solid #e3d6bd;

		display: flex;
		flex-direction: column;

		z-index: 30;
	}


	.brand {
		display: flex;
		align-items: center;
		gap: 11px;

		padding: 0 5px 25px;
	}


	.logo {
		width: 46px;
		height: 46px;

		border-radius: 14px;

		background: #0d7249;
		color: white;

		display: grid;
		place-items: center;

		font-size: 22px;

		box-shadow:
			0 8px 18px rgba(13, 114, 73, 0.15);
	}


	.logo.small {
		width: 37px;
		height: 37px;

		border-radius: 11px;

		font-size: 17px;
	}


	.brand-copy {
		display: flex;
		flex-direction: column;
	}


	.brand-copy strong {
		color: #075a3c;

		font-size: 18px;
		line-height: 1;
	}


	.brand-copy span {
		margin-top: 5px;

		color: #786c5d;

		font-size: 9px;
	}


	.main-nav {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}


	.nav-link {
		width: 100%;

		border: none;
		border-radius: 15px;

		padding: 11px 13px;

		background: transparent;

		text-decoration: none;
		text-align: left;

		color: #51483c;

		display: flex;
		align-items: center;
		gap: 12px;

		transition:
			background 0.2s,
			transform 0.2s;
	}


	.nav-link:hover {
		background: #f3eedc;

		transform: translateX(2px);
	}


	.nav-link.active {
		background:
			linear-gradient(
				90deg,
				#ecf2c9,
				#f6f4dc
			);

		color: #166144;
	}


	.nav-icon {
		width: 30px;
		height: 30px;

		display: grid;
		place-items: center;

		font-size: 18px;
	}


	.nav-link div {
		display: flex;
		flex-direction: column;
	}


	.nav-link strong {
		font-size: 13px;
	}


	.nav-link small {
		margin-top: 3px;

		color: #8e8170;

		font-size: 8px;
	}


	.sample-card {
		margin-top: auto;

		padding: 16px;

		border: 1px solid #e5d7bd;
		border-radius: 20px;

		background:
			linear-gradient(
				145deg,
				#fffdf5,
				#f5f3df
			);
	}


	.sample-phone {
		width: 42px;
		height: 70px;

		padding: 5px;

		margin-bottom: 12px;

		border: 3px solid #487d42;
		border-radius: 11px;

		background: #93b53c;
	}


	.sample-speaker {
		width: 14px;
		height: 3px;

		margin: auto;

		border-radius: 6px;

		background: #4d713a;
	}


	.sample-screen {
		height: 46px;

		margin-top: 4px;

		border: 2px solid #33643d;
		border-radius: 6px;

		background: #d8e94c;

		color: #22523a;

		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}


	.sample-screen span {
		font-size: 5px;
		font-weight: 900;
	}


	.sample-screen strong {
		font-size: 7px;
	}


	.sample-screen div {
		font-size: 10px;
	}


	.sample-copy p {
		margin: 0 0 5px;

		color: #2c7550;

		font-size: 8px;
		font-weight: bold;
		letter-spacing: 1px;
	}


	.sample-copy h3 {
		margin: 0;

		color: #2a4938;

		font-size: 15px;
	}


	.sample-copy span {
		display: block;

		margin-top: 5px;

		color: #766b5b;

		font-size: 9px;
		line-height: 1.4;
	}


	.sample-button {
		width: 100%;

		margin-top: 12px;
		padding: 10px;

		border: none;
		border-radius: 11px;

		background: #167749;
		color: white;

		font-weight: bold;
		font-size: 11px;
	}


	.sample-button:hover {
		background: #0e623b;
	}


	.sample-message {
		margin: 8px 0 0;

		color: #735f43;

		font-size: 8px;
		line-height: 1.4;
	}


	.sidebar-footer {
		padding: 18px 7px 2px;

		color: #8a7d69;

		display: flex;
		align-items: flex-start;
		gap: 7px;
	}


	.sidebar-footer p {
		margin: 0;

		font-size: 8px;
		line-height: 1.5;
	}



	/* =========================================================
	   MAIN
	   ========================================================= */

	.main-area {
		min-width: 0;
	}


	.topbar {
		height: 76px;

		padding: 0 4%;

		border-bottom: 1px solid #e1d4bb;

		background:
			rgba(255, 250, 240, 0.93);

		backdrop-filter: blur(12px);

		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 28px;

		position: sticky;
		top: 0;

		z-index: 20;
	}


	.mobile-logo {
		display: none;
	}


	.top-date {
		display: flex;
		align-items: center;
		gap: 9px;

		color: #4f463a;
	}


	.top-date > span {
		font-size: 18px;
	}


	.top-date div {
		display: flex;
		flex-direction: column;
	}


	.top-date small {
		font-size: 7px;
		letter-spacing: 1px;
		font-weight: bold;
		color: #8b7f6d;
	}


	.top-date strong {
		font-size: 11px;
	}


	.top-actions {
		display: flex;
		align-items: center;
		gap: 14px;
	}


	.help {
		padding: 8px 12px;

		border: 1px solid #dfd0b4;
		border-radius: 13px;

		background: #fffaf0;

		color: #52483a;

		font-size: 12px;
		font-weight: bold;

		display: flex;
		align-items: center;
		gap: 6px;
	}


	.profile {
		border: none;

		background: transparent;

		display: flex;
		align-items: center;
		gap: 9px;
	}


	.avatar {
		width: 39px;
		height: 39px;

		border-radius: 50%;

		background: #d5e64d;
		color: #23553c;

		display: grid;
		place-items: center;

		font-weight: bold;
	}


	.profile-name {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
	}


	.profile-name strong {
		font-size: 11px;
		color: #322c23;
	}


	.profile-name span {
		margin-top: 2px;

		font-size: 8px;
		color: #8a7d6c;
	}


	.dropdown-arrow {
		font-size: 13px;

		color: #736958;
	}

	/* PROFILE MENU */
	.profile-container {
		position: relative;
	}

	.profile-menu {
		position: absolute;
		top: calc(100% + 8px);
		right: 0;
		background: white;
		border: 1px solid #e2d4bc;
		border-radius: 16px;
		padding: 12px;
		min-width: 220px;
		box-shadow: 0 10px 30px rgba(0,0,0,0.12);
		z-index: 100;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.profile-menu-header {
		padding: 6px 10px 10px;
		border-bottom: 1px solid #f2e9dc;
		display: flex;
		flex-direction: column;
	}

	.profile-menu-header strong { font-size: 13px; color: #173f31; }
	.profile-menu-header small { font-size: 11px; color: #85745f; margin-top: 2px; }

	.menu-item {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 10px 12px;
		border-radius: 10px;
		border: none;
		background: transparent;
		color: #173f31;
		font-weight: bold;
		font-size: 12px;
		text-decoration: none;
		text-align: left;
		cursor: pointer;
		transition: 0.15s ease;
	}

	.menu-item:hover {
		background: #f4ecdc;
	}

	.menu-item.logout {
		color: #b81414;
		border-top: 1px solid #f2e9dc;
		margin-top: 4px;
		padding-top: 10px;
	}

	.menu-item.logout:hover {
		background: #fde8e8;
	}

	/* EMPTY INLINE STATE */
	.empty-inline-state {
		padding: 24px;
		text-align: center;
		color: #85745f;
		font-size: 13px;
	}

	/* HELP MODAL */
	.help-overlay {
		position: fixed;
		inset: 0;
		background: rgba(11, 45, 33, 0.6);
		backdrop-filter: blur(4px);
		display: grid;
		place-items: center;
		padding: 20px;
		z-index: 1000;
	}

	.help-card {
		background: white;
		width: 100%;
		max-width: 480px;
		border-radius: 24px;
		padding: 28px;
		box-shadow: 0 20px 40px rgba(0,0,0,0.2);
	}

	.help-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 20px;
	}

	.help-eyebrow { margin: 0; font-size: 10px; color: #85745f; letter-spacing: 1px; }
	.help-header h2 { margin: 4px 0 0; font-size: 20px; color: #0b3d2b; }

	.modal-close {
		background: transparent;
		border: none;
		font-size: 26px;
		color: #85745f;
		cursor: pointer;
	}

	.help-body {
		display: flex;
		flex-direction: column;
		gap: 16px;
		margin-bottom: 24px;
	}

	.help-item {
		display: flex;
		align-items: flex-start;
		gap: 14px;
	}

	.help-icon {
		width: 40px;
		height: 40px;
		border-radius: 12px;
		background: #f4ecdc;
		color: #0b6845;
		display: grid;
		place-items: center;
		font-size: 18px;
		flex-shrink: 0;
	}

	.help-item strong { display: block; font-size: 14px; color: #173f31; }
	.help-item p { margin: 3px 0 0; font-size: 12px; color: #695a47; line-height: 1.4; }

	.help-footer {
		display: flex;
		justify-content: flex-end;
	}

	.btn-help-close {
		background: #0b6845;
		color: white;
		border: none;
		padding: 12px 24px;
		border-radius: 12px;
		font-weight: bold;
		cursor: pointer;
	}


	.content {
		width: min(1230px, 94%);

		margin: auto;

		padding: 42px 0 60px;
	}



	/* =========================================================
	   WELCOME
	   ========================================================= */

	.welcome {
		margin-bottom: 28px;

		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: 30px;
	}


	.section-label {
		margin: 0 0 8px;

		color: #197349;

		font-size: 9px;
		font-weight: 900;
		letter-spacing: 1.4px;
	}


	.welcome h1 {
		margin: 0;

		color: #184936;

		font-size: clamp(38px, 4.4vw, 59px);
		line-height: 1;
		letter-spacing: -2px;
	}


	.welcome h1 span {
		color: #78a345;
	}


	.welcome > div:first-child > p:last-child {
		margin: 13px 0 0;

		color: #716454;

		font-size: 13px;
	}


	.welcome-badge {
		padding: 11px 16px 11px 11px;

		border: 1px solid #d8e5c8;
		border-radius: 999px;

		background: rgba(255, 255, 255, 0.88);

		display: flex;
		align-items: center;
		gap: 12px;
		box-shadow: 0 10px 28px rgba(28, 72, 52, 0.07);
	}


	.welcome-badge > .status-mark {
		width: 38px;
		height: 38px;
		flex: 0 0 38px;

		border-radius: 50%;

		background: #e2f0c5;
		color: #39713d;

		display: grid;
		place-items: center;
		font-size: 18px !important;
		font-weight: 800;
	}


	.welcome-badge div {
		display: flex;
		flex-direction: column;
	}


	.welcome-badge small {
		font-size: 13px !important;
		line-height: 1.15 !important;
		letter-spacing: 0.2px;

		color: #728075;
	}


	.welcome-badge strong {
		margin-top: 2px;

		font-size: 16px !important;
		line-height: 1.2 !important;

		color: #254c38;
	}



	/* =========================================================
	   CALL
	   ========================================================= */

	.call-banner {
		position: relative;
		overflow: hidden;

		min-height: 225px;

		padding: 30px 34px;

		border-radius: 28px;

		background:
			linear-gradient(
				110deg,
				#075f40,
				#08794c 60%,
				#086a45
			);

		color: white;

		display: grid;
		grid-template-columns: 110px 1fr 280px;
		align-items: center;
		gap: 28px;

		box-shadow:
			0 16px 35px rgba(11, 90, 58, 0.13);
	}


	.call-banner::before {
		content: "";

		position: absolute;

		width: 340px;
		height: 340px;

		right: -85px;
		top: -200px;

		border: 1px solid rgba(217, 231, 80, 0.19);
		border-radius: 50%;
	}


	.call-banner::after {
		content: "♡";

		position: absolute;

		right: 33%;
		top: 30px;

		color: rgba(216, 231, 80, 0.19);

		font-size: 52px;
	}


	.call-phone {
		position: relative;
		z-index: 2;

		width: 95px;
		height: 155px;

		padding: 12px 9px;

		border: 5px solid #688e32;
		border-radius: 22px;

		background: #a7ca3c;

		transform: rotate(-4deg);
	}


	.phone-top {
		width: 38px;
		height: 6px;

		margin: 0 auto 9px;

		border-radius: 10px;

		background: #587730;
	}


	.phone-display {
		height: 78px;

		border: 4px solid #35623a;
		border-radius: 11px;

		background: #ddeb50;
		color: #17442d;

		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}


	.phone-display small {
		font-size: 5px;
		font-weight: bold;
	}


	.phone-display strong {
		font-size: 10px;
		margin-top: 3px;
	}


	.phone-display span {
		font-size: 17px;
	}


	.phone-controls {
		margin-top: 9px;

		display: flex;
		align-items: center;
		justify-content: center;
		gap: 7px;
	}


	.phone-controls div {
		width: 19px;
		height: 19px;

		border-radius: 50%;

		display: grid;
		place-items: center;

		font-size: 7px;
	}


	.answer {
		background: #198b58;
	}


	.center-button {
		background: #f5efd8;

		color: #52713b;
	}


	.decline {
		background: #ea5e45;
	}


	.call-info {
		position: relative;
		z-index: 2;
	}


	.lime-label {
		margin: 0;

		color: #ddeb50;

		font-size: 9px;
		font-weight: bold;
		letter-spacing: 1.4px;
	}


	.call-info h2 {
		margin: 7px 0 0;

		font-size: clamp(26px, 3vw, 37px);

		line-height: 1.1;
	}


	.call-info h2 span {
		color: #ddeb50;
	}


	.call-description {
		max-width: 560px;

		margin: 12px 0 17px;

		color: rgba(255,255,255,.76);

		font-size: 11px;
		line-height: 1.55;
	}


	.call-chips {
		display: flex;
		flex-wrap: wrap;
		gap: 7px;
	}


	.call-chips span {
		padding: 7px 10px;

		border: 1px solid rgba(255,255,255,.16);
		border-radius: 20px;

		background: rgba(255,255,255,.08);

		font-size: 8px;
	}


	.call-countdown {
		position: relative;
		z-index: 2;

		padding-left: 28px;

		border-left:
			1px solid rgba(255,255,255,.17);
	}


	.call-countdown > small {
		color: #ddeb50;

		font-size: 7px;
		letter-spacing: 1.3px;
	}


	.countdown {
		margin-top: 8px;

		display: flex;
		align-items: flex-start;
		gap: 6px;
	}


	.countdown div {
		display: flex;
		flex-direction: column;
		align-items: center;
	}


	.countdown strong {
		font-size: 29px;
		line-height: 1;
	}


	.countdown span {
		margin-top: 4px;

		color: rgba(255,255,255,.62);

		font-size: 6px;
	}


	.countdown b {
		font-size: 20px;
		font-weight: normal;
	}


	.scheduled {
		width: fit-content;

		margin-top: 17px;
		padding: 7px 10px;

		border-radius: 20px;

		background: rgba(255,255,255,.1);

		font-size: 8px;

		display: flex;
		align-items: center;
		gap: 6px;
	}


	.scheduled i {
		width: 6px;
		height: 6px;

		border-radius: 50%;

		background: #ddeb50;
	}



	/* =========================================================
	   GRIDS
	   ========================================================= */

	.top-grid,
	.middle-grid,
	.lower-grid {
		margin-top: 20px;

		display: grid;
		gap: 20px;
	}


	.top-grid {
		grid-template-columns: 1.15fr .85fr;
	}


	.middle-grid {
		grid-template-columns: 1.08fr .92fr;
	}


	.lower-grid {
		grid-template-columns: 1fr 1fr;
	}



	/* =========================================================
	   PANELS
	   ========================================================= */

	.panel {
		padding: 26px;

		border: 1px solid #e0d1b4;
		border-radius: 24px;

		background: rgba(255,250,240,.94);

		box-shadow:
			0 7px 25px rgba(67, 52, 29, 0.035);
	}


	.panel-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 20px;
	}


	.panel-header h2 {
		margin: 0;

		color: #284438;

		font-size: 20px;
	}


	.panel-subtitle {
		display: block;

		margin-top: 6px;

		color: #827562;

		font-size: 9px;
	}


	.panel-icon {
		width: 43px;
		height: 43px;

		border-radius: 13px;

		display: grid;
		place-items: center;

		font-size: 18px;
	}


	.medicine-panel-icon {
		background: #eaf0be;
		color: #55793a;
	}


	.mood-icon {
		background: #f5e0d2;
		color: #ac6e4c;
	}


	.care-icon {
		background: #edf1c4;
		color: #4f7838;
	}


	.alert-icon {
		background: #f8dfd3;
		color: #bd5940;

		font-weight: bold;
	}



	/* =========================================================
	   MEDICINES
	   ========================================================= */

	.medicine-list {
		margin-top: 18px;
	}


	.medicine-row {
		min-height: 72px;

		border-top: 1px solid #eadfc9;

		display: grid;
		grid-template-columns: 59px 36px 1fr auto;
		align-items: center;
		gap: 11px;
	}


	.medicine-row:last-child {
		border-bottom: 1px solid #eadfc9;
	}


	.medicine-row.completed {
		opacity: .72;
	}


	.medicine-time {
		display: flex;
		flex-direction: column;

		color: #276247;
	}


	.medicine-time strong {
		font-size: 12px;
	}


	.medicine-time span {
		font-size: 7px;
	}


	.medicine-pill-icon {
		width: 31px;
		height: 31px;

		border-radius: 10px;

		background: #eef2cf;

		display: grid;
		place-items: center;

		font-size: 13px;
	}


	.medicine-content {
		display: flex;
		flex-direction: column;
	}


	.medicine-content strong {
		font-size: 11px;
	}


	.medicine-content span {
		margin-top: 4px;

		color: #8a7d68;

		font-size: 8px;
	}


	.medicine-action {
		padding: 8px 11px;

		border: 1px solid #85a45c;
		border-radius: 10px;

		background: #f5f6dc;
		color: #315e41;

		font-size: 8px;
		font-weight: bold;
	}


	.status-complete {
		color: #4e7d45;

		font-size: 8px;
		font-weight: bold;
	}


	.panel-footer {
		margin-top: 16px;

		display: flex;
		justify-content: space-between;
		align-items: center;
	}


	.plain-button,
	.small-link {
		border: none;

		background: none;

		color: #187049;

		font-size: 9px;
		font-weight: bold;
	}


	.plain-button span {
		margin-left: 5px;
	}


	.add-button,
	.outline-button {
		padding: 9px 11px;

		border: 1px solid #85a65e;
		border-radius: 10px;

		background: #fffdf6;
		color: #315e41;

		font-size: 8px;
		font-weight: bold;
	}



	/* =========================================================
	   MOOD
	   ========================================================= */

	.moods {
		margin-top: 22px;

		display: grid;
		grid-template-columns: repeat(3,1fr);
		gap: 10px;
	}


	.moods button {
		min-height: 98px;

		border: 1px solid #e2d3b7;
		border-radius: 17px;

		background: #fffdf7;

		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 8px;

		transition: .2s;
	}


	.moods button:hover {
		transform: translateY(-2px);
	}


	.moods button.chosen {
		border-color: #8fab66;

		background: #f4f7df;

		box-shadow:
			0 0 0 2px rgba(118,157,71,.07);
	}


	.face {
		width: 39px;
		height: 39px;

		border-radius: 50%;

		display: grid;
		place-items: center;

		font-size: 23px;
	}


	.green-face {
		background: #dff0c8;
		color: #4a863e;
	}


	.yellow-face {
		background: #f8edbf;
		color: #ad8834;
	}


	.red-face {
		background: #f6d8cd;
		color: #b75c4b;
	}


	.moods strong {
		color: #4a4237;

		font-size: 9px;
	}


	.mood-result {
		margin-top: 15px;
		padding: 14px;

		border-radius: 16px;

		background: #eef3d5;

		display: flex;
		align-items: center;
		gap: 11px;
	}


	.mood-result-icon {
		width: 34px;
		height: 34px;

		border-radius: 11px;

		background: #dbe75d;
		color: #3a683f;

		display: grid;
		place-items: center;
	}


	.mood-result > div:last-child {
		display: flex;
		flex-direction: column;
	}


	.mood-result strong {
		color: #416343;

		font-size: 10px;
	}


	.mood-result span {
		margin-top: 3px;

		color: #7a755d;

		font-size: 7px;
	}



	/* =========================================================
	   TIMELINE
	   ========================================================= */

	.timeline {
		margin-top: 20px;
	}


	.timeline-row {
		min-height: 67px;

		display: grid;
		grid-template-columns: 55px 18px 39px 1fr auto;
		align-items: center;
		gap: 9px;
	}


	.timeline-time {
		display: flex;
		flex-direction: column;

		color: #235f43;
	}


	.timeline-time strong {
		font-size: 11px;
	}


	.timeline-time span {
		font-size: 7px;
	}


	.timeline-line {
		height: 100%;

		position: relative;

		display: flex;
		justify-content: center;
	}


	.timeline-line::before {
		content: "";

		position: absolute;

		top: 0;
		bottom: 0;

		width: 1px;

		background: #ddd3bd;
	}


	.timeline-line.last::before {
		bottom: 50%;
	}


	.timeline-line i {
		width: 8px;
		height: 8px;

		position: relative;
		top: 50%;

		border-radius: 50%;

		transform: translateY(-50%);

		z-index: 2;
	}


	.done-dot {
		background: #6d9d51;

		box-shadow:
			0 0 0 3px #edf3d7;
	}


	.future-dot {
		background: #d0b56c;

		box-shadow:
			0 0 0 3px #f5eedb;
	}


	.timeline-icon {
		width: 36px;
		height: 36px;

		border-radius: 12px;

		display: grid;
		place-items: center;

		font-size: 15px;
	}


	.medicine-bg {
		background: #e7f0d5;
	}


	.walk-bg {
		background: #f7e7bd;
	}


	.doctor-bg {
		background: #f5d8d2;
	}


	.vcare-bg {
		background: #dbebde;

		color: #24704b;
	}


	.timeline-content {
		display: flex;
		flex-direction: column;
	}


	.timeline-content strong {
		font-size: 10px;
	}


	.timeline-content span {
		margin-top: 4px;

		color: #887b68;

		font-size: 7px;
	}


	.timeline-status {
		font-size: 8px;
		font-weight: bold;
	}


	.timeline-status.done {
		color: #4f8548;
	}


	.timeline-status.upcoming {
		color: #b48427;
	}


	.wide-link {
		width: 100%;

		margin-top: 16px;
		padding: 12px 0 0;

		border: none;
		border-top: 1px solid #eadfc9;

		background: none;

		color: #176e48;

		font-size: 9px;
		font-weight: bold;

		display: flex;
		justify-content: center;
		gap: 8px;
	}



	/* =========================================================
	   CALL HISTORY
	   ========================================================= */

	.calls-list {
		margin-top: 17px;
	}


	.call-row {
		padding: 15px 0;

		border-top: 1px solid #eadfc9;

		display: flex;
		gap: 12px;
	}


	.call-row:last-child {
		border-bottom: 1px solid #eadfc9;
	}


	.call-status-icon {
		width: 39px;
		height: 39px;

		flex-shrink: 0;

		border-radius: 50%;

		background: #258153;
		color: white;

		display: grid;
		place-items: center;

		font-size: 13px;
	}


	.call-status-icon.missed-call {
		background: #e86f5c;
	}


	.call-row-content {
		min-width: 0;

		flex: 1;
	}


	.call-row-top {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 10px;
	}


	.call-row-top > div {
		display: flex;
		flex-direction: column;
	}


	.call-row-top strong {
		font-size: 10px;
	}


	.call-row-top > div > span {
		margin-top: 3px;

		color: #887b68;

		font-size: 7px;
	}


	.call-badge {
		padding: 5px 8px;

		border-radius: 8px;

		background: #e6efce;
		color: #477243;

		font-size: 7px;
	}


	.missed-badge {
		background: #fae1da;
		color: #a94d40;
	}


	.call-summary {
		margin-top: 7px;

		display: flex;
		align-items: center;
		gap: 5px;

		color: #796d5c;

		font-size: 7px;
	}


	.call-summary i {
		font-style: normal;
	}


	.call-row-content p {
		margin: 6px 0 0;

		color: #4f6755;

		font-size: 8px;
	}



	/* =========================================================
	   CAREGIVER
	   ========================================================= */

	.caregiver-list {
		margin-top: 18px;
	}


	.caregiver-row {
		padding: 13px 0;

		border-top: 1px solid #eadfc9;

		display: flex;
		align-items: center;
	}


	.caregiver-row:last-child {
		border-bottom: 1px solid #eadfc9;
	}


	.caregiver-avatar {
		width: 40px;
		height: 40px;

		border-radius: 50%;

		background: #dae65a;
		color: #2e6040;

		display: grid;
		place-items: center;

		font-weight: bold;
	}


	.caregiver-info {
		margin-left: 11px;

		display: flex;
		flex-direction: column;
	}


	.caregiver-name {
		display: flex;
		align-items: center;
		gap: 7px;
	}


	.caregiver-name strong {
		font-size: 10px;
	}


	.caregiver-name span {
		padding: 3px 6px;

		border-radius: 8px;

		background: #e5efd2;
		color: #4d7547;

		font-size: 6px;
	}


	.caregiver-info p {
		margin: 3px 0 0;

		color: #897c68;

		font-size: 7px;
	}


	.call-caregiver {
		width: 37px;
		height: 37px;

		margin-left: auto;

		border: 1px solid #d7c7a9;
		border-radius: 50%;

		background: #fffaf0;
		color: #197249;

		text-decoration: none;

		display: grid;
		place-items: center;

		font-size: 13px;
	}


	.call-caregiver:hover {
		background: #ebf1ce;
	}


	.care-note {
		margin-top: 16px;
		padding: 13px;

		border-radius: 14px;

		background: #f1f1dc;

		display: flex;
		gap: 8px;

		color: #5d6c58;
	}


	.care-note span {
		color: #6c9447;
	}


	.care-note p {
		margin: 0;

		font-size: 8px;
		line-height: 1.45;
	}



	/* =========================================================
	   ALERTS
	   ========================================================= */

	.alerts-list {
		margin-top: 19px;
	}


	.alert-card {
		padding: 15px;

		border: 1px solid #f0c9bc;
		border-radius: 15px;

		background: #fff0e9;

		display: flex;
		align-items: flex-start;
		gap: 11px;
	}


	.alert-symbol {
		width: 29px;
		height: 29px;

		flex-shrink: 0;

		border-radius: 50%;

		background: #d45c48;
		color: white;

		display: grid;
		place-items: center;

		font-weight: bold;
	}


	.alert-card strong {
		color: #a74a3c;

		font-size: 9px;
	}


	.alert-card p {
		margin: 5px 0 0;

		color: #795b50;

		font-size: 8px;
		line-height: 1.45;
	}


	.all-good {
		margin-top: 18px;
		padding: 17px;

		border-radius: 15px;

		background: #edf2d5;

		display: flex;
		align-items: center;
		gap: 11px;
	}


	.all-good > span {
		width: 34px;
		height: 34px;

		border-radius: 50%;

		background: #6b9550;
		color: white;

		display: grid;
		place-items: center;
	}


	.all-good strong {
		font-size: 9px;
	}


	.all-good p {
		margin: 4px 0 0;

		color: #77715c;

		font-size: 7px;
	}



	/* =========================================================
	   CLOSING
	   ========================================================= */

	.closing-card {
		position: relative;
		overflow: hidden;

		margin-top: 20px;
		padding: 22px 28px;

		border-radius: 23px;

		background:
			linear-gradient(
				90deg,
				#eef2d5,
				#f6f1df
			);

		display: flex;
		align-items: center;
		gap: 15px;
	}


	.closing-heart {
		width: 46px;
		height: 46px;

		border-radius: 15px;

		background: rgba(255,255,255,.56);
		color: #4f8447;

		display: grid;
		place-items: center;

		font-size: 25px;
	}


	.closing-card h2 {
		margin: 0;

		color: #2f6243;

		font-size: 16px;
	}


	.closing-card p {
		margin: 4px 0 0;

		color: #796f5d;

		font-size: 9px;
	}


	.closing-decoration {
		margin-left: auto;

		display: flex;
		gap: 20px;

		color: rgba(100,140,70,.28);

		font-size: 28px;
	}



	/* =========================================================
	   TABLET
	   ========================================================= */

	@media (max-width: 1050px) {

		.app {
			grid-template-columns: 205px minmax(0,1fr);
		}


		.sidebar {
			padding-left: 13px;
			padding-right: 13px;
		}


		.call-banner {
			grid-template-columns: 90px 1fr;
		}


		.call-countdown {
			grid-column: 1 / -1;

			padding: 17px 0 0;

			border-left: none;
			border-top: 1px solid rgba(255,255,255,.15);
		}


		.top-grid,
		.middle-grid,
		.lower-grid {
			grid-template-columns: 1fr;
		}

	}



	/* =========================================================
	   MOBILE
	   ========================================================= */

	@media (max-width: 760px) {

		.app {
			display: block;
		}


		.sidebar {
			display: none;
		}


		.topbar {
			height: 67px;

			padding: 0 15px;

			justify-content: space-between;
		}


		.mobile-logo {
			display: flex;
			align-items: center;
			gap: 8px;

			color: #0d6140;
		}


		.mobile-logo strong {
			font-size: 14px;
		}


		.top-date {
			display: none;
		}


		.help {
			display: none;
		}


		.profile-name,
		.dropdown-arrow {
			display: none;
		}


		.content {
			width: calc(100% - 24px);

			padding-top: 29px;
		}


		.welcome {
			align-items: flex-start;
			flex-direction: column;
		}


		.welcome h1 {
			font-size: 37px;
		}


		.welcome-badge {
			width: 100%;
		}


		.call-banner {
			padding: 24px 20px;

			grid-template-columns: 1fr;

			border-radius: 22px;
		}


		.call-phone {
			width: 75px;
			height: 120px;
		}


		.phone-display {
			height: 57px;
		}


		.call-info h2 {
			font-size: 26px;
		}


		.call-banner::after {
			right: 20px;
		}


		.call-countdown {
			grid-column: auto;
		}


		.countdown strong {
			font-size: 24px;
		}


		.panel {
			padding: 20px 17px;

			border-radius: 20px;
		}


		.medicine-row {
			padding: 10px 0;

			grid-template-columns: 50px 32px 1fr;
		}


		.medicine-row .medicine-action,
		.medicine-row .status-complete {
			grid-column: 3;

			justify-self: start;

			margin-top: 5px;
		}


		.moods {
			gap: 6px;
		}


		.moods button {
			min-height: 82px;
		}


		.face {
			width: 34px;
			height: 34px;

			font-size: 19px;
		}


		.timeline-row {
			grid-template-columns:
				47px 14px 34px 1fr;
		}


		.timeline-status {
			grid-column: 4;

			margin-top: -8px;
		}


		.call-row-top {
			flex-direction: column;
		}


		.call-badge {
			width: fit-content;
		}


		.closing-decoration {
			display: none;
		}

	}



	/* =========================================================
	   SMALL MOBILE
	   ========================================================= */

	@media (max-width: 410px) {

		.welcome h1 {
			font-size: 32px;
		}


		.moods {
			grid-template-columns: 1fr;
		}


		.moods button {
			min-height: 57px;

			flex-direction: row;
		}


		.panel-footer {
			align-items: flex-start;
			flex-direction: column;
			gap: 10px;
		}


		.call-chips {
			flex-direction: column;
			align-items: flex-start;
		}

	}
  .live-time {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    font-weight: 700;
    color: #0d7249;
}

/* 2026 senior experience refresh */
:global(body) {
	font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
	background: #f2f5ef;
}

.app {
	grid-template-columns: 272px minmax(0, 1fr);
	background:
		radial-gradient(circle at 84% 4%, rgba(202, 231, 96, .22), transparent 28%),
		linear-gradient(180deg, #f8faf6 0%, #eff3ec 100%);
}

.sidebar {
	padding: 26px 20px;
	border-right: 0;
	background:
		linear-gradient(165deg, rgba(255,255,255,.05), transparent 42%),
		#123f31;
	box-shadow: 14px 0 40px rgba(21, 62, 48, .10);
}

.brand { padding: 0 7px 27px; }
.brand .logo { background: #d6eb6c; color: #123f31; box-shadow: 0 9px 25px rgba(0,0,0,.16); }
.brand-copy strong { color: #fff; font-size: 19px; }
.brand-copy span { color: rgba(255,255,255,.58); }
.main-nav { gap: 7px; }
.nav-link { min-height: 58px; color: rgba(255,255,255,.78); border: 1px solid transparent; }
.nav-link small { color: rgba(255,255,255,.46); }
.nav-link:hover { background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.08); transform: translateX(3px); }
.nav-link.active { background: #e4efc7; color: #153f31; box-shadow: 0 12px 26px rgba(0,0,0,.13); }
.nav-link.active small { color: #647266; }
.nav-icon { border-radius: 11px; background: rgba(255,255,255,.07); }
.nav-link.active .nav-icon { background: rgba(18,63,49,.08); }

.sample-card {
	border-color: rgba(255,255,255,.12);
	background: linear-gradient(145deg, rgba(255,255,255,.12), rgba(255,255,255,.05));
	box-shadow: none;
}
.sample-copy p, .sample-copy h3, .sample-copy span, .sample-message { color: rgba(255,255,255,.82); }
.sample-copy p { color: #d6eb6c; }
.sample-button { background: #d6eb6c; color: #123f31; }
.sidebar-footer { color: rgba(255,255,255,.5); }

.topbar {
	height: 82px;
	border-color: rgba(25,82,61,.09);
	background: rgba(250,252,247,.86);
	backdrop-filter: blur(18px);
}
.help { background: white; border-color: rgba(25,82,61,.12); box-shadow: 0 8px 24px rgba(27,65,50,.06); }
.profile { padding: 5px 7px 5px 5px; border-radius: 16px; transition: background .2s ease; }
.profile:hover { background: rgba(18,63,49,.06); }
.avatar { background: #d6eb6c; box-shadow: 0 6px 16px rgba(92,122,43,.16); }

.content { width: min(1280px, 92%); padding-top: 36px; }
.welcome { align-items: center; }
.welcome h1 { font-family: Georgia, "Times New Roman", serif; letter-spacing: -2.8px; }
.welcome h1 span { font-family: Inter, ui-sans-serif, sans-serif; font-weight: 650; }
.welcome-badge { border-color: rgba(25,82,61,.11); background: rgba(255,255,255,.74); box-shadow: 0 14px 44px rgba(27,65,50,.07); }

.call-banner {
	border: 1px solid rgba(255,255,255,.12);
	background:
		radial-gradient(circle at 87% 8%, rgba(213,235,108,.18), transparent 30%),
		linear-gradient(135deg, #0f6647 0%, #118457 60%, #0e714c 100%);
	box-shadow: 0 26px 60px rgba(13,91,61,.18);
}

.panel {
	border-color: rgba(32,83,63,.11);
	background: rgba(255,255,255,.78);
	box-shadow: 0 18px 56px rgba(24,62,47,.07);
	transition: transform .22s ease, box-shadow .22s ease;
}
.panel:hover { transform: translateY(-2px); box-shadow: 0 24px 65px rgba(24,62,47,.11); }
.medicine-row, .timeline-row, .call-row { border-radius: 15px; transition: background .2s ease; }
.medicine-row:hover, .timeline-row:hover, .call-row:hover { background: #f5f8f2; }
.medicine-action, .outline-button, .wide-link, .add-button { transition: transform .18s ease, box-shadow .18s ease; }
.medicine-action:hover, .outline-button:hover, .add-button:hover { transform: translateY(-2px); box-shadow: 0 8px 18px rgba(20,93,63,.13); }
.moods button { border-color: rgba(31,83,62,.12); background: #fbfcf9; }
.moods button.chosen { background: #edf4d8; box-shadow: inset 0 0 0 1px rgba(37,100,69,.16); }
.closing-card { background: linear-gradient(135deg, #e6f0cf, #f8f5e9); border-color: rgba(32,83,63,.11); }

@media (max-width: 1020px) {
	.app { grid-template-columns: 224px minmax(0,1fr); }
	.sidebar { padding-inline: 14px; }
}

@media (max-width: 820px) {
	.app { display: block; }
	.sidebar { display: none; }
	.topbar { padding-inline: 20px; }
	.content { width: min(94%, 720px); }
}


</style>
