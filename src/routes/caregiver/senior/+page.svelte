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
		full_name: '',
		phone: '',
		date_of_birth: '',
		gender: '',
		preferred_language: 'English',
		emergency_contact_name: '',
		emergency_contact_relationship: '',
		emergency_contact_phone: '',
		role: 'senior'
	});

	let loading = $state(true);
	let saving = $state(false);
	let saveStatus = $state(null); // { type: 'success' | 'error', message: '' }

	let medCount = $state(0);
	let callCount = $state(0);

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
			.select('full_name, phone')
			.eq('id', user.id)
			.maybeSingle();

		if (profile?.full_name) {
			caregiverName = profile.full_name;
			caregiverInitial = profile.full_name.charAt(0).toUpperCase();
		}

		// Fetch assigned senior
		let seniors = [];
		const token = session?.access_token;

		// 1. Try Backend API
		if (token && PUBLIC_BACKEND_URL) {
			try {
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
					seniors = await response.json();
				}
			} catch (err) {
				console.warn('Backend senior fetch failed, falling back to Supabase:', err);
			}
		}

		// 2. Direct Supabase query fallback
		if (!seniors || seniors.length === 0) {
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

			if ((!seniors || seniors.length === 0) && profile?.emergency_contact_name) {
				seniors = [{
					id: user.id,
					full_name: profile.emergency_contact_name,
					phone: profile.emergency_contact_phone || '',
					role: 'senior'
				}];
			}
		}

		if (seniors && seniors.length > 0) {
			const firstSenior = seniors[0];
			senior = {
				id: firstSenior.id,
				full_name: firstSenior.full_name || '',
				phone: firstSenior.phone || '',
				date_of_birth: firstSenior.date_of_birth || '',
				gender: firstSenior.gender || '',
				preferred_language: firstSenior.preferred_language || 'English',
				emergency_contact_name: firstSenior.emergency_contact_name || caregiverName,
				emergency_contact_relationship: firstSenior.emergency_contact_relationship || 'Caregiver',
				emergency_contact_phone: firstSenior.emergency_contact_phone || (profile?.phone || ''),
				role: 'senior'
			};

			// Fetch counts
			let meds = [];
			if (token && PUBLIC_BACKEND_URL) {
				try {
					const medRes = await fetch(`${PUBLIC_BACKEND_URL}/medications/${firstSenior.id}`, {
						headers: { 'Authorization': `Bearer ${token}` }
					});
					if (medRes.ok) meds = await medRes.json();
				} catch (e) {
					console.warn('Backend med count fetch failed:', e);
				}
			}
			if (!meds || meds.length === 0) {
				const { data: sbMeds } = await supabase
					.from('medications')
					.select('id')
					.eq('senior_id', firstSenior.id);
				if (sbMeds) meds = sbMeds;
			}
			medCount = meds.length;

			let calls = [];
			if (token && PUBLIC_BACKEND_URL) {
				try {
					const callRes = await fetch(`${PUBLIC_BACKEND_URL}/calls/${firstSenior.id}`, {
						headers: { 'Authorization': `Bearer ${token}` }
					});
					if (callRes.ok) calls = await callRes.json();
				} catch (e) {
					console.warn('Backend call count fetch failed:', e);
				}
			}
			if (!calls || calls.length === 0) {
				const { data: sbCalls } = await supabase
					.from('call_logs')
					.select('id')
					.eq('senior_id', firstSenior.id);
				if (sbCalls) calls = sbCalls;
			}
			callCount = calls.length;
		}

		loading = false;

		return () => clearInterval(clock);
	});

	/* =====================================================
	   SAVE PROFILE
	===================================================== */

	async function saveSeniorProfile() {
		if (!senior.id) return;
		saving = true;
		saveStatus = null;

		try {
			const { data: { session } } = await supabase.auth.getSession();
			const token = session?.access_token;

			let saved = false;

			if (token && PUBLIC_BACKEND_URL) {
				try {
					const response = await fetch(`${PUBLIC_BACKEND_URL}/seniors/${senior.id}`, {
						method: 'PUT',
						headers: {
							'Authorization': `Bearer ${token}`,
							'Content-Type': 'application/json'
						},
						body: JSON.stringify({
							full_name: senior.full_name,
							phone: senior.phone,
							date_of_birth: senior.date_of_birth || null,
							gender: senior.gender || null,
							preferred_language: senior.preferred_language,
							emergency_contact_name: senior.emergency_contact_name,
							emergency_contact_relationship: senior.emergency_contact_relationship,
							emergency_contact_phone: senior.emergency_contact_phone
						})
					});
					if (response.ok) saved = true;
				} catch (e) {
					console.warn('Backend save profile failed, falling back to Supabase:', e);
				}
			}

			if (!saved) {
				const { error: sbErr } = await supabase
					.from('profiles')
					.update({
						full_name: senior.full_name,
						phone: senior.phone,
						date_of_birth: senior.date_of_birth || null,
						gender: senior.gender || null,
						preferred_language: senior.preferred_language,
						emergency_contact_name: senior.emergency_contact_name,
						emergency_contact_relationship: senior.emergency_contact_relationship,
						emergency_contact_phone: senior.emergency_contact_phone
					})
					.eq('id', senior.id);

				if (sbErr) throw sbErr;
				saved = true;
			}

			if (saved) {
				saveStatus = {
					type: 'success',
					message: '✓ Senior profile updated successfully!'
				};
			}
		} catch (err) {
			console.error('Error updating profile:', err);
			saveStatus = {
				type: 'error',
				message: err.message || 'Error saving senior profile.'
			};
		} finally {
			saving = false;
			setTimeout(() => saveStatus = null, 4000);
		}
	}

	async function logout() {
		await supabase.auth.signOut();
		goto('/');
	}

	let seniorFirstName = $derived((senior.full_name || 'Senior').split(' ')[0]);
	let seniorInitials = $derived(
		(senior.full_name || 'S')
			.split(' ')
			.map(n => n.charAt(0))
			.join('')
			.toUpperCase()
	);
