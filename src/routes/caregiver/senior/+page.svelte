<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import { chooseCareRecipient } from '$lib/careConnections';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import Badge from '$lib/components/Badge.svelte';
	import PhoneInput, { countryCodes } from '$lib/components/PhoneInput.svelte';
	import '../theme.css';

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

	let seniorPhoneLocal = $state('');
	let seniorPhoneCountry = $state('+91');

	let emergencyPhoneLocal = $state('');
	let emergencyPhoneCountry = $state('+91');

	function splitPhone(fullPhone) {
		if (!fullPhone) return { countryCode: '+91', local: '' };
		const match = countryCodes.find((c) => fullPhone.startsWith(c.code));
		if (match) {
			return {
				countryCode: match.code,
				local: fullPhone.slice(match.code.length)
			};
		}
		return { countryCode: '+91', local: fullPhone.replace(/^\+91/, '') };
	}

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

			const pSenior = splitPhone(senior.phone);
			seniorPhoneCountry = pSenior.countryCode;
			seniorPhoneLocal = pSenior.local;

			const pEmer = splitPhone(senior.emergency_contact_phone);
			emergencyPhoneCountry = pEmer.countryCode;
			emergencyPhoneLocal = pEmer.local;

			// Fast load counts from Supabase directly
			try {
				const { data: sbMeds } = await supabase
					.from('medications')
					.select('id')
					.eq('senior_id', firstSenior.id);
				if (sbMeds) medCount = sbMeds.length;

				const { data: sbCalls } = await supabase
					.from('call_logs')
					.select('id')
					.eq('senior_id', firstSenior.id);
				if (sbCalls) callCount = sbCalls.length;
			} catch (e) {
				console.error('Failed to load counts from Supabase:', e);
			}
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

		const cleanPhone = (val) => (val || '').replace(/\D/g, '');
		senior.phone = seniorPhoneLocal.trim()
			? `${seniorPhoneCountry}${cleanPhone(seniorPhoneLocal)}`
			: '';
		senior.emergency_contact_phone = emergencyPhoneLocal.trim()
			? `${emergencyPhoneCountry}${cleanPhone(emergencyPhoneLocal)}`
			: '';

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
</script>

