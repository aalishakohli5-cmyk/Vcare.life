<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';
	import { careInviteErrorMessage } from '$lib/careConnections';

	/** @type {Array<{linkId: number, id: string, name: string, relation: string, phone: string, initial: string, primary: boolean}>} */
	let caregivers = $state([]);
	let loading = $state(true);
	let formError = $state('');
	let inviteCode = $state('');
	let inviteExpiresAt = $state('');
	let generating = $state(false);
	let copyLabel = $state('Copy code');

	onMount(loadCareCircle);

	async function loadCareCircle() {
		loading = true;
		formError = '';

		const { data: { user } } = await supabase.auth.getUser();
		if (!user) {
			goto('/auth?role=senior');
			return;
		}

		const { data: links, error: linksError } = await supabase
			.from('caregiver_links')
			.select('id, caregiver_id, relationship, created_at')
			.eq('senior_id', user.id)
			.order('created_at', { ascending: true });

		if (linksError) {
			formError = 'We could not load your Care Circle. Please try again.';
			loading = false;
			return;
		}

		const caregiverIds = (links || []).map((link) => link.caregiver_id);
		if (caregiverIds.length === 0) {
			caregivers = [];
			loading = false;
			return;
		}

		const { data: profiles, error: profilesError } = await supabase
			.from('profiles')
			.select('id, full_name, phone')
			.in('id', caregiverIds);

		if (profilesError) {
			formError = 'We found your connections but could not load their profiles.';
			loading = false;
			return;
		}

		caregivers = (links || []).map((link) => {
			const profile = (profiles || []).find((person) => person.id === link.caregiver_id);
			const displayName = profile?.full_name || 'Caregiver';
			return {
				linkId: link.id,
				id: link.caregiver_id,
				name: displayName,
				relation: link.relationship || 'Trusted caregiver',
				phone: profile?.phone || '',
				initial: displayName.charAt(0).toUpperCase(),
				primary: false
			};
		});

		loading = false;
	}

	function goBack() {
		goto('/senior/dashboard');
	}

	async function generateInvite() {
		generating = true;
		formError = '';
		copyLabel = 'Copy code';

		const { data, error } = await supabase.rpc('generate_care_invite');
		generating = false;

		if (error || !data?.[0]?.code) {
			formError = careInviteErrorMessage(error, 'generate');
			return;
		}

		inviteCode = data[0].code;
		inviteExpiresAt = data[0].expires_at;
	}

	async function copyInvite() {
		if (!inviteCode) return;
		try {
			await navigator.clipboard.writeText(inviteCode);
			copyLabel = 'Copied!';
		} catch {
			formError = 'Copying was blocked. Select the code and copy it manually.';
		}
	}

	/** @param {string} value */
	function inviteExpiryLabel(value) {
		if (!value) return '';
		return new Intl.DateTimeFormat(undefined, {
			hour: 'numeric',
			minute: '2-digit',
			timeZoneName: 'short'
		}).format(new Date(value));
	}

	/** @param {number} linkId @param {string} name */
	async function removeCaregiver(linkId, name) {
		if (!window.confirm(`Remove ${name} from your Care Circle?`)) return;

		const { error } = await supabase.from('caregiver_links').delete().eq('id', linkId);
		if (error) {
			formError = 'This caregiver could not be removed. Please try again.';
			return;
		}

		caregivers = caregivers.filter((caregiver) => caregiver.linkId !== linkId);
	}
</script>

<svelte:head>
	<title>Care Circle — Vcare.life</title>
</svelte:head>