</script>

<svelte:head>
	<title>{seniorFirstName}'s Profile — Vcare.life</title>
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
			<a href="/caregiver/calls" class="nav-item">
				<span class="nav-icon">☎</span>
				<span>Vcare Calls</span>
			</a>
			<a href="/caregiver/senior" class="nav-item active">
				<span class="nav-icon">♡</span>
				<span>Senior Profile</span>
			</a>
		</nav>

		<div class="sidebar-bottom">
			<div class="mini-senior">
				<div class="mini-avatar">{seniorInitials}</div>
				<div>
					<small>CARING FOR</small>
					<strong>{senior.full_name || 'Senior'}</strong>
				</div>
			</div>

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
				<h1>{seniorFirstName}'s Profile & Care Details</h1>
				<p class="intro">Update senior information, emergency contacts, and personalized call settings.</p>
			</div>

			<div class="top-actions">
				<a href={`tel:${senior.phone}`} class="btn-secondary">
					<span>☎</span>
					<span>Call {seniorFirstName}</span>
				</a>
				<button class="btn-primary" onclick={saveSeniorProfile} disabled={saving}>
					<span>💾</span>
					<span>{saving ? 'Saving...' : 'Save Changes'}</span>
				</button>
			</div>
		</header>

		<!-- SAVE STATUS TOAST -->
		{#if saveStatus}
			<div class="status-banner" class:success={saveStatus.type === 'success'} class:error={saveStatus.type === 'error'}>
				<span>{saveStatus.type === 'success' ? '✓' : '⚠'}</span>
				<p>{saveStatus.message}</p>
			</div>
		{/if}

		{#if loading}
			<div class="loading-state">
				<div class="spinner">♥</div>
				<p>Loading {seniorFirstName}'s details...</p>
			</div>
		{:else if !senior.id}
			<div class="empty-card">
				<div class="empty-icon">♡</div>
				<h3>No senior profile found</h3>
				<p>You haven't completed onboarding or linked a senior yet.</p>
				<a href="/onboarding/caregiver" class="btn-primary">
					<span>✚</span> Complete Onboarding
				</a>
			</div>
		{:else}
			<!-- PROFILE CARDS GRID -->
			<div class="profile-grid">

				<!-- 1. PERSONAL INFO CARD -->
				<section class="card">
					<div class="card-header">
						<div class="card-icon">☺</div>
						<div>
							<h2>Personal Information</h2>
							<p>Senior's identification and phone contact for Vcare AI calls</p>
						</div>
					</div>

					<div class="form-grid">
						<div class="field full">
							<label for="fullName">Full Legal Name</label>
							<input
								id="fullName"
								type="text"
								bind:value={senior.full_name}
								placeholder="e.g. Kalyani Devi"
							/>
						</div>

						<div class="field">
							<label for="phone">Phone Number (used for AI Calls)</label>
							<input
								id="phone"
								type="tel"
								bind:value={senior.phone}
								placeholder="+919876543210"
							/>
							<small class="hint">Include country code (e.g. +91)</small>
						</div>

						<div class="field">
							<label for="dob">Date of Birth</label>
							<input
								id="dob"
								type="date"
								bind:value={senior.date_of_birth}
							/>
						</div>

						<div class="field">
							<label for="gender">Gender</label>
							<select id="gender" bind:value={senior.gender}>
								<option value="">Select gender</option>
								<option value="Female">Female</option>
								<option value="Male">Male</option>
								<option value="Other">Other / Prefer not to say</option>
							</select>
						</div>

						<div class="field">
							<label for="language">Preferred AI Call Language</label>
							<select id="language" bind:value={senior.preferred_language}>
								<option value="English">English</option>
								<option value="Hindi">Hindi</option>
								<option value="Hinglish">Hindi / English (Mixed)</option>
								<option value="Spanish">Spanish</option>
								<option value="French">French</option>
							</select>
						</div>
					</div>
				</section>

				<!-- 2. EMERGENCY CONTACT & CAREGIVER LINK CARD -->
				<section class="card">
					<div class="card-header">
						<div class="card-icon emergency">🛡</div>
						<div>
							<h2>Emergency & Care Contact</h2>
							<p>Person to notify if distress or missed medicines are detected</p>
						</div>
					</div>

					<div class="form-grid">
						<div class="field full">
							<label for="emerName">Emergency Contact Name</label>
							<input
								id="emerName"
								type="text"
								bind:value={senior.emergency_contact_name}
								placeholder="e.g. Adarsh"
							/>
						</div>

						<div class="field">
							<label for="emerRel">Relationship to Senior</label>
							<input
								id="emerRel"
								type="text"
								bind:value={senior.emergency_contact_relationship}
								placeholder="e.g. Son / Daughter"
							/>
						</div>

						<div class="field">
							<label for="emerPhone">Emergency Contact Phone</label>
							<input
								id="emerPhone"
								type="tel"
								bind:value={senior.emergency_contact_phone}
								placeholder="+919876543210"
							/>
						</div>
					</div>

					<div class="security-badge">
						<span>🛡</span>
						<p>Vcare automatically alerts this contact when distress or consecutive missed medication is detected during check-ins.</p>
					</div>
				</section>

				<!-- 3. CARE OVERVIEW SUMMARY -->
				<section class="card overview-card">
					<div class="card-header">
						<div class="card-icon stats">📊</div>
						<div>
							<h2>Care Circle Overview</h2>
							<p>Real-time statistics for {seniorFirstName}</p>
						</div>
					</div>

					<div class="stats-row">
						<a href="/caregiver/medicines" class="stat-box">
							<span class="stat-number">{medCount}</span>
							<span class="stat-label">Active Prescriptions</span>
							<span class="stat-link">Manage medicines →</span>
						</a>

						<a href="/caregiver/calls" class="stat-box">
							<span class="stat-number">{callCount}</span>
							<span class="stat-label">Vcare Calls Logged</span>
							<span class="stat-link">View call logs →</span>
						</a>

						<div class="stat-box status">
							<span class="status-indicator">● Active</span>
							<span class="stat-label">Connection Status</span>
							<span class="stat-sub">Linked with {caregiverName}</span>
						</div>
					</div>
				</section>

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

	button, a, input, select { font-family: inherit; }

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
		color: white;
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
		text-decoration: none;
	}

	.btn-primary:hover { background: #08402a; transform: translateY(-2px); }

	.btn-secondary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: #f0e6d2;
		color: #173f31;
		padding: 12px 20px;
		border-radius: 14px;
		text-decoration: none;
		border: 1px solid #dfd1b8;
		font-weight: bold;
		cursor: pointer;
		transition: 0.2s ease;
	}

	.btn-secondary:hover { background: #e6d8c0; transform: translateY(-2px); }

	/* STATUS BANNER */
	.status-banner {
		padding: 14px 20px;
		border-radius: 14px;
		margin-bottom: 22px;
		display: flex;
		align-items: center;
		gap: 12px;
		font-weight: bold;
		animation: slideDown 0.3s ease;
	}

	.status-banner.success { background: #e3fae8; color: #0f6828; border: 1px solid #a6e8b4; }
	.status-banner.error { background: #fde8e8; color: #b81414; border: 1px solid #f8b4b4; }
	.status-banner p { margin: 0; font-size: 13px; }

	@keyframes slideDown {
		from { opacity: 0; transform: translateY(-10px); }
		to { opacity: 1; transform: translateY(0); }
	}

	/* PROFILE GRID */
	.profile-grid {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.card {
		background: white;
		border-radius: 24px;
		padding: 30px;
		border: 1px solid #ebe0cc;
		box-shadow: 0 4px 18px rgba(23,63,49,0.04);
	}

	.card-header {
		display: flex;
		align-items: center;
		gap: 16px;
		margin-bottom: 24px;
		padding-bottom: 18px;
		border-bottom: 1px solid #f2e9dc;
	}

	.card-icon {
		width: 48px;
		height: 48px;
		border-radius: 16px;
		background: #e8f5ec;
		color: #0b6845;
		display: grid;
		place-items: center;
		font-size: 22px;
		flex-shrink: 0;
	}

	.card-icon.emergency { background: #fff0d4; color: #b86200; }
	.card-icon.stats { background: #e8f0fe; color: #1a73e8; }

	.card-header h2 { margin: 0; font-size: 20px; color: #0b3d2b; }
	.card-header p { margin: 4px 0 0; font-size: 12px; color: #85745f; }

	.form-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 20px;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.field.full { grid-column: 1 / -1; }

	.field label {
		font-weight: bold;
		color: #173f31;
		font-size: 13px;
	}

	.field input, .field select {
		padding: 12px 16px;
		border: 1px solid #d9cdb8;
		border-radius: 12px;
		font-size: 14px;
		background: #fdfbf7;
		color: #173f31;
		outline: none;
		transition: 0.2s ease;
	}

	.field input:focus, .field select:focus {
		border-color: #0b6845;
		background: white;
	}

	.hint { font-size: 11px; color: #8a7a66; }

	.security-badge {
		margin-top: 20px;
		background: #fdfbf7;
		border: 1px solid #eee5d3;
		border-radius: 14px;
		padding: 14px 18px;
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.security-badge span { font-size: 20px; }
	.security-badge p { margin: 0; font-size: 12px; color: #695a47; line-height: 1.4; }

	/* STATS ROW */
	.stats-row {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 18px;
	}

	.stat-box {
		background: #fdfbf7;
		border: 1px solid #ede2cf;
		border-radius: 18px;
		padding: 20px;
		display: flex;
		flex-direction: column;
		text-decoration: none;
		color: inherit;
		transition: 0.2s ease;
	}

	.stat-box:hover {
		transform: translateY(-2px);
		border-color: #0b6845;
		background: white;
	}

	.stat-number { font-size: 32px; font-weight: bold; color: #0b3d2b; }
	.stat-label { font-size: 13px; font-weight: bold; color: #173f31; margin-top: 4px; }
	.stat-link { font-size: 11px; color: #0b6845; font-weight: bold; margin-top: 10px; }

	.stat-box.status { background: #e3fae8; border-color: #b5eec3; }
	.status-indicator { color: #0f6828; font-weight: bold; font-size: 16px; }
	.stat-sub { font-size: 11px; color: #2e663e; margin-top: 8px; }

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
</style>