<svelte:head>
	<title>Senior Profile & Care Details — Vcare.life</title>
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
			<a href="/caregiver/calls" class="nav-item">
				<span class="nav-icon" aria-hidden="true">
					<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
					</svg>
				</span>
				<span>Vcare Calls</span>
			</a>
			<a href="/caregiver/senior" class="nav-item active">
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
			<div class="mini-senior">
				<div class="mini-avatar">{seniorInitials}</div>
				<div class="mini-senior-info">
				<div class="mini-avatar" aria-hidden="true">♡</div>
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
				<h1 class="page-title">{seniorFirstName}'s Profile & Care Details</h1>
				<p class="intro">Update senior information, emergency contacts, and personalized call settings.</p>
				<h1>Senior Profile & Care Details</h1>
				<p class="intro">Review the person receiving care, emergency contacts, and personalized call settings.</p>
			</div>

			<div class="top-actions">
				<a
					href={`tel:${senior.phone}`}
					class="btn-secondary"
					aria-label={`Call ${seniorFirstName}`}
				>
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
			<div
				class="status-banner"
				class:success={saveStatus.type === 'success'}
				class:error={saveStatus.type === 'error'}
			>
				<span aria-hidden="true">{saveStatus.type === 'success' ? '✓' : '⚠️'}</span>
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
				<div class="empty-icon" aria-hidden="true">♡</div>
				<h3>No senior profile found</h3>
				<p>You haven't completed onboarding or linked a senior yet.</p>
				<a href="/onboarding/caregiver" class="btn-primary">
					<span>✚</span> Complete Onboarding
				</a>
			</div>
		{:else}
			<!-- PROFILE CARDS GRID -->
			<div class="profile-grid">

				<!-- 1. PERSONAL INFO CARD (SEMANTIC GREEN ICON CHIP) -->
				<section class="card">
					<div class="card-header">
						<div class="card-icon personal" aria-hidden="true">
							<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
								<circle cx="12" cy="7" r="4"/>
							</svg>
						</div>
						<div>
							<h2>Personal Information</h2>
							<p class="section-desc">Senior's identification and phone contact for Vcare AI calls</p>
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
							<small class="hint">This is the care recipient name shown throughout the caregiver portal. Correct it here and select “Save Changes”.</small>
						</div>

						<div class="field">
							<label for="phone">Phone Number (used for AI Calls)</label>
							<PhoneInput
								id="phone"
								bind:value={seniorPhoneLocal}
								bind:countryCode={seniorPhoneCountry}
								placeholder="Phone number"
							/>
						</div>

						<div class="field">
							<label for="dob">Date of Birth</label>
							<input
								id="dob"
								type="date"
								bind:value={senior.date_of_birth}
							/>
							<small class="hint">Formatted as YYYY-MM-DD</small>
						</div>

						<div class="field">
							<label for="gender">Gender</label>
							<div class="select-wrapper">
								<select id="gender" bind:value={senior.gender}>
									<option value="">Select gender</option>
									<option value="Female">Female</option>
									<option value="Male">Male</option>
									<option value="Other">Other / Prefer not to say</option>
								</select>
							</div>
						</div>

						<div class="field">
							<label for="language">Preferred AI Call Language</label>
							<div class="select-wrapper">
								<select id="language" bind:value={senior.preferred_language}>
									<option value="English">English</option>
									<option value="Hindi">Hindi</option>
									<option value="Hinglish">Hindi / English (Mixed)</option>
									<option value="Spanish">Spanish</option>
									<option value="French">French</option>
								</select>
							</div>
						</div>
					</div>
				</section>

				<!-- 2. EMERGENCY CONTACT & CAREGIVER LINK CARD (SEMANTIC AMBER ICON CHIP) -->
				<section class="card">
					<div class="card-header">
						<div class="card-icon emergency" aria-hidden="true">
							<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
							</svg>
						</div>
						<div>
							<h2>Emergency & Care Contact</h2>
							<p class="section-desc">Person to notify if distress or missed medicines are detected</p>
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
							<PhoneInput
								id="emerPhone"
								bind:value={emergencyPhoneLocal}
								bind:countryCode={emergencyPhoneCountry}
								placeholder="Phone number"
							/>
						</div>
					</div>

					<!-- REFERENCE SHIELD TRUST REASSURANCE BOX -->
					<div class="security-badge">
						<span class="security-badge-icon" aria-hidden="true">
							<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
								<path d="m9 12 2 2 4-4"/>
							</svg>
						</span>
						<p>Vcare automatically alerts this contact when distress or consecutive missed medication is detected during check-ins.</p>
					</div>
				</section>

				<!-- 3. CARE OVERVIEW SUMMARY (CONSISTENT CARDS TREATMENT) -->
				<section class="card overview-card">
					<div class="card-header">
						<div class="card-icon overview" aria-hidden="true">
							<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								<line x1="18" y1="20" x2="18" y2="10"/>
								<line x1="12" y1="20" x2="12" y2="4"/>
								<line x1="6" y1="20" x2="6" y2="14"/>
							</svg>
						</div>
						<div>
							<h2>Care Circle Overview</h2>
							<p class="section-desc">Real-time statistics for {seniorFirstName}</p>
						</div>
					</div>

					<!-- CONSISTENT CARD GRID WITH UNIFIED VISUAL WEIGHT -->
					<div class="stats-row">
						<a href="/caregiver/medicines" class="stat-box">
							<div class="stat-top">
								<span class="stat-number">{medCount}</span>
								<span class="stat-chip">💊 Meds</span>
							</div>
							<span class="stat-label">Active Prescriptions</span>
							<span class="stat-link">Manage medicines →</span>
						</a>

						<a href="/caregiver/calls" class="stat-box">
							<div class="stat-top">
								<span class="stat-number">{callCount}</span>
								<span class="stat-chip">☎ Calls</span>
							</div>
							<span class="stat-label">Vcare Calls Logged</span>
							<span class="stat-link">View call history →</span>
						</a>

						<div class="stat-box status-highlight">
							<div class="stat-top">
								<Badge variant="success" dot={true}>Active</Badge>
							</div>
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
		color: white;
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

	/* FRAUNCES DISPLAY SERIF ONLY HERE */
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
		text-decoration: none;
	}

	.btn-primary:hover:not(:disabled) {
		background: #08402a;
		transform: translateY(-1px);
	}

	.btn-primary:disabled {
		opacity: 0.7;
		cursor: not-allowed;
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
	   STATUS BANNER
	===================================================== */

	.status-banner {
		padding: 14px 20px;
		border-radius: var(--radius-md, 14px);
		margin-bottom: 22px;
		display: flex;
		align-items: center;
		gap: 12px;
		font-weight: 600;
		animation: slideDown 0.3s ease;
	}

	.status-banner.success {
		background: var(--color-success-bg, #e8f7ee);
		color: var(--color-success-text, #0f6e3c);
		border: 1px solid var(--color-success-border, #b7e8ca);
	}

	.status-banner.error {
		background: var(--color-danger-bg, #fdf0f0);
		color: var(--color-danger-text, #b91c1c);
		border: 1px solid var(--color-danger-border, #fecaca);
	}

	.status-banner p {
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
	   PROFILE CARDS & FORMS
	===================================================== */

	.profile-grid {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.card {
		background: var(--color-surface, #ffffff);
		border-radius: var(--radius-xl, 20px);
		padding: 28px 30px;
		border: 1px solid var(--color-border, #e2e8e0);
		box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
	}

	.card-header {
		display: flex;
		align-items: center;
		gap: 16px;
		margin-bottom: 24px;
		padding-bottom: 18px;
		border-bottom: 1px solid var(--color-border-subtle, #edf2eb);
	}

	/* SEMANTIC ICON CHIP SYSTEM */
	.card-icon {
		width: 44px;
		height: 44px;
		border-radius: var(--radius-md, 14px);
		display: grid;
		place-items: center;
		flex-shrink: 0;
	}

	.card-icon.personal {
		background: var(--color-success-bg, #e8f7ee);
		color: var(--color-brand-primary, #116240);
	}

	.card-icon.emergency {
		background: var(--color-warning-icon-bg, #fef3c7);
		color: var(--color-warning-icon, #b45309);
	}

	.card-icon.overview {
		background: var(--color-neutral-bg, #f1f4f2);
		color: var(--color-text-primary, #153d30);
	}

	.card-header h2 {
		margin: 0;
		font-size: 19px;
		font-weight: 700;
		color: var(--color-text-primary, #153d30);
	}

	.section-desc {
		margin: 3px 0 0;
		font-size: 13px;
		color: var(--color-text-secondary, #475569);
	}

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

	.field.full {
		grid-column: 1 / -1;
	}

	.field label {
		font-weight: 600;
		color: var(--color-text-primary, #153d30);
		font-size: 13px;
	}

	/* CUSTOM STYLED FORM CONTROLS (TEXT, DATE, SELECT) */
	.field input,
	.field select {
		width: 100%;
		padding: 12px 16px;
		border: 1px solid var(--color-border, #d9cdb8);
		border-radius: var(--radius-md, 12px);
		font-size: 14px;
		background: var(--color-surface, #ffffff);
		color: var(--color-text-body, #1e293b);
		outline: none;
		transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
		font-family: inherit;
	}

	.field input:focus,
	.field select:focus {
		border-color: var(--color-brand-primary, #116240);
		box-shadow: 0 0 0 3px rgba(17, 98, 64, 0.1);
	}

	/* Custom Styled Select with SVG Arrow */
	.select-wrapper {
		position: relative;
		width: 100%;
	}

	.select-wrapper select {
		appearance: none;
		-webkit-appearance: none;
		padding-right: 38px;
		cursor: pointer;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right 14px center;
	}

	.hint {
		font-size: 12px;
		color: var(--color-text-muted, #64748b);
	}

	/* =====================================================
	   REFERENCE SHIELD TRUST REASSURANCE BOX
	===================================================== */

	.security-badge {
		margin-top: 22px;
		background: var(--color-surface-tinted, #f4f7f2);
		border: 1px solid var(--color-border-subtle, #e2ebd0);
		border-radius: var(--radius-md, 14px);
		padding: 14px 18px;
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.security-badge-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-brand-primary, #116240);
		flex-shrink: 0;
	}

	.security-badge p {
		margin: 0;
		font-size: 13px;
		color: var(--color-text-secondary, #475569);
		line-height: 1.45;
	}

	/* =====================================================
	   CARE OVERVIEW STATS ROW (CONSISTENT CARDS)
	===================================================== */

	.stats-row {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 18px;
	}

	.stat-box {
		background: var(--color-surface, #ffffff);
		border: 1px solid var(--color-border, #e2e8e0);
		border-radius: var(--radius-lg, 16px);
		padding: 20px;
		display: flex;
		flex-direction: column;
		text-decoration: none;
		color: inherit;
		box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
		transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
	}

	.stat-box:hover {
		transform: translateY(-2px);
		border-color: var(--color-brand-light, #2c9a59);
		box-shadow: var(--shadow-md, 0 4px 14px rgba(23, 63, 49, 0.06));
	}

	.stat-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 8px;
	}

	.stat-number {
		font-size: 28px;
		font-weight: 700;
		color: var(--color-text-primary, #153d30);
		line-height: 1.1;
	}

	.stat-chip {
		font-size: 11px;
		font-weight: 600;
		padding: 3px 8px;
		border-radius: var(--radius-xs, 6px);
		background: var(--color-neutral-bg, #f1f4f2);
		color: var(--color-text-secondary, #475569);
	}

	.stat-label {
		font-size: 13px;
		font-weight: 600;
		color: var(--color-text-primary, #153d30);
		margin-top: 8px;
	}

	.stat-link {
		font-size: 12px;
		color: var(--color-brand-primary, #116240);
		font-weight: 600;
		margin-top: 10px;
	}

	.stat-box.status-highlight {
		border-color: var(--color-success-border, #b7e8ca);
		background: var(--color-surface-soft, #fbfdfb);
	}

	.stat-sub {
		font-size: 12px;
		color: var(--color-text-secondary, #475569);
		margin-top: 8px;
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
	}
</style>
