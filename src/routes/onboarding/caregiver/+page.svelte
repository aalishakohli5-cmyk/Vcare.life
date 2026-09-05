<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import { PUBLIC_BACKEND_URL } from '$env/static/public';
	import PhoneInput from '$lib/components/PhoneInput.svelte';
	import {
		careInviteErrorMessage,
		normalizeCareInviteCode,
		rememberCareRecipient
	} from '$lib/careConnections';

	/* =====================================================
	   CAREGIVER DATA
	   ===================================================== */

	let caregiverName = $state('');
	let email = $state('');
	let caregiverPhone = $state('');
	let caregiverCountryCode = $state('+91');
	let relationship = $state('');

	let seniorName = $state('');
	let seniorPhone = $state('');
	let seniorCountryCode = $state('+91');
	let inviteCode = $state('');

	let step = $state(1);
	let loading = $state(true);
	let saving = $state(false);
	let errorMessage = $state('');

	/* =====================================================
	   ANIMATED PHONE
	   ===================================================== */

	let phoneDropped = $state(false);

	function togglePhone() {
		phoneDropped = !phoneDropped;
	}

	/* =====================================================
	   COUNTRY DATA
	===================================================== */

	const countryCodes = [
		{ country: 'India', flag: '🇮🇳', code: '+91' },
		{ country: 'United States', flag: '🇺🇸', code: '+1' },
		{ country: 'United Kingdom', flag: '🇬🇧', code: '+44' },
		{ country: 'Canada', flag: '🇨🇦', code: '+1' },
		{ country: 'Australia', flag: '🇦🇺', code: '+61' },
		{ country: 'UAE', flag: '🇦🇪', code: '+971' },
		{ country: 'Singapore', flag: '🇸🇬', code: '+65' },
		{ country: 'Germany', flag: '🇩🇪', code: '+49' },
		{ country: 'France', flag: '🇫🇷', code: '+33' },
		{ country: 'Japan', flag: '🇯🇵', code: '+81' },
		{ country: 'South Korea', flag: '🇰🇷', code: '+82' },
		{ country: 'China', flag: '🇨🇳', code: '+86' },
		{ country: 'New Zealand', flag: '🇳🇿', code: '+64' },
		{ country: 'Italy', flag: '🇮🇹', code: '+39' },
		{ country: 'Spain', flag: '🇪🇸', code: '+34' },
		{ country: 'Netherlands', flag: '🇳🇱', code: '+31' },
		{ country: 'Switzerland', flag: '🇨🇭', code: '+41' },
		{ country: 'Saudi Arabia', flag: '🇸🇦', code: '+966' },
		{ country: 'Qatar', flag: '🇶🇦', code: '+974' },
		{ country: 'Malaysia', flag: '🇲🇾', code: '+60' }
	];

	/* =====================================================
	   CAREGIVER COUNTRY PICKER
	===================================================== */

	let caregiverCountryCode = $state('+91');
	let caregiverCountrySearch = $state('');
	let caregiverCountryDropdownOpen = $state(false);

	let filteredCaregiverCountries = $derived(
		countryCodes.filter(
			(item) =>
				item.country
					.toLowerCase()
					.includes(caregiverCountrySearch.toLowerCase()) ||
				item.code.includes(caregiverCountrySearch)
		)
	);

	/** @param {{ code: string }} item */
	function selectCaregiverCountry(item) {
		caregiverCountryCode = item.code;
		caregiverCountrySearch = '';
		caregiverCountryDropdownOpen = false;
	}

	/* =====================================================
	   AUTH
	   ===================================================== */

	onMount(async () => {
		const {
			data: { user }
		} = await supabase.auth.getUser();

		if (!user) {
			goto('/auth?role=caregiver');
			return;
		}

		email = user.email ?? '';

		caregiverName =
			user.user_metadata?.full_name ??
			user.user_metadata?.name ??
			'';

		loading = false;
	});

	/* =====================================================
	   HELPERS
	   ===================================================== */

	/** @param {string} value */
	function cleanPhone(value) {
		return (value || '').replace(/\D/g, '');
	}

	function nextStep() {
		errorMessage = '';

		if (!caregiverName.trim()) {
			errorMessage = 'Please enter your name.';
			return;
		}

		if (!caregiverPhone.trim()) {
			errorMessage = 'Please enter your phone number.';
			return;
		}

		if (!relationship.trim()) {
			errorMessage =
				'Please tell us your relationship to the senior.';
			return;
		}

		step = 2;
	}

	function previousStep() {
		errorMessage = '';
		step = 1;
	}

	/* =====================================================
	   SAVE CAREGIVER
	   ===================================================== */

	async function finishSetup() {
		errorMessage = '';

		if (!seniorName.trim()) {
			errorMessage =
				'Please enter the name of the senior you care for.';
			return;
		}

		if (!seniorPhone.trim()) {
			errorMessage =
				'Please enter the senior’s phone number.';
		const normalizedCode = normalizeCareInviteCode(inviteCode);
		if (!/^VCARE-[A-Z0-9]{6}$/.test(normalizedCode)) {
			errorMessage = 'Enter the complete invitation code, for example VCARE-ABC123.';
			return;
		}

		saving = true;

		const {
			data: { user },
			error: userError
		} = await supabase.auth.getUser();

		if (userError || !user) {
			saving = false;
			errorMessage =
				'Your session expired. Please sign in again.';
			return;
		}

		const fullCaregiverPhone =
			`${caregiverCountryCode}${cleanPhone(caregiverPhone)}`;

		// Save the caregiver account first; the code securely identifies the senior.
		const { error } = await supabase
			.from('profiles')
			.upsert({
				id: user.id,
				role: 'caregiver',
				full_name: caregiverName.trim(),
				email: user.email,
				phone: fullCaregiverPhone,
				emergency_contact_name: seniorName.trim(),
				emergency_contact_relationship: relationship.trim(),
				emergency_contact_phone: fullSeniorPhone,

				onboarding_complete: true,
				updated_at: new Date().toISOString()
			});

		if (error) {
			console.error(error);
			saving = false;
			errorMessage =
				'Your caregiver profile could not be saved yet. Please try again.';
			return;
		}

		const { data: connection, error: connectionError } = await supabase.rpc(
			'redeem_care_invite',
			{ invite_code: normalizedCode, relationship_to_senior: relationship.trim() }
		);

		// Direct Supabase fallback
		if (!onboardSuccess) {
			try {
				const { data: existingSenior } = await supabase
					.from('profiles')
					.select('id')
					.eq('phone', fullSeniorPhone)
					.maybeSingle();

				if (existingSenior) {
					await supabase.from('caregiver_links').upsert({
						caregiver_id: user.id,
						senior_id: existingSenior.id
					}, { onConflict: 'caregiver_id,senior_id' });
				}
			} catch (e) {
				console.warn('Supabase link fallback error:', e);
			}
		if (connectionError || !connection?.[0]?.senior_id) {
			saving = false;
			errorMessage = careInviteErrorMessage(connectionError, 'redeem');
			return;
		}

		rememberCareRecipient(connection[0].senior_id);
		goto('/caregiver/dashboard');
	}
</script>

<svelte:head>
	<title>Set up your caregiver profile — Vcare.life</title>
</svelte:head>

{#if loading}
	<div class="loading-screen">
		<div class="loading-heart">♥</div>
		<h2>Getting Vcare ready...</h2>
	</div>
{:else}
	<main class="onboarding">
		<!-- =====================================================
		     LEFT PANEL
		     ===================================================== -->
		<aside class="left-panel">
			<!-- BRAND -->
			<a href="/" class="brand">
				<div class="brand-heart">♥</div>
				<div>
					<strong>Vcare.life</strong>
					<span>A Voice That Cares</span>
				</div>
			</a>

			<!-- RETRO PHONE ILLUSTRATION (TONED DOWN PALETTE, NO COLLISION) -->
			<button
				type="button"
				class="phone-area"
				class:dropped={phoneDropped}
				onclick={togglePhone}
				aria-label="Toggle Vcare retro phone receiver"
				title="Click receiver to test line"
			>
				<div class="cord">
					<div class="cord-line"></div>
					<div class="cord-curl curl-one"></div>
					<div class="cord-curl curl-two"></div>
					<div class="cord-curl curl-three"></div>
				</div>

				<div class="hook">●</div>

				<div class="retro-phone">
					<div class="speaker">
						<span></span>
						<span></span>
						<span></span>
						<span></span>
						<span></span>
					</div>

					<div class="phone-screen">
						<small>VCARE CALLING</small>
						<strong>
							{phoneDropped ? 'Pick me up!' : 'Hello there'}
						</strong>
						<span>♥</span>
					</div>

					<div class="phone-buttons">
						<div class="call">☎</div>
						<div class="circle-control">
							<span>‹</span>
							<b>●</b>
							<span>›</span>
						</div>
						<div class="hang">×</div>
					</div>

					<div class="numbers">
						<span>1</span><span>2</span><span>3</span>
						<span>4</span><span>5</span><span>6</span>
						<span>7</span><span>8</span><span>9</span>
						<span>*</span><span>0</span><span>#</span>
					</div>
				</div>
			</button>

			<!-- INTERACTIVE EASTER EGG STATUS BADGE -->
			<div class="phone-status-pill" class:active={phoneDropped}>
				<span class="pulse-dot">●</span>
				<span>{phoneDropped ? 'Receiver off hook (tap to hang up)' : 'Interactive: tap receiver to test'}</span>
			</div>

			<!-- LEFT TEXT -->
			<div class="left-content">
				<p class="left-eyebrow">CARE THAT STAYS CLOSE</p>

				<h1>
					Stay close,
					<br />
					even when
					<br />
					<span>you're away.</span>
				</h1>

				<p class="left-description">
					Vcare helps you stay connected with someone you care for — through
					medication support, check-ins, and meaningful updates.
				</p>

				<!-- STEPS -->
				<div class="side-steps">
					<div
						class:active={step === 1}
						class:complete={step > 1}
					>
						<span>{step > 1 ? '✓' : '1'}</span>
						<div>
							<strong>About you</strong>
							<p>Your caregiver information</p>
						</div>
					</div>

					<div class:active={step === 2}>
						<span>2</span>
						<div>
							<strong>Senior profile</strong>
							<p>The person you're caring for</p>

							<strong>Connect securely</strong>

							<p>
								Enter their invitation code
							</p>

						</div>
					</div>
				</div>
			</div>
		</aside>

		<!-- =====================================================
		     RIGHT PANEL
		     ===================================================== -->
		<section class="right-panel">
			<div class="form-card">
				<!-- TOPBAR -->
				<header class="topbar">
					<div>
						<p>STEP {step} OF 2</p>
						<div class="progress">
							<span class:filled={step >= 1}></span>
							<span class:filled={step >= 2}></span>
						</div>
					</div>

					<div class="secure-pill">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="15"
							height="15"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							aria-hidden="true"
						>
							<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
							<path d="m9 12 2 2 4-4" />
						</svg>
						<span>Private &amp; secure</span>
					</div>
				</header>

				<!-- STEP 1: CAREGIVER INFO -->
				{#if step === 1}
					<section class="form-section">
						<p class="welcome">WELCOME TO VCARE</p>
						<h2>
							Tell us a little
							<span>about you.</span>
						</h2>
						<p class="subtitle">
							We'll use this to personalise your caregiver experience and
							keep you connected with the person you care for.
						</p>

						<div class="fields">
							<div class="field full">
								<label for="caregiverName">Full name</label>
								<div class="input-shell">
									<input
										id="caregiverName"
										type="text"
										bind:value={caregiverName}
										placeholder="What should Vcare call you?"
									/>
									<span class="input-icon" aria-hidden="true">☺</span>
								</div>
							</div>

							<div class="field full">
								<label for="email">Email</label>
								<input
									id="email"
									type="email"
									value={email}
									disabled
								/>
								<small class="connected">
									✓ Connected through your Google account
								</small>
							</div>

							<div class="field">
								<label for="caregiverPhone">Phone number</label>
								<PhoneInput
									id="caregiverPhone"
									bind:value={caregiverPhone}
									bind:countryCode={caregiverCountryCode}
									placeholder="Phone number"
								/>
							</div>

							<div class="field">
								<label for="relationship">Relationship to senior</label>
								<input
									id="relationship"
									type="text"
									bind:value={relationship}
									placeholder="e.g. Daughter"
								/>
							</div>

							<div class="message-card">
								<div class="message-icon" aria-hidden="true">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										width="20"
										height="20"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<circle cx="12" cy="12" r="10" />
										<path d="m9 12 2 2 4-4" />
									</svg>
								</div>
								<section>
									<strong>One place to stay connected.</strong>
									<p>
										See medication and Vcare check-in updates without needing
										to be there every moment.
									</p>
								</section>
							</div>
						</div>
					</section>
				{/if}

				<!-- STEP 2: SENIOR PROFILE -->
				{#if step === 2}
					<section class="form-section">
						<p class="welcome">YOUR SENIOR</p>
						<h2>
							Who are you
							<span>caring for?</span>

					<p class="welcome">PRIVATE CONNECTION</p>


						<h2>

							Enter your <span>invitation code.</span>

						</h2>
						<p class="subtitle">
							Add the person you'd like Vcare to check in with and
							help you stay connected to.

							Ask the senior to open Care Circle and generate a code. No email or phone search is needed.

						</p>

						<div class="fields">
							<div class="field full">
								<label for="seniorName">Senior's name</label>
								<div class="input-shell">
									<input
										id="seniorName"
										type="text"
										bind:value={seniorName}
										placeholder="e.g. Shanta Devi"
									/>
									<span class="input-icon" aria-hidden="true">♥</span>
								</div>
							</div>

							<div class="field full">
								<label for="seniorPhone">Senior's phone number</label>
								<PhoneInput
									id="seniorPhone"
									bind:value={seniorPhone}
									bind:countryCode={seniorCountryCode}
									placeholder="Phone number"
								/>


							<div class="field full">
								<label for="inviteCode">Vcare invitation code</label>
								<div class="input-shell">
									<input id="inviteCode" type="text" bind:value={inviteCode} placeholder="VCARE-ABC123" autocomplete="one-time-code" spellcheck="false" maxlength="12" />
									<span class="input-icon">♡</span>
								</div>
								<small class="connected">Codes work once and expire after 15 minutes.</small>
							</div>

							<div class="message-card ready">
								<div class="message-icon ready-icon" aria-hidden="true">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										width="20"
										height="20"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2"
										stroke-linecap="round"
										stroke-linejoin="round"
									>
										<path
											d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"
										/>
									</svg>
								</div>
								<section>
									<strong>You're ready!</strong>
									<p>
										Vcare can now help you stay close to the person you care for.
									After the code is confirmed, both portals will use the same senior profile and care information.
									</p>
								</section>
							</div>
						</div>
					</section>
				{/if}

				<!-- ERROR -->
				{#if errorMessage}
					<div class="error-message">
						⚠ {errorMessage}
					</div>
				{/if}

				<!-- BUTTONS -->
				<footer class="actions">
					{#if step > 1}
						<button
							class="back-button"
							type="button"
							onclick={previousStep}
						>
							← Back
						</button>
					{:else}
						<span></span>
					{/if}

					{#if step < 2}
						<button
							class="continue-button"
							type="button"
							onclick={nextStep}
						>
							<span>Continue</span>
							<span class="arrow">→</span>
						</button>
					{:else}
						<button
							class="continue-button"
							type="button"
							onclick={finishSetup}
							disabled={saving}
						>
							<span>{saving ? 'Preparing Vcare...' : 'Enter my Vcare'}</span>
							<span class="arrow">→</span>

							{saving ? 'Connecting…' : 'Connect & enter Vcare'}

							<span>
								→
							</span>

						</button>
					{/if}
				</footer>

				<p class="privacy-note">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="15"
						height="15"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
					>
						<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
						<path d="m9 12 2 2 4-4" />
					</svg>
					<span>Your information stays yours.</span>
				</p>
			</div>
		</section>
	</main>
{/if}

<style>
	:global(*) {
		box-sizing: border-box;
	}

	:global(html) {
		margin: 0;
		width: 100%;
		min-height: 100%;
	}

	button,
	input {
		font-family: inherit;
	}

	.loading-screen {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		gap: 15px;
		background: #f9f0e0;
		color: #176146;
	}

	.loading-heart {
		font-size: 58px;
		animation: beat 1.2s ease-in-out infinite;
	}

	@keyframes beat {
		50% {
			transform: scale(1.18);
		}
	}

	.onboarding {
		min-height: 100vh;
		display: grid;
		grid-template-columns: minmax(460px, 40%) 1fr;
		background: #f9f0e0;
	}

	.left-panel {
		position: sticky;
		top: 0;
		height: 100vh;
		max-height: 100vh;
		overflow-y: auto;
		overflow-x: hidden;
		padding: 36px 38px 32px;
		color: #ffffff;
		background:
			radial-gradient(
				circle at 85% 20%,
				rgba(30, 95, 62, 0.45),
				transparent 45%
			),
			linear-gradient(
				155deg,
				#073524 0%,
				#0c4d34 45%,
				#083c2a 100%
			);
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		box-sizing: border-box;
	}

	.left-panel::after {
		content: '';
		position: absolute;
		z-index: 15;
		top: -3%;
		right: -31px;
		width: 62px;
		height: 106%;
		border-radius: 50%;
		background: #f9f0e0;
		pointer-events: none;
	}

	.brand {
		position: relative;
		z-index: 25;
		display: flex;
		align-items: center;
		gap: 12px;
		width: fit-content;
		color: white;
		text-decoration: none;
	}

	.brand-heart {
		width: 48px;
		height: 48px;
		display: grid;
		place-items: center;
		border-radius: 14px;
		background: #ffffff;
		color: #0b6142;
		font-size: 24px;
	}

	.brand > div:last-child {
		display: flex;
		flex-direction: column;
	}

	.brand strong {
		font-size: 24px;
		line-height: 1;
	}

	.brand span {
		margin-top: 4px;
		font-size: 12px;
		color: rgba(255, 255, 255, 0.82);
	}

	/* RETRO PHONE */
	.phone-area {
		position: absolute;
		z-index: 4;
		top: 14px;
		right: 22px;
		width: 156px;
		height: 380px;
		padding: 0;
		border: 0;
		outline: 0;
		background: transparent;
		cursor: pointer;
		transform-origin: top center;
		animation: swing 4.5s ease-in-out infinite;
	}

	.phone-area:hover .retro-phone {
		filter: brightness(1.05);
	}

	@keyframes swing {
		0%,
		100% {
			transform: rotate(-1.5deg);
		}
		50% {
			transform: rotate(1.5deg);
		}
	}

	.phone-area.dropped {
		animation: dropPhone 0.85s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
	}

	@keyframes dropPhone {
		0% {
			transform: translateY(0) rotate(0deg);
		}
		35% {
			transform: translateY(80px) rotate(7deg);
		}
		70% {
			transform: translateY(125px) rotate(-4deg);
		}
		100% {
			transform: translateY(105px) rotate(2deg);
		}
	}

	.cord {
		position: absolute;
		left: 50%;
		top: 0;
		width: 26px;
		height: 90px;
		transform: translateX(-50%);
	}

	.cord-line {
		position: absolute;
		left: 50%;
		top: 0;
		width: 4px;
		height: 42px;
		transform: translateX(-50%);
		border-radius: 10px;
		background: #48735a;
	}

	.cord-curl {
		position: absolute;
		left: 50%;
		width: 17px;
		height: 17px;
		transform: translateX(-50%);
		border: 3px solid #48735a;
		border-left-color: transparent;
		border-radius: 50%;
	}

	.curl-one {
		top: 34px;
	}

	.curl-two {
		top: 48px;
		transform: translateX(-50%) rotate(180deg);
	}

	.curl-three {
		top: 62px;
	}

	.hook {
		position: absolute;
		z-index: 5;
		top: 76px;
		left: 50%;
		transform: translateX(-50%);
		width: 22px;
		height: 22px;
		display: grid;
		place-items: center;
		border-radius: 50%;
		border: 3px solid #0f3b28;
		background: #507d64;
		color: #ffffff;
		font-size: 7px;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
	}

	.retro-phone {
		position: absolute;
		top: 94px;
		left: 50%;
		transform: translateX(-50%);
		width: 144px;
		padding: 12px 10px 14px;
		border: 4px solid #0d3322;
		border-radius: 32px 32px 26px 26px;
		background: linear-gradient(
			155deg,
			#1d523b 0%,
			#153f2c 60%,
			#0d2b1e 100%
		);
		box-shadow:
			0 16px 28px rgba(0, 24, 15, 0.45),
			inset 1px 1px 3px rgba(255, 255, 255, 0.15);
		transition: filter 0.2s ease;
	}

	.speaker {
		width: 86px;
		height: 19px;
		margin: 0 auto 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 4px;
		border-radius: 10px;
		background: #0d2d1e;
	}

	.speaker span {
		width: 3px;
		height: 3px;
		border-radius: 50%;
		background: #6e997e;
	}

	.phone-screen {
		height: 80px;
		padding: 7px 6px;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		border: 3.5px solid #0b291a;
		border-radius: 14px;
		background: linear-gradient(150deg, #faf7ee, #f0ebd9);
		color: #0b3d2b;
		box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.06);
	}

	.phone-screen small {
		font-size: 8px;
		font-weight: 700;
		letter-spacing: 0.06em;
		color: #3b614d;
	}

	.phone-screen strong {
		margin-top: 4px;
		font-size: 13px;
		font-weight: 700;
		color: #0b3d2b;
	}

	.phone-screen > span {
		margin-top: 2px;
		font-size: 14px;
		color: #b45309;
	}

	.phone-buttons {
		margin: 8px 0 7px;
		display: flex;
		align-items: center;
		justify-content: space-around;
	}

	.call,
	.hang {
		width: 26px;
		height: 20px;
		display: grid;
		place-items: center;
		border-radius: 12px;
		color: white;
		font-size: 10px;
		font-weight: bold;
	}

	.call {
		background: #15803d;
	}

	.hang {
		background: #b91c1c;
	}

	.circle-control {
		width: 36px;
		height: 36px;
		display: flex;
		align-items: center;
		justify-content: space-around;
		border-radius: 50%;
		background: #ebe6d3;
		color: #1b4230;
		box-shadow: 0 1.5px 3px rgba(0, 0, 0, 0.2);
		font-size: 10px;
	}

	.circle-control b {
		width: 11px;
		height: 11px;
		display: grid;
		place-items: center;
		border-radius: 50%;
		background: #ffffff;
		font-size: 5px;
	}

	.numbers {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 4px;
	}

	.numbers span {
		height: 17px;
		display: grid;
		place-items: center;
		border-radius: 5px;
		background: #f4efdb;
		color: #123824;
		font-size: 9px;
		font-weight: bold;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
	}

	.phone-status-pill {
		position: absolute;
		top: 404px;
		right: 18px;
		z-index: 6;
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 6px 12px;
		border-radius: 20px;
		background: rgba(255, 255, 255, 0.12);
		border: 1px solid rgba(255, 255, 255, 0.18);
		backdrop-filter: blur(8px);
		color: rgba(255, 255, 255, 0.9);
		font-size: 11px;
		font-weight: 500;
	}

	.phone-status-pill .pulse-dot {
		color: #86efac;
		font-size: 8px;
		animation: blink 1.8s ease-in-out infinite;
	}

	@keyframes blink {
		0%,
		100% {
			opacity: 0.4;
		}
		50% {
			opacity: 1;
		}
	}

	/* LEFT CONTENT */
	.left-content {
		position: relative;
		z-index: 10;
		width: 100%;
		max-width: 420px;
		margin-top: 28px;
		margin-bottom: auto;
	}

	.left-eyebrow {
		margin: 0 0 12px;
		color: #a8d5b8;
		font-size: 12.5px;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	.left-content h1 {
		margin: 0;
		color: #ffffff;
		font-family: var(--font-display, 'Fraunces', Georgia, serif);
		font-size: clamp(34px, 3.4vw, 44px);
		line-height: 1.12;
		letter-spacing: -0.02em;
		font-weight: 500;
	}

	.left-content h1 span {
		color: #d1e784;
		font-style: italic;
	}

	.left-description {
		max-width: 360px;
		margin: 16px 0 22px;
		color: rgba(255, 255, 255, 0.88);
		font-size: 14.5px;
		line-height: 1.55;
	}

	/* SIDE STEPS */
	.side-steps {
		display: grid;
		gap: 10px;
	}

	.side-steps > div {
		min-height: 62px;
		padding: 10px 14px;
		display: grid;
		grid-template-columns: 42px 1fr;
		gap: 12px;
		align-items: center;
		border: 1px solid rgba(255, 255, 255, 0.12);
		border-radius: 15px;
		background: rgba(255, 255, 255, 0.06);
		opacity: 0.65;
		transition: 0.22s ease;
	}

	.side-steps > div.active {
		opacity: 1;
		transform: translateX(6px);
		background: rgba(255, 255, 255, 0.14);
		border-color: rgba(209, 231, 132, 0.35);
	}

	.side-steps > div.complete {
		opacity: 0.9;
	}

	.side-steps > div > span {
		width: 38px;
		height: 38px;
		display: grid;
		place-items: center;
		border-radius: 11px;
		background: rgba(209, 231, 132, 0.24);
		color: #f7f9d8;
		font-size: 15px;
		font-weight: bold;
	}

	.side-steps strong {
		display: block;
		color: white;
		font-size: 14.5px;
	}

	.side-steps p {
		margin: 2px 0 0;
		color: rgba(255, 255, 255, 0.72);
		font-size: 12px;
	}

	/* RIGHT PANEL & FORM CARD */
	.right-panel {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 42px 40px;
	}

	.form-card {
		width: 100%;
		max-width: 720px;
		padding: 34px 40px 28px;
		border: 1px solid #ead9b7;
		border-radius: 30px;
		background: rgba(255, 248, 235, 0.72);
		box-shadow: 0 20px 50px rgba(105, 76, 30, 0.07);
	}

	.topbar {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		margin-bottom: 34px;
	}

	.topbar p {
		margin: 0 0 8px;
		color: var(--color-brand-primary, #116240);
		font-size: 13.5px;
		font-weight: 700;
		letter-spacing: 0.06em;
	}

	.progress {
		display: flex;
		gap: 8px;
	}

	.progress span {
		width: 58px;
		height: 5px;
		border-radius: 10px;
		background: #e5d4b4;
		transition: background 0.25s ease;
	}

	.progress span.filled {
		background: var(--color-brand-primary, #116240);
	}

	.secure-pill {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 7px 14px;
		border-radius: 50px;
		background: var(--color-surface-tinted, #f0f4ea);
		border: 1px solid var(--color-border-subtle, #dce6cf);
		color: var(--color-brand-primary, #116240);
		font-size: 12.5px;
		font-weight: 600;
	}

	.welcome {
		margin: 0 0 8px;
		color: var(--color-brand-primary, #116240);
		font-size: 13px;
		font-weight: 700;
		letter-spacing: 0.06em;
		text-transform: uppercase;
	}

	.form-section h2 {
		margin: 0;
		color: var(--color-text-primary, #124c37);
		font-size: clamp(36px, 3.2vw, 48px);
		line-height: 1.08;
		letter-spacing: -0.035em;
	}

	.form-section h2 span {
		color: #6c983f;
	}

	.subtitle {
		max-width: 620px;
		margin: 12px 0 26px;
		color: var(--color-text-secondary, #475569);
		font-size: 15px;
		line-height: 1.55;
	}

	.fields {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 18px 16px;
	}

	.field {
		display: flex;
		flex-direction: column;
	}

	.field.full {
		grid-column: 1 / -1;
	}

	label {
		margin-bottom: 7px;
		color: #342c23;
		font-size: 14.5px;
		font-weight: 600;
	}

	input[type='text'],
	input[type='email'] {
		width: 100%;
		height: 56px;
		padding: 0 16px;
		border: 1.5px solid var(--color-border, #decdb0);
		border-radius: var(--radius-md, 14px);
		outline: none;
		background: var(--color-surface, #ffffff);
		color: var(--color-text-body, #1e293b);
		font-size: 15px;
		font-family: inherit;
		transition:
			border-color 0.18s ease,
			box-shadow 0.18s ease;
		box-sizing: border-box;
	}

	input:hover {
		border-color: #b8b47c;
	}

	input:focus {
		border-color: var(--color-brand-primary, #116240);
		box-shadow: 0 0 0 3px rgba(17, 98, 64, 0.12);
	}

	input:disabled {
		background: rgba(224, 215, 199, 0.35);
		color: #716b63;
		cursor: not-allowed;
	}

	.input-shell {
		position: relative;
	}

	.input-shell input {
		padding-right: 48px;
	}

	.input-icon {
		position: absolute;
		right: 16px;
		top: 50%;
		transform: translateY(-50%);
		font-size: 19px;
		color: #64748b;
	}

	.connected {
		margin-top: 6px;
		color: var(--color-brand-accent, #2e6930);
		font-size: 12px;
		font-weight: 600;
	}

	/* REASSURANCE CARDS */
	.message-card {
		grid-column: 1 / -1;
		padding: 16px 18px;
		display: flex;
		gap: 14px;
		align-items: center;
		border: 1px solid var(--color-border-subtle, #d8e5c8);
		border-radius: var(--radius-md, 14px);
		background: var(--color-surface-tinted, #f4f7f2);
	}

	.message-card.ready {
		background: rgba(217, 119, 6, 0.07);
		border-color: rgba(217, 119, 6, 0.24);
	}

	.message-icon {
		width: 42px;
		height: 42px;
		display: grid;
		place-items: center;
		flex-shrink: 0;
		border-radius: 12px;
		background: rgba(17, 98, 64, 0.12);
		color: var(--color-brand-primary, #116240);
	}

	.ready-icon {
		background: rgba(217, 119, 6, 0.14);
		color: #b45309;
	}

	.message-card strong {
		font-size: 14.5px;
		font-weight: 600;
		color: var(--color-text-primary, #0b3d2b);
	}

	.message-card.ready strong {
		color: #92400e;
	}

	.message-card p {
		margin: 3px 0 0;
		color: var(--color-text-secondary, #475569);
		font-size: 13px;
		line-height: 1.5;
	}

	.error-message {
		margin-top: 18px;
		padding: 12px 16px;
		border-radius: 12px;
		background: #ffe4dc;
		color: #991b1b;
		font-size: 13.5px;
		font-weight: 500;
	}

	.actions {
		margin-top: 28px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 14px;
	}

	.back-button {
		height: 52px;
		padding: 0 20px;
		border: 1.5px solid #ddcba9;
		border-radius: 14px;
		background: rgba(255, 255, 255, 0.5);
		color: #365b46;
		cursor: pointer;
		font-size: 14.5px;
		font-weight: 600;
		transition: background 0.15s ease;
	}

	.back-button:hover {
		background: rgba(255, 255, 255, 0.8);
	}

	.continue-button {
		min-width: 200px;
		height: 56px;
		padding: 0 22px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		border: 0;
		border-radius: 14px;
		background: linear-gradient(
			135deg,
			var(--color-brand-primary, #116240),
			#147a50
		);
		color: white;
		cursor: pointer;
		font-size: 16px;
		font-weight: 600;
		box-shadow: 0 12px 26px rgba(17, 98, 64, 0.2);
		transition:
			transform 0.18s ease,
			box-shadow 0.18s ease;
	}

	.continue-button:hover:not(:disabled) {
		transform: translateY(-2px);
		box-shadow: 0 16px 32px rgba(17, 98, 64, 0.28);
	}

	.continue-button .arrow {
		font-size: 20px;
		transition: transform 0.18s ease;
	}

	.continue-button:hover:not(:disabled) .arrow {
		transform: translateX(4px);
	}

	.continue-button:disabled {
		opacity: 0.65;
		cursor: wait;
	}

	.privacy-note {
		margin: 22px 0 0;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 6px;
		color: var(--color-text-secondary, #64748b);
		font-size: 12.5px;
	}

	@media (max-width: 1024px) {
		.onboarding {
			grid-template-columns: 1fr;
		}

		.left-panel {
			position: relative;
			height: auto;
			min-height: auto;
			max-height: none;
			padding: 32px 28px;
		}

		.left-panel::after {
			display: none;
		}

		.left-content {
			max-width: 100%;
			margin-top: 24px;
		}

		.phone-area {
			right: 20px;
		}

		.right-panel {
			min-height: auto;
			padding: 48px 24px;
		}
	}

	@media (max-width: 640px) {
		.left-panel {
			padding: 24px 18px;
		}

		.brand-heart {
			width: 40px;
			height: 40px;
			font-size: 20px;
		}

		.brand strong {
			font-size: 20px;
		}

		.phone-area {
			display: none;
		}

		.phone-status-pill {
			display: none;
		}

		.left-content {
			margin-top: 20px;
		}

		.left-content h1 {
			font-size: 32px;
		}

		.side-steps {
			display: none;
		}

		.right-panel {
			padding: 24px 14px 48px;
		}

		.form-card {
			padding: 24px 18px;
			border-radius: 20px;
		}

		.form-section h2 {
			font-size: 30px;
		}

		.fields {
			grid-template-columns: 1fr;
		}

		.field.full,
		.message-card {
			grid-column: auto;
		}

		.continue-button {
			min-width: 160px;
			font-size: 15px;
		}
	}
</style>
