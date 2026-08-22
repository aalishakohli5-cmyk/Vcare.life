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

	let medications = $state([]);
	let loading = $state(true);
	let saving = $state(false);
	let filter = $state('all'); // 'all' | 'pending' | 'taken'
	let showAddModal = $state(false);
	let callStatus = $state(null); // { type: 'calling' | 'success' | 'error', message: '' }

	// New medication form
	let newMedName = $state('');
	let newMedDosage = $state('');
	let newMedTime = $state('08:00 AM');
	let addError = $state('');

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

	let medChannel;

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

						await loadMedications(firstSenior.id, token);

						// Setup Realtime
						medChannel = supabase
							.channel(`caregiver-meds-${firstSenior.id}`)
							.on(
								'postgres_changes',
								{
									event: '*',
									schema: 'public',
									table: 'medications',
									filter: `senior_id=eq.${firstSenior.id}`
								},
								() => {
									loadMedications(firstSenior.id, token);
								}
							)
							.subscribe();
					}
				}
			}
		} catch (err) {
			console.error('Error fetching senior/medications:', err);
		} finally {
			loading = false;
		}

		return () => {
			clearInterval(clock);
			if (medChannel) supabase.removeChannel(medChannel);
		};
	});

	async function loadMedications(seniorId, token) {
		try {
			const medResponse = await fetch(
				`${PUBLIC_BACKEND_URL}/medications/${seniorId}`,
				{
					headers: {
						'Authorization': `Bearer ${token}`,
						'Content-Type': 'application/json'
					}
				}
			);

			if (medResponse.ok) {
				const data = await medResponse.json();
				medications = data.map(m => ({
					id: m.id,
					name: m.name,
					dosage: m.dosage,
					scheduled_time: m.scheduled_time,
					taken: m.taken,
					status: m.taken ? 'taken' : 'pending'
				}));
			}
		} catch (e) {
			console.error('Failed to load medications:', e);
		}
	}

	/* =====================================================
	   ACTIONS
	==================================================== */

	async function toggleMedication(med) {
		const newStatus = !med.taken;
		// Optimistic update
		medications = medications.map(m =>
			m.id === med.id ? { ...m, taken: newStatus, status: newStatus ? 'taken' : 'pending' } : m
		);

		try {
			const { data: { session } } = await supabase.auth.getSession();
			const token = session?.access_token;

			const response = await fetch(`${PUBLIC_BACKEND_URL}/medications/${med.id}`, {
				method: 'PUT',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					taken: newStatus,
					taken_at: newStatus ? new Date().toISOString() : null
				})
			});

			if (!response.ok) {
				// Revert on failure
				medications = medications.map(m =>
					m.id === med.id ? { ...m, taken: !newStatus, status: !newStatus ? 'taken' : 'pending' } : m
				);
			}
		} catch (err) {
			console.error('Failed to update medication:', err);
		}
	}

	async function addMedication() {
		addError = '';
		if (!newMedName.trim()) {
			addError = 'Please enter medication name.';
			return;
		}

		if (!senior.id) {
			addError = 'No senior linked yet. Please complete onboarding first.';
			return;
		}

		saving = true;
		try {
			const { data: { session } } = await supabase.auth.getSession();
			const token = session?.access_token;

			const response = await fetch(`${PUBLIC_BACKEND_URL}/medications/`, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					senior_id: senior.id,
					name: newMedName.trim(),
					dosage: newMedDosage.trim() || 'As prescribed',
					scheduled_time: newMedTime.trim()
				})
			});

			if (response.ok) {
				const newMed = await response.json();
				medications = [...medications, {
					id: newMed.id,
					name: newMed.name,
					dosage: newMed.dosage,
					scheduled_time: newMed.scheduled_time,
					taken: false,
					status: 'pending'
				}];
				newMedName = '';
				newMedDosage = '';
				newMedTime = '08:00 AM';
				showAddModal = false;
			} else {
				const errData = await response.json().catch(() => ({}));
				addError = errData.detail || 'Failed to add medication.';
			}
		} catch (err) {
			console.error('Error adding medication:', err);
			addError = 'Error connecting to server.';
		} finally {
			saving = false;
		}
	}

	async function deleteMedication(medId) {
		if (!confirm('Are you sure you want to remove this medication?')) return;

		// Optimistic removal
		medications = medications.filter(m => m.id !== medId);

		try {
			const { data: { session } } = await supabase.auth.getSession();
			const token = session?.access_token;

			await fetch(`${PUBLIC_BACKEND_URL}/medications/${medId}`, {
				method: 'DELETE',
				headers: {
					'Authorization': `Bearer ${token}`
				}
			});
		} catch (err) {
			console.error('Error deleting medication:', err);
		}
	}

	async function triggerVcareCall(med = null) {
		if (!senior.phone) {
			callStatus = {
				type: 'error',
				message: `Cannot call ${senior.firstName}: Phone number is not registered.`
			};
			setTimeout(() => callStatus = null, 5000);
			return;
		}

		const targetMed = med || medications.find(m => m.status === 'pending') || medications[0];

		callStatus = {
			type: 'calling',
			message: `Initiating Vcare AI Call to ${senior.firstName} (${senior.phone})...`
		};

		try {
			const response = await fetch('/api/bland-call', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					phoneNumber: senior.phone,
					seniorName: senior.firstName,
					seniorId: senior.id,
					medicationId: targetMed?.id,
					medicationName: targetMed?.name || 'daily medicines',
					dosage: targetMed?.dosage || 'prescribed dose'
				})
			});

			const data = await response.json();

			if (response.ok && data.success) {
				callStatus = {
					type: 'success',
					message: `✓ Vcare Call connected to ${senior.firstName}! Bland AI is now checking on them.`
				};
			} else {
				callStatus = {
					type: 'error',
					message: data.error || 'Failed to trigger call. Check Bland AI credentials.'
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

	async function logout() {
		await supabase.auth.signOut();
		goto('/');
	}

	// Computed counts
	let pendingCount = $derived(medications.filter(m => !m.taken).length);
	let takenCount = $derived(medications.filter(m => m.taken).length);

	let filteredMeds = $derived(
		filter === 'all'
			? medications
			: filter === 'pending'
				? medications.filter(m => !m.taken)
				: medications.filter(m => m.taken)
	);
</script>

<svelte:head>
	<title>{senior.firstName}'s Medicines — Vcare.life</title>
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
			<a href="/caregiver/medicines" class="nav-item active">
				<span class="nav-icon">✚</span>
				<span>Medicines</span>
			</a>
			<a href="/caregiver/calls" class="nav-item">
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
				<h1>{senior.firstName}'s Medicine Schedule</h1>
				<p class="intro">Manage prescriptions, track daily adherence, and trigger instant AI reminder calls.</p>
			</div>

			<div class="top-actions">
				<button class="btn-reminder" onclick={() => triggerVcareCall()}>
					<span>☎</span>
					<span>Call {senior.firstName} Now</span>
				</button>
				<button class="btn-primary" onclick={() => showAddModal = true}>
					<span>✚</span>
					<span>Add Medicine</span>
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
				<div class="metric-icon total">💊</div>
				<div>
					<small>TOTAL MEDICINES</small>
					<strong>{medications.length}</strong>
				</div>
			</div>
			<div class="metric-card">
				<div class="metric-icon taken">✓</div>
				<div>
					<small>TAKEN TODAY</small>
					<strong>{takenCount}</strong>
				</div>
			</div>
			<div class="metric-card">
				<div class="metric-icon pending">⏳</div>
				<div>
					<small>PENDING</small>
					<strong>{pendingCount}</strong>
				</div>
			</div>
		</section>

		<!-- FILTER TABS -->
		<div class="filter-bar">
			<div class="filter-pills">
				<button class="pill" class:active={filter === 'all'} onclick={() => filter = 'all'}>
					All ({medications.length})
				</button>
				<button class="pill" class:active={filter === 'pending'} onclick={() => filter = 'pending'}>
					Pending ({pendingCount})
				</button>
				<button class="pill" class:active={filter === 'taken'} onclick={() => filter = 'taken'}>
					Taken ({takenCount})
				</button>
			</div>
		</div>

		<!-- MEDICATIONS LIST -->
		{#if loading}
			<div class="loading-state">
				<div class="spinner">♥</div>
				<p>Loading medicines for {senior.firstName}...</p>
			</div>
		{:else if filteredMeds.length === 0}
			<div class="empty-card">
				<div class="empty-icon">✚</div>
				<h3>No medicines found</h3>
				<p>{filter === 'all' ? `You haven't added any medicines for ${senior.firstName} yet.` : `No ${filter} medicines right now.`}</p>
				{#if filter === 'all'}
					<button class="btn-primary" onclick={() => showAddModal = true}>
						<span>✚</span> Add First Medicine
					</button>
				{/if}
			</div>
		{:else}
			<div class="meds-grid">
				{#each filteredMeds as med (med.id)}
					<div class="med-card" class:taken={med.taken}>
						<div class="med-card-top">
							<button class="status-btn" class:taken={med.taken} onclick={() => toggleMedication(med)} title="Click to toggle status">
								{med.taken ? '✓' : '○'}
							</button>
							<div class="med-details">
								<h3>{med.name}</h3>
								<p class="dosage-text">{med.dosage}</p>
							</div>
							<span class="status-pill" class:taken={med.taken} class:pending={!med.taken}>
								{med.taken ? 'Taken' : 'Pending'}
							</span>
						</div>

						<div class="med-card-mid">
							<div class="time-badge">
								<span>⏰</span>
								<span>{med.scheduled_time}</span>
							</div>
						</div>

						<div class="med-card-actions">
							<button class="action-btn call" onclick={() => triggerVcareCall(med)} title="Trigger Vcare reminder call for this medicine">
								<span>☎</span>
								<span>Remind with AI</span>
							</button>
							<button class="action-btn delete" onclick={() => deleteMedication(med.id)} title="Delete medication">
								<span>🗑</span>
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}

	</main>

</div>

<!-- ADD MEDICINE MODAL -->
{#if showAddModal}
	<div class="modal-overlay" onclick={(e) => { if (e.target === e.currentTarget) showAddModal = false; }} role="dialog" aria-modal="true">
		<div class="modal-card">
			<header class="modal-header">
				<div>
					<p class="eyebrow">NEW PRESCRIPTION</p>
					<h2>Add Medicine for {senior.firstName}</h2>
				</div>
				<button class="modal-close" onclick={() => showAddModal = false}>×</button>
			</header>

			{#if addError}
				<div class="modal-error">{addError}</div>
			{/if}

			<form onsubmit={(e) => { e.preventDefault(); addMedication(); }}>
				<div class="form-group">
					<label for="medName">Medicine Name & Purpose</label>
					<input
						id="medName"
						type="text"
						bind:value={newMedName}
						placeholder="e.g. Metformin (Blood Sugar)"
						required
					/>
					<div class="presets">
						<span class="preset-label">Quick suggestions:</span>
						<button type="button" class="preset-tag" onclick={() => { newMedName = 'Metformin 500mg'; newMedDosage = '1 Tablet with meals'; }}>Metformin</button>
						<button type="button" class="preset-tag" onclick={() => { newMedName = 'Amlodipine 5mg'; newMedDosage = '1 Tablet after lunch'; }}>Amlodipine</button>
						<button type="button" class="preset-tag" onclick={() => { newMedName = 'Calcium + Vit D3'; newMedDosage = '1 Tablet post dinner'; }}>Calcium</button>
					</div>
				</div>

				<div class="form-group">
					<label for="medDosage">Dosage & Instructions</label>
					<input
						id="medDosage"
						type="text"
						bind:value={newMedDosage}
						placeholder="e.g. 1 Tablet after breakfast"
					/>
				</div>

				<div class="form-group">
					<label for="medTime">Scheduled Reminder Time</label>
					<input
						id="medTime"
						type="text"
						bind:value={newMedTime}
						placeholder="e.g. 08:00 AM"
					/>
					<div class="time-presets">
						<button type="button" class="time-tag" class:active={newMedTime === '08:00 AM'} onclick={() => newMedTime = '08:00 AM'}>🌅 08:00 AM</button>
						<button type="button" class="time-tag" class:active={newMedTime === '02:00 PM'} onclick={() => newMedTime = '02:00 PM'}>☀️ 02:00 PM</button>
						<button type="button" class="time-tag" class:active={newMedTime === '08:30 PM'} onclick={() => newMedTime = '08:30 PM'}>🌙 08:30 PM</button>
					</div>
				</div>

				<footer class="modal-footer">
					<button type="button" class="btn-cancel" onclick={() => showAddModal = false}>Cancel</button>
					<button type="submit" class="btn-submit" disabled={saving}>
						{saving ? 'Saving...' : 'Save Medicine'}
					</button>
				</footer>
			</form>
		</div>
	</div>
{/if}

<style>
	:global(*) {
		box-sizing: border-box;
	}

	:global(html), :global(body) {
		margin: 0;
		min-height: 100%;
	}

	:global(body) {
		background: #f7f0e2;
		color: #173f31;
		font-family: "Comic Sans MS", "Comic Sans", "Chalkboard SE", "Marker Felt", cursive;
	}

	button, a, input {
		font-family: inherit;
	}

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

	.brand > div:last-child {
		display: flex;
		flex-direction: column;
	}

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

	.nav-item.active {
		color: #143d2e;
		background: #dce76a;
	}

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

	.btn-reminder {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: #ebf5b8;
		color: #174631;
		padding: 12px 20px;
		border-radius: 14px;
		border: 1px solid #d4e892;
		font-weight: bold;
		cursor: pointer;
		transition: 0.2s ease;
	}

	.btn-reminder:hover {
		background: #dce76a;
		transform: translateY(-2px);
	}

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
	.metric-icon.taken { background: #e6f7eb; color: #137333; }
	.metric-icon.pending { background: #fef7e0; color: #b06000; }

	.metric-card small { display: block; font-size: 10px; color: #8a7a66; letter-spacing: 0.8px; }
	.metric-card strong { font-size: 24px; color: #173f31; }

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

	/* MEDS GRID */
	.meds-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 20px;
	}

	.med-card {
		background: white;
		border-radius: 20px;
		padding: 22px;
		border: 1px solid #ebe0cc;
		box-shadow: 0 4px 18px rgba(23,63,49,0.04);
		transition: 0.2s ease;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.med-card:hover {
		transform: translateY(-3px);
		box-shadow: 0 8px 24px rgba(23,63,49,0.08);
	}

	.med-card.taken {
		border-color: #cdecd5;
		background: #fbfdfb;
	}

	.med-card-top {
		display: flex;
		align-items: flex-start;
		gap: 14px;
	}

	.status-btn {
		width: 32px;
		height: 32px;
		border-radius: 10px;
		border: 2px solid #c9bda8;
		background: white;
		color: #635541;
		font-size: 16px;
		font-weight: bold;
		cursor: pointer;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		transition: 0.2s ease;
	}

	.status-btn:hover {
		border-color: #0b6845;
		transform: scale(1.08);
	}

	.status-btn.taken {
		background: #0b6845;
		border-color: #0b6845;
		color: white;
	}

	.med-details { flex: 1; }
	.med-details h3 { margin: 0; font-size: 17px; color: #173f31; }
	.dosage-text { margin: 4px 0 0; color: #72624d; font-size: 12px; }

	.status-pill {
		padding: 4px 10px;
		border-radius: 8px;
		font-size: 10px;
		font-weight: bold;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.status-pill.taken { background: #d7f5dd; color: #0b6845; }
	.status-pill.pending { background: #fff0d4; color: #b86200; }

	.med-card-mid {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.time-badge {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		background: #f4ecdc;
		padding: 6px 12px;
		border-radius: 10px;
		font-size: 12px;
		font-weight: bold;
		color: #4b3e2d;
	}

	.med-card-actions {
		display: flex;
		align-items: center;
		gap: 10px;
		padding-top: 14px;
		border-top: 1px dashed #ede2cf;
	}

	.action-btn {
		padding: 8px 14px;
		border-radius: 10px;
		font-weight: bold;
		font-size: 12px;
		cursor: pointer;
		border: none;
		transition: 0.2s ease;
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}

	.action-btn.call {
		flex: 1;
		background: #eef7c0;
		color: #174631;
		border: 1px solid #d8e895;
	}

	.action-btn.call:hover { background: #dce76a; }

	.action-btn.delete {
		background: #fae8e8;
		color: #b81414;
	}

	.action-btn.delete:hover { background: #f5cfcf; }

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
	.empty-card p { margin: 0 0 20px; color: #72624d; }

	/* MODAL */
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(11, 45, 33, 0.6);
		backdrop-filter: blur(4px);
		display: grid;
		place-items: center;
		padding: 20px;
		z-index: 1000;
	}

	.modal-card {
		background: white;
		width: 100%;
		max-width: 500px;
		border-radius: 24px;
		padding: 30px;
		box-shadow: 0 20px 40px rgba(0,0,0,0.2);
	}

	.modal-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		margin-bottom: 20px;
	}

	.modal-header h2 { margin: 4px 0 0; color: #0b3d2b; font-size: 22px; }
	.eyebrow { margin: 0; font-size: 10px; color: #85745f; letter-spacing: 1px; }

	.modal-close {
		background: transparent;
		border: none;
		font-size: 28px;
		color: #85745f;
		cursor: pointer;
	}

	.modal-error {
		background: #fde8e8;
		color: #b81414;
		padding: 10px 14px;
		border-radius: 10px;
		margin-bottom: 16px;
		font-size: 12px;
	}

	.form-group {
		margin-bottom: 18px;
	}

	.form-group label {
		display: block;
		margin-bottom: 6px;
		font-weight: bold;
		color: #173f31;
		font-size: 13px;
	}

	.form-group input {
		width: 100%;
		padding: 12px 16px;
		border: 1px solid #d9cdb8;
		border-radius: 12px;
		font-size: 14px;
		background: #fdfbf7;
		color: #173f31;
		outline: none;
	}

	.form-group input:focus { border-color: #0b6845; }

	.presets {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-top: 8px;
		align-items: center;
	}

	.preset-label { font-size: 10px; color: #8a7a66; }

	.preset-tag, .time-tag {
		background: #f0e6d2;
		border: 1px solid #dfd1b8;
		padding: 4px 10px;
		border-radius: 8px;
		font-size: 11px;
		cursor: pointer;
		color: #3b3022;
	}

	.preset-tag:hover, .time-tag:hover { background: #e4d6be; }
	.time-presets { display: flex; gap: 8px; margin-top: 8px; }
	.time-tag.active { background: #0b6845; color: white; border-color: #0b6845; }

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
		margin-top: 26px;
	}

	.btn-cancel {
		background: #f4ecdc;
		border: none;
		padding: 12px 20px;
		border-radius: 12px;
		font-weight: bold;
		cursor: pointer;
		color: #4b3e2d;
	}

	.btn-submit {
		background: #0b6845;
		color: white;
		border: none;
		padding: 12px 24px;
		border-radius: 12px;
		font-weight: bold;
		cursor: pointer;
	}

	.btn-submit:hover { background: #074e33; }
</style>