<div class="page">
	<main class="content">

		<!-- HERO -->

		<section class="hero">

			<div>
				<p class="eyebrow">
					YOUR PEOPLE
				</p>

				<h1>
					Your <span>Care Circle.</span>
				</h1>

				<p class="hero-copy">
					The people you trust, kept close when
					something needs their attention.
				</p>
			</div>

			<div class="summary-card">

				<div class="summary-icon">
					♡
				</div>

				<div>
					<strong>{caregivers.length}</strong>

					<span>
						{caregivers.length === 1
							? 'trusted person'
							: 'trusted people'}
					</span>
				</div>

			</div>

		</section>


		<!-- INFO STRIP -->

		<section class="care-strip">

			<div class="strip-icon">
				♡
			</div>

			<div>
				<strong>
					People who matter, when it matters.
				</strong>

				<p>
					Vcare can keep your chosen people connected
					and ready to help when needed.
				</p>
			</div>

			<div class="strip-decoration">
				♡
			</div>

		</section>


		<!-- MAIN CARD -->

		<section class="care-card">

			<div class="section-header">

				<div>
					<p class="eyebrow">
						MY CARE CIRCLE
					</p>

					<h2>
						Trusted people
					</h2>

					<p>
						Manage the people Vcare can keep close.
					</p>
				</div>

				<button
					class="add-button"
					onclick={generateInvite}
					disabled={generating}
				>
					{generating ? 'Creating code…' : '＋ Invite caregiver'}
				</button>

			</div>


			{#if inviteCode}

				<section class="add-panel invite-panel" aria-labelledby="invite-heading">

					<div class="form-heading">

						<div class="form-symbol">
							♡
						</div>

						<div>
							<strong id="invite-heading">Share this one-time code</strong>

							<p>
								Your caregiver enters it on their dashboard. It expires at {inviteExpiryLabel(inviteExpiresAt)}.
							</p>
						</div>

					</div>


					<div class="invite-code" aria-label={`Invitation code ${inviteCode}`}>{inviteCode}</div>


					<div class="form-actions">

						<button type="button" class="cancel-button" onclick={() => (inviteCode = '')}>Close</button>
						<button type="button" class="save-button" onclick={copyInvite}>{copyLabel}</button>

					</div>

				</section>

			{/if}


			<!-- CAREGIVERS -->

			{#if formError}
				<p class="form-error" role="alert">{formError}</p>
			{/if}

			<div class="caregiver-list" aria-live="polite">
				{#if loading}
					<p class="loading-copy">Loading your trusted people…</p>
				{/if}

				{#each caregivers as caregiver}

					<article class="caregiver-row">

						<div
							class="caregiver-avatar"
							class:primary-avatar={caregiver.primary}
						>
							{caregiver.initial}
						</div>


						<div class="caregiver-info">

							<div class="name-row">

								<strong>
									{caregiver.name}
								</strong>

								{#if caregiver.primary}

									<span class="primary-badge">
										Primary
									</span>

								{/if}

							</div>


							<span class="relation">
								{caregiver.relation}
							</span>


							{#if caregiver.phone}

								<span class="phone">
									{caregiver.phone}
								</span>

							{/if}

						</div>


						<div class="caregiver-actions">

							{#if caregiver.phone}

								<a
									class="call-button"
									href={`tel:${caregiver.phone}`}
									aria-label={`Call ${caregiver.name}`}
								>
									☎
								</a>

							{/if}


							<button
								class="remove-button"
								onclick={() => removeCaregiver(caregiver.linkId, caregiver.name)}
								aria-label={`Remove ${caregiver.name} from your Care Circle`}
							>
								×
							</button>

						</div>

					</article>

				{/each}

			</div>


			{#if !loading && caregivers.length === 0}

				<div class="empty-state">

					<div class="empty-icon">
						♡
					</div>

					<h3>
						Your Care Circle is empty.
					</h3>

					<p>
						Add someone you trust so Vcare can keep
						them close when you need support.
					</p>

					<button onclick={generateInvite} disabled={generating}>
						{generating ? 'Creating code…' : '＋ Invite your first caregiver'}
					</button>

				</div>

			{/if}

		</section>


		<!-- SAFETY INFO -->

		<section class="bottom-grid">

			<div class="mini-card">

				<div class="mini-icon">
					☎
				</div>

				<div>
					<strong>
						One tap away
					</strong>

					<p>
						Call someone in your Care Circle whenever
						you need them.
					</p>
				</div>

			</div>

		</section>


		<button
			class="back-button"
			onclick={goBack}
		>
			← Back to dashboard
		</button>

	</main>

</div>


<style>
	:global(*) {
		box-sizing: border-box;
	}

	:global(html) {
		background: #f9f0e0;
	}

	:global(body) {
		margin: 0;

		background: #f9f0e0;
		color: #30473a;

		font-family:
			"Comic Sans MS",
			"Comic Sans",
			cursive;

		-webkit-font-smoothing: antialiased;
	}

	button,
	input {
		font: inherit;
	}

	button {
		cursor: pointer;
	}


	.page {
		min-height: 100vh;

		background:
			radial-gradient(
				circle at 89% 4%,
				rgba(215, 231, 80, 0.18),
				transparent 27%
			),
			radial-gradient(
				circle at 8% 92%,
				rgba(61, 138, 89, 0.06),
				transparent 23%
			),
			#f9f0e0;
	}


	/* TOP BAR */

	.topbar {
		height: 78px;

		padding: 0 48px;

		border-bottom:
			1px solid #e1d4bb;

		background:
			rgba(255, 250, 240, 0.96);

		display: flex;

		align-items: center;

		justify-content:
			space-between;

		position: sticky;

		top: 0;

		z-index: 20;

		backdrop-filter: blur(12px);
	}


	.brand {
		padding: 0;

		border: 0;

		background: transparent;

		color: inherit;

		display: flex;

		align-items: center;

		gap: 11px;

		text-align: left;
	}


	.logo {
		width: 47px;

		height: 47px;

		border-radius: 14px;

		background: #0b7148;

		color: white;

		display: grid;

		place-items: center;

		font-size: 23px;

		box-shadow:
			0 9px 20px
			rgba(11, 113, 72, 0.17);
	}


	.brand-copy {
		display: flex;

		flex-direction: column;
	}


	.brand-copy strong {
		color: #075b3c;

		font-size: 18px;

		line-height: 1;
	}


	.brand-copy span {
		margin-top: 5px;

		color: #7f7261;

		font-size: 9px;
	}


	.profile {
		display: flex;

		align-items: center;

		gap: 10px;
	}


	.avatar {
		width: 42px;

		height: 42px;

		border-radius: 50%;

		background: #d7e94d;

		color: #245a3d;

		display: grid;

		place-items: center;

		font-weight: 800;
	}


	.profile > div:last-child {
		display: flex;

		flex-direction: column;
	}


	.profile strong {
		color: #332e25;

		font-size: 11px;
	}


	.profile span {
		margin-top: 3px;

		color: #887b69;

		font-size: 8px;
	}


	/* CONTENT */

	.content {
		width:
			min(
				1080px,
				calc(100% - 42px)
			);

		margin: 0 auto;

		padding: 58px 0 70px;
	}


	/* HERO */

	.hero {
		margin-bottom: 24px;

		display: flex;

		align-items: flex-end;

		justify-content:
			space-between;

		gap: 30px;
	}


	.eyebrow {
		margin: 0 0 8px;

		color: #19724b;

		font-size: 9px;

		font-weight: 900;

		letter-spacing: 1.7px;
	}


	.hero h1 {
		margin: 0;

		color: #18513b;

		font-size:
			clamp(
				45px,
				5vw,
				65px
			);

		font-weight: 600;

		line-height: 0.98;

		letter-spacing: -2px;
	}


	.hero h1 span {
		color: #78a64a;
	}


	.hero-copy {
		margin: 15px 0 0;

		max-width: 590px;

		color: #766a5a;

		font-size: 12px;

		line-height: 1.6;
	}


	.summary-card {
		min-width: 185px;

		padding: 16px 19px;

		border:
			1px solid #ddceb2;

		border-radius: 18px;

		background: #fffaf0;

		display: flex;

		align-items: center;

		gap: 12px;

		box-shadow:
			0 8px 24px
			rgba(77, 57, 29, 0.04);
	}


	.summary-icon {
		width: 43px;

		height: 43px;

		border-radius: 12px;

		background: #eef2c8;

		color: #507d46;

		display: grid;

		place-items: center;

		font-size: 24px;
	}


	.summary-card > div:last-child {
		display: flex;

		flex-direction: column;
	}


	.summary-card strong {
		color: #315e43;

		font-size: 21px;
	}


	.summary-card span {
		margin-top: 2px;

		color: #817462;

		font-size: 8px;
	}


	/* CARE STRIP */

	.care-strip {
		margin-bottom: 18px;

		padding: 18px 20px;

		border:
			1px solid #d8d8a8;

		border-radius: 18px;

		background:
			linear-gradient(
				90deg,
				#edf2ce,
				#f8f1dd
			);

		display: flex;

		align-items: center;

		gap: 13px;

		position: relative;

		overflow: hidden;
	}


	.strip-icon {
		width: 42px;

		height: 42px;

		flex-shrink: 0;

		border-radius: 12px;

		background:
			rgba(255, 255, 255, 0.55);

		color: #63904d;

		display: grid;

		place-items: center;

		font-size: 24px;
	}


	.care-strip strong {
		color: #386346;

		font-size: 10px;
	}


	.care-strip p {
		margin: 4px 0 0;

		color: #796e5d;

		font-size: 8px;

		line-height: 1.5;
	}


	.strip-decoration {
		position: absolute;

		right: 25px;

		top: -27px;

		color:
			rgba(86, 133, 72, 0.08);

		font-size: 100px;
	}


	/* MAIN CARD */

	.care-card {
		padding: 28px 31px 23px;

		border:
			1px solid #ddceb2;

		border-radius: 24px;

		background:
			rgba(
				255,
				250,
				240,
				0.96
			);

		box-shadow:
			0 14px 32px
			rgba(64, 48, 25, 0.05);
	}


	.section-header {
		padding-bottom: 21px;

		border-bottom:
			1px solid #eadfc9;

		display: flex;

		align-items: flex-start;

		justify-content:
			space-between;

		gap: 25px;
	}


	.section-header h2 {
		margin: 0;

		color: #294a3a;

		font-size: 27px;
	}


	.section-header > div > p:last-child {
		margin: 6px 0 0;

		color: #837766;

		font-size: 9px;
	}


	.add-button {
		padding: 10px 15px;

		border:
			1px solid #83a568;

		border-radius: 11px;

		background: #f5f7dd;

		color: #356646;

		font-size: 9px;

		font-weight: 800;
	}


	/* FORM */

	.add-panel {
		margin-top: 19px;

		padding: 21px;

		border:
			1px solid #d6d9a1;

		border-radius: 18px;

		background:
			linear-gradient(
				120deg,
				#eff3cd,
				#fff8e8
			);
	}


	.form-heading {
		margin-bottom: 16px;

		display: flex;

		align-items: center;

		gap: 11px;
	}


	.form-symbol {
		width: 38px;

		height: 38px;

		border-radius: 11px;

		background: #d8e64e;

		color: #315e41;

		display: grid;

		place-items: center;

		font-size: 21px;
	}


	.form-heading strong {
		color: #334a3c;

		font-size: 12px;
	}


	.form-heading p {
		margin: 3px 0 0;

		color: #7d7160;

		font-size: 8px;
	}


	.form-grid {
		display: grid;

		grid-template-columns:
			1fr 1fr 1fr;

		gap: 11px;
	}


	.form-grid label {
		display: flex;

		flex-direction: column;

		gap: 7px;
	}


	.form-grid label > span {
		color: #455044;

		font-size: 8px;

		font-weight: 800;
	}


	.form-grid input {
		width: 100%;

		padding: 11px 12px;

		border:
			1px solid #d7c7aa;

		border-radius: 10px;

		outline: none;

		background: #fffaf1;

		color: #39483e;

		font-size: 10px;
	}


	.form-grid input:focus {
		border-color: #739c56;

		box-shadow:
			0 0 0 3px
			rgba(115, 156, 86, 0.11);
	}


	.form-actions {
		margin-top: 15px;

		display: flex;

		justify-content:
			flex-end;

		gap: 8px;
	}

	.form-error {
		margin: 14px 0 0;
		padding: 11px 13px;
		border: 1px solid #efc6bd;
		border-radius: 12px;
		background: #fff1ed;
		color: #9b2f24;
		font-size: 13px;
		font-weight: 700;
	}


	.cancel-button,
	.save-button {
		padding: 9px 14px;

		border-radius: 9px;

		font-size: 9px;

		font-weight: 800;
	}


	.cancel-button {
		border:
			1px solid #d5c5a8;

		background: transparent;

		color: #766958;
	}


	.save-button {
		border: 0;

		background: #14784c;

		color: white;
	}


	/* CAREGIVER ROWS */

	.caregiver-list {
		margin-top: 3px;
	}


	.caregiver-row {
		min-height: 100px;

		padding: 16px 0;

		border-bottom:
			1px solid #eadfc9;

		display: grid;

		grid-template-columns:
			58px
			minmax(0, 1fr)
			auto;

		align-items: center;

		gap: 15px;
	}


	.caregiver-avatar {
		width: 48px;

		height: 48px;

		border-radius: 50%;

		background: #eef1ce;

		color: #53744b;

		display: grid;

		place-items: center;

		font-size: 17px;

		font-weight: 900;
	}


	.caregiver-avatar.primary-avatar {
		background: #d9e94d;

		color: #356045;
	}


	.caregiver-info {
		display: flex;

		flex-direction: column;
	}


	.name-row {
		display: flex;

		align-items: center;

		gap: 8px;
	}


	.name-row strong {
		color: #35463c;

		font-size: 11px;
	}


	.primary-badge {
		padding: 4px 7px;

		border-radius: 8px;

		background: #e4efd2;

		color: #55804c;

		font-size: 6px;

		font-weight: 800;
	}


	.relation {
		margin-top: 4px;

		color: #837766;

		font-size: 8px;
	}


	.phone {
		margin-top: 4px;

		color: #9a8d7a;

		font-size: 7px;
	}


	.caregiver-actions {
		display: flex;

		align-items: center;

		gap: 7px;
	}


	.primary-button {
		padding: 7px 9px;

		border:
			1px solid #d5c8ad;

		border-radius: 9px;

		background: transparent;

		color: #6d6658;

		font-size: 7px;

		font-weight: 800;
	}


	.call-button {
		width: 37px;

		height: 37px;

		border:
			1px solid #d8c9ac;

		border-radius: 50%;

		background: #fffaf0;

		color: #167449;

		display: grid;

		place-items: center;

		text-decoration: none;

		font-size: 14px;
	}


	.call-button:hover {
		background: #edf2d1;
	}


	.remove-button {
		width: 31px;

		height: 31px;

		border:
			1px solid #dfd0b9;

		border-radius: 9px;

		background: transparent;

		color: #9a8d79;

		display: grid;

		place-items: center;

		font-size: 15px;
	}


	/* EMPTY */

	.empty-state {
		min-height: 290px;

		display: flex;

		flex-direction: column;

		align-items: center;

		justify-content: center;

		text-align: center;
	}


	.empty-icon {
		width: 62px;

		height: 62px;

		border-radius: 19px;

		background: #eef2c9;

		color: #61864e;

		display: grid;

		place-items: center;

		font-size: 31px;
	}


	.empty-state h3 {
		margin: 15px 0 0;

		color: #355646;

		font-size: 19px;
	}


	.empty-state p {
		max-width: 390px;

		margin: 8px 0 17px;

		color: #837664;

		font-size: 9px;

		line-height: 1.6;
	}


	.empty-state button {
		padding: 10px 14px;

		border: 0;

		border-radius: 10px;

		background: #14784c;

		color: white;

		font-size: 8px;

		font-weight: 800;
	}


	/* BOTTOM INFO */

	.bottom-grid {
		margin-top: 17px;

		display: grid;
		grid-template-columns: minmax(0, 640px);
		justify-content: center;

		gap: 11px;
	}


	.mini-card {
		padding: 15px 16px;

		border:
			1px solid #dfd1b8;

		border-radius: 16px;

		background:
			rgba(
				255,
				250,
				240,
				0.92
			);

		display: flex;

		align-items: center;

		gap: 11px;
	}


	.mini-icon {
		width: 39px;

		height: 39px;

		border-radius: 11px;

		background: #eef2c8;

		color: #52774a;

		display: grid;

		place-items: center;

		font-size: 17px;
	}


	.mini-card > div:last-child {
		display: flex;

		flex-direction: column;
	}


	.mini-card strong {
		color: #35493d;

		font-size: 10px;
	}


	.mini-card p {
		margin: 4px 0 0;

		color: #8a7e6d;

		font-size: 7px;

		line-height: 1.5;
	}


	.back-button {
		margin-top: 16px;

		padding: 9px 0;

		border: 0;

		background: transparent;

		color: #27704d;

		font-size: 9px;

		font-weight: 800;
	}


	@media (max-width: 760px) {

		.topbar {
			padding: 0 18px;
		}

		.content {
			width:
				calc(100% - 26px);

			padding-top: 34px;
		}

		.hero {
			align-items: flex-start;

			flex-direction: column;
		}

		.summary-card {
			width: 100%;
		}

		.section-header {
			flex-direction: column;
		}

		.add-button {
			width: 100%;
		}

		.form-grid {
			grid-template-columns: 1fr;
		}

		.caregiver-row {
			grid-template-columns:
				50px 1fr;

			row-gap: 13px;
		}

		.caregiver-actions {
			grid-column: 1 / -1;

			justify-content: flex-end;
		}

		.bottom-grid {
			grid-template-columns: 1fr;
		}
	}

	/* Unified senior navigation and modern page shell */
	:global(body) { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f3f5ef; }
	.page { display: grid; grid-template-columns: 250px minmax(0,1fr); grid-template-rows: auto 1fr; background: radial-gradient(circle at 86% 5%, rgba(203,230,99,.22), transparent 28%), linear-gradient(180deg,#f8faf5 0%,#f1f4ed 100%); }
	.topbar { grid-column: 2; height: 82px; justify-content: flex-end; border-color: rgba(25,82,61,.1); background: rgba(250,252,247,.88); backdrop-filter: blur(18px); }
	.content { grid-column: 2; width: min(1180px,92%); }
	.hero h1 { font-family: Georgia, "Times New Roman", serif; letter-spacing: -2.5px; }
	.hero h1 span { font-family: Inter, ui-sans-serif, sans-serif; font-weight: 650; }
	.care-strip, .care-card, .summary-card, .mini-card { border-color: rgba(32,83,63,.11); background: rgba(255,255,255,.78); box-shadow: 0 18px 56px rgba(24,62,47,.07); }
	.caregiver-row { border-radius: 16px; padding-inline: 14px; transition: background .2s ease, transform .2s ease; }
	.caregiver-row:hover { background: #f5f8f2; transform: translateX(3px); }
	.invite-panel { border: 1px solid #cfe2d8; background: linear-gradient(135deg,#f4fbf7,#edf7f1); }
	.invite-code { margin: 20px 0; padding: 18px; border: 2px dashed #6ca88b; border-radius: 16px; background: white; color: #124b38; font-size: clamp(25px,3vw,38px); font-weight: 900; letter-spacing: .12em; text-align: center; }
	.loading-copy { padding: 24px 12px; color: #63756d; font-weight: 700; }
	.add-button:disabled, .empty-state button:disabled { opacity: .65; cursor: wait; }

	.senior-sidebar { grid-row: 1 / 3; position: sticky; top: 0; height: 100vh; padding: 27px 18px 22px; background: linear-gradient(165deg,rgba(255,255,255,.055),transparent 42%),#123f31; box-shadow: 14px 0 40px rgba(21,62,48,.11); display: flex; flex-direction: column; z-index: 30; }
	.side-brand { display: flex; align-items: center; gap: 11px; padding: 0 7px 28px; color: white; text-decoration: none; }
	.side-brand > span:last-child { display: flex; flex-direction: column; }
	.side-brand strong { font-size: 18px; line-height: 1; }
	.side-brand small { margin-top: 5px; color: rgba(255,255,255,.55); font-size: 9px; }
	.side-logo { width: 44px; height: 44px; border-radius: 14px; background: #d6eb6c; color: #123f31; display: grid; place-items: center; font-size: 21px; box-shadow: 0 9px 25px rgba(0,0,0,.16); }
	.side-nav { display: flex; flex-direction: column; gap: 7px; }
	.side-nav a { min-height: 58px; padding: 10px 12px; border: 1px solid transparent; border-radius: 15px; color: rgba(255,255,255,.78); display: flex; align-items: center; gap: 12px; text-decoration: none; transition: .2s ease; }
	.side-nav a > span { width: 31px; height: 31px; border-radius: 11px; background: rgba(255,255,255,.07); display: grid; place-items: center; font-size: 17px; }
	.side-nav a div { display: flex; flex-direction: column; }
	.side-nav a strong { font-size: 12px; }
	.side-nav a small { margin-top: 3px; color: rgba(255,255,255,.44); font-size: 8px; }
	.side-nav a:hover { transform: translateX(3px); border-color: rgba(255,255,255,.08); background: rgba(255,255,255,.08); }
	.side-nav a.active { background: #e4efc7; color: #153f31; box-shadow: 0 12px 26px rgba(0,0,0,.14); }
	.side-nav a.active > span { background: rgba(18,63,49,.08); }
	.side-nav a.active small { color: #647266; }
	.side-note { margin-top: auto; padding: 15px; border: 1px solid rgba(255,255,255,.1); border-radius: 17px; background: rgba(255,255,255,.07); color: white; display: flex; align-items: center; gap: 10px; }
	.side-note > span { width: 33px; height: 33px; border-radius: 11px; background: rgba(214,235,108,.15); color: #d6eb6c; display: grid; place-items: center; }
	.side-note div { display: flex; flex-direction: column; }
	.side-note strong { font-size: 10px; }
	.side-note small { margin-top: 3px; color: rgba(255,255,255,.5); font-size: 8px; }

	@media (max-width: 820px) { .page { display:block; } .senior-sidebar { display:none; } .topbar { padding-inline:20px; } .invite-code { letter-spacing:.06em; } }
</style>
