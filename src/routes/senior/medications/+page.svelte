<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { supabase } from '$lib/supabase';

	let senior = $state({
		firstName: 'User',
		fullName: ''
	});

	let medicines = $state([]);
	let loading = $state(true);
	let saving = $state(false);
	let errorMessage = $state('');
	let successMessage = $state('');
	let showAddForm = $state(false);

	let medicineName = $state('');
	let dosage = $state('');
	let scheduledTime = $state('');

	let userId = $state('');

	onMount(() => {
		let channel;

		async function start() {
			loading = true;

			const {
				data: { user },
				error: authError
			} = await supabase.auth.getUser();

			if (authError || !user) {
				goto('/auth');
				return;
			}

			userId = user.id;

			const { data: profile } = await supabase
				.from('profiles')
				.select('full_name')
				.eq('id', user.id)
				.single();

			const fullName =
				profile?.full_name ||
				user.user_metadata?.full_name ||
				user.user_metadata?.name ||
				'User';

			senior.fullName = fullName;
			senior.firstName = fullName.split(' ')[0];

			await loadMedicines();

			/*
				REALTIME:
				If the backend / Bland webhook updates a medication,
				this page reloads the medicines automatically.
			*/
			channel = supabase
				.channel(`senior-medications-${user.id}`)
				.on(
					'postgres_changes',
					{
						event: '*',
						schema: 'public',
						table: 'medications',
						filter: `senior_id=eq.${user.id}`
					},
					async () => {
						await loadMedicines();
					}
				)
				.subscribe();

			loading = false;
		}

		start();

		return () => {
			if (channel) {
				supabase.removeChannel(channel);
			}
		};
	});

	async function loadMedicines() {
		if (!userId) return;

		errorMessage = '';

		const { data, error } = await supabase
			.from('medications')
			.select(
				'id, senior_id, name, dosage, scheduled_time, taken, taken_at'
			)
			.eq('senior_id', userId)
			.order('scheduled_time', { ascending: true });

		if (error) {
			console.error('Medicine load error:', error);
			errorMessage = 'Could not load your medicines.';
			return;
		}

		medicines = data || [];
	}

	async function addMedicine() {
		errorMessage = '';
		successMessage = '';

		if (!medicineName.trim()) {
			errorMessage = 'Please enter the medicine name.';
			return;
		}

		if (!dosage.trim()) {
			errorMessage = 'Please enter the dosage.';
			return;
		}

		if (!scheduledTime) {
			errorMessage = 'Please choose a time.';
			return;
		}

		if (!userId) {
			errorMessage = 'Please sign in again.';
			return;
		}

		saving = true;

		const { error } = await supabase.from('medications').insert({
			senior_id: userId,
			name: medicineName.trim(),
			dosage: dosage.trim(),
			scheduled_time: scheduledTime,
			taken: false,
			taken_at: null
		});

		saving = false;

		if (error) {
			console.error('Medicine insert error:', error);
			errorMessage = error.message || 'Could not add the medicine.';
			return;
		}

		medicineName = '';
		dosage = '';
		scheduledTime = '';
		showAddForm = false;

		successMessage = 'Medicine added successfully.';

		await loadMedicines();

		setTimeout(() => {
			successMessage = '';
		}, 2500);
	}

	async function markTaken(medicine) {
		errorMessage = '';

		const { error } = await supabase
			.from('medications')
			.update({
				taken: true,
				taken_at: new Date().toISOString()
			})
			.eq('id', medicine.id)
			.eq('senior_id', userId);

		if (error) {
			console.error('Medicine update error:', error);
			errorMessage = 'Could not update the medicine.';
			return;
		}

		await loadMedicines();
	}

	async function markPending(medicine) {
		errorMessage = '';

		const { error } = await supabase
			.from('medications')
			.update({
				taken: false,
				taken_at: null
			})
			.eq('id', medicine.id)
			.eq('senior_id', userId);

		if (error) {
			console.error('Medicine update error:', error);
			errorMessage = 'Could not update the medicine.';
			return;
		}

		await loadMedicines();
	}

	function formatTime(time) {
		if (!time) return '';

		const parts = time.split(':');

		let hour = Number(parts[0]);
		const minute = parts[1] || '00';

		const suffix = hour >= 12 ? 'PM' : 'AM';

		hour = hour % 12 || 12;

		return `${hour}:${minute} ${suffix}`;
	}

	function goHome() {
		goto('/senior/dashboard');
	}
</script>

<svelte:head>
	<title>My Medicines — Vcare.life</title>
</svelte:head>

<div class="page">
	<header class="topbar">
		<button class="brand" onclick={goHome}>
			<div class="logo">♥</div>

			<div class="brand-copy">
				<strong>Vcare.life</strong>
				<span>A Voice That Cares</span>
			</div>
		</button>

		<div class="profile">
			<div class="avatar">
				{senior.firstName.charAt(0).toUpperCase()}
			</div>

			<div>
				<strong>{senior.firstName}</strong>
				<span>My medicines</span>
			</div>
		</div>
	</header>

	<main class="content">
		<section class="hero">
			<div>
				<p class="eyebrow">YOUR CARE PLAN</p>

				<h1>
					Your <span>medicines.</span>
				</h1>

				<p class="hero-copy">
					Keep everything in one simple place.
					Vcare can check in with you about these medicines.
				</p>
			</div>

			<div class="hero-pill">
				<div>💊</div>

				<span>
					<strong>{medicines.length}</strong>
					medicines
				</span>
			</div>
		</section>

		{#if errorMessage}
			<div class="message error">
				<span>!</span>
				{errorMessage}
			</div>
		{/if}

		{#if successMessage}
			<div class="message success">
				<span>✓</span>
				{successMessage}
			</div>
		{/if}

		<section class="medicine-card">
			<div class="section-header">
				<div>
					<p class="eyebrow">TODAY</p>
					<h2>Medication plan</h2>

					<p>
						Add the medicines you want Vcare to remember.
					</p>
				</div>

				<button
					class="add-button"
					onclick={() => (showAddForm = !showAddForm)}
				>
					<span>+</span>
					Add medicine
				</button>
			</div>

			{#if showAddForm}
				<div class="add-panel">
					<div class="form-heading">
						<div class="form-icon">+</div>

						<div>
							<strong>Add a medicine</strong>
							<p>We'll keep it ready for your Vcare check-ins.</p>
						</div>
					</div>

					<div class="form-grid">
						<label class="field medicine-field">
							<span>Medicine name</span>

							<input
								type="text"
								placeholder="e.g. Evening Medicine"
								bind:value={medicineName}
							/>
						</label>

						<label class="field">
							<span>Dosage</span>

							<input
								type="text"
								placeholder="e.g. 1 tablet"
								bind:value={dosage}
							/>
						</label>

						<label class="field">
							<span>Time</span>

							<input
								type="time"
								bind:value={scheduledTime}
							/>
						</label>
					</div>

					<div class="form-actions">
						<button
							class="cancel-button"
							onclick={() => (showAddForm = false)}
						>
							Cancel
						</button>

						<button
							class="save-button"
							onclick={addMedicine}
							disabled={saving}
						>
							{saving ? 'Saving...' : 'Save medicine →'}
						</button>
					</div>
				</div>
			{/if}

			{#if loading}
				<div class="empty-state">
					<div class="empty-icon">♡</div>
					<h3>Loading your medicines...</h3>
				</div>

			{:else if medicines.length === 0}
				<div class="empty-state">
					<div class="empty-icon">💊</div>

					<h3>No medicines added yet</h3>

					<p>
						Add your first medicine and Vcare can include it
						in your check-ins.
					</p>

					<button
						class="empty-add"
						onclick={() => (showAddForm = true)}
					>
						+ Add your first medicine
					</button>
				</div>

			{:else}
				<div class="medicine-list">
					{#each medicines as medicine}
						<article
							class="medicine-row"
							class:taken={medicine.taken}
						>
							<div class="time">
								<strong>
									{formatTime(medicine.scheduled_time).split(' ')[0]}
								</strong>

								<span>
									{formatTime(medicine.scheduled_time).split(' ')[1]}
								</span>
							</div>

							<div
								class="timeline"
								class:taken-line={medicine.taken}
							>
								<div class="dot">
									{medicine.taken ? '✓' : ''}
								</div>
							</div>

							<div class="pill-icon">
								💊
							</div>

							<div class="medicine-details">
								<strong>{medicine.name}</strong>
								<span>{medicine.dosage}</span>
							</div>

							<div class="status-area">
								{#if medicine.taken}
									<div class="taken-badge">
										✓ Taken
									</div>

									<button
										class="tiny-button"
										onclick={() => markPending(medicine)}
									>
										Undo
									</button>
								{:else}
									<div class="pending-badge">
										● Pending
									</div>

									<button
										class="take-button"
										onclick={() => markTaken(medicine)}
									>
										I took this
									</button>
								{/if}
							</div>
						</article>
					{/each}
				</div>
			{/if}
		</section>

		<section class="info-card">
			<div class="info-heart">♡</div>

			<div>
				<strong>How Vcare uses this</strong>

				<p>
					During a check-in, Vcare can ask whether you've
					taken a scheduled medicine. When confirmed, its
					status can be updated here automatically.
				</p>
			</div>
		</section>

		<button class="back-button" onclick={goHome}>
			← Back to dashboard
		</button>
	</main>
</div>

<style>
	:global(*) {
		box-sizing: border-box;
	}

	:global(html) {
		background: #fbf2e3;
	}

	:global(body) {
		margin: 0;
		background: #fbf2e3;
		font-family:
			Inter,
			-apple-system,
			BlinkMacSystemFont,
			"Segoe UI",
			sans-serif;
		color: #294537;
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
				circle at 90% 6%,
				rgba(213, 230, 82, 0.16),
				transparent 29%
			),
			#fbf2e3;
	}

	.topbar {
		height: 86px;
		padding: 0 54px;
		border-bottom: 1px solid #e5d8bf;
		background: rgba(255, 251, 242, 0.93);

		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.brand {
		padding: 0;
		border: 0;
		background: transparent;

		display: flex;
		align-items: center;
		gap: 12px;

		text-align: left;
		color: inherit;
	}

	.logo {
		width: 49px;
		height: 49px;

		border-radius: 15px;

		background: #08734a;
		color: white;

		display: grid;
		place-items: center;

		font-size: 24px;

		box-shadow: 0 9px 20px rgba(8, 115, 74, 0.15);
	}

	.brand-copy {
		display: flex;
		flex-direction: column;
	}

	.brand-copy strong {
		color: #075d3d;
		font-size: 19px;
	}

	.brand-copy span {
		margin-top: 3px;

		color: #776e60;
		font-size: 10px;
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

		background: #d7e84d;
		color: #27623f;

		display: grid;
		place-items: center;

		font-weight: 800;
	}

	.profile > div:last-child {
		display: flex;
		flex-direction: column;
	}

	.profile strong {
		font-size: 12px;
	}

	.profile span {
		margin-top: 3px;

		color: #887b68;
		font-size: 9px;
	}

	.content {
		width: min(1060px, calc(100% - 40px));

		margin: 0 auto;
		padding: 72px 0 80px;
	}

	.hero {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 30px;

		margin-bottom: 34px;
	}

	.eyebrow {
		margin: 0 0 10px;

		color: #18714c;

		font-size: 10px;
		font-weight: 800;
		letter-spacing: 2px;
	}

	.hero h1 {
		margin: 0;

		color: #17543d;

		font-family:
			Georgia,
			"Times New Roman",
			serif;

		font-size: clamp(42px, 5vw, 68px);
		font-weight: 500;
		line-height: 0.98;
	}

	.hero h1 span {
		color: #75a54d;
	}

	.hero-copy {
		max-width: 600px;

		margin: 18px 0 0;

		color: #756b5e;

		font-size: 14px;
		line-height: 1.7;
	}

	.hero-pill {
		min-width: 180px;

		padding: 18px 21px;

		border: 1px solid #dfd1b5;
		border-radius: 19px;

		background: rgba(255, 250, 240, 0.88);

		display: flex;
		align-items: center;
		gap: 13px;

		box-shadow: 0 10px 28px rgba(70, 53, 30, 0.04);
	}

	.hero-pill > div {
		width: 43px;
		height: 43px;

		border-radius: 13px;

		background: #edf2c8;

		display: grid;
		place-items: center;

		font-size: 20px;
	}

	.hero-pill span {
		display: flex;
		flex-direction: column;

		color: #817462;
		font-size: 10px;
	}

	.hero-pill strong {
		color: #315c41;
		font-size: 20px;
	}

	.message {
		margin-bottom: 18px;
		padding: 13px 16px;

		border-radius: 13px;

		display: flex;
		align-items: center;
		gap: 10px;

		font-size: 12px;
	}

	.message span {
		width: 24px;
		height: 24px;

		border-radius: 50%;

		display: grid;
		place-items: center;

		font-weight: bold;
	}

	.message.error {
		background: #f8ded5;
		color: #a64d3f;
	}

	.message.error span {
		background: #c96150;
		color: white;
	}

	.message.success {
		background: #eaf1ce;
		color: #386a46;
	}

	.message.success span {
		background: #6b984d;
		color: white;
	}

	.medicine-card {
		padding: 32px 34px;

		border: 1px solid #dfd0b3;
		border-radius: 25px;

		background: rgba(255, 250, 240, 0.94);

		box-shadow: 0 10px 30px rgba(70, 53, 30, 0.04);
	}

	.section-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 25px;

		padding-bottom: 24px;

		border-bottom: 1px solid #eadfc9;
	}

	.section-header h2 {
		margin: 0;

		color: #28483a;

		font-family:
			Georgia,
			"Times New Roman",
			serif;

		font-size: 30px;
		font-weight: 500;
	}

	.section-header > div > p:last-child {
		margin: 7px 0 0;

		color: #837665;
		font-size: 11px;
	}

	.add-button {
		padding: 12px 17px;

		border: 1px solid #86a769;
		border-radius: 12px;

		background: #f6f8de;
		color: #346745;

		font-weight: 700;
		font-size: 11px;

		display: flex;
		align-items: center;
		gap: 8px;
	}

	.add-button span {
		font-size: 19px;
		line-height: 0;
	}

	.add-panel {
		margin-top: 25px;
		padding: 25px;

		border: 1px solid #d8dba4;
		border-radius: 19px;

		background:
			linear-gradient(
				115deg,
				rgba(238, 244, 201, 0.9),
				rgba(255, 249, 235, 0.95)
			);
	}

	.form-heading {
		display: flex;
		align-items: center;
		gap: 12px;

		margin-bottom: 21px;
	}

	.form-icon {
		width: 39px;
		height: 39px;

		border-radius: 12px;

		background: #d8e654;
		color: #356344;

		display: grid;
		place-items: center;

		font-size: 25px;
		font-weight: 700;
	}

	.form-heading strong {
		font-size: 15px;
	}

	.form-heading p {
		margin: 4px 0 0;

		color: #79715f;
		font-size: 10px;
	}

	.form-grid {
		display: grid;

		grid-template-columns:
			minmax(0, 1.5fr)
			minmax(0, 1fr)
			minmax(150px, 0.75fr);

		gap: 13px;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.field > span {
		color: #3e493e;

		font-size: 10px;
		font-weight: 700;
	}

	.field input {
		width: 100%;

		padding: 13px 14px;

		border: 1px solid #d8c9ad;
		border-radius: 12px;
		outline: none;

		background: #fffaf1;
		color: #3a453d;

		font-size: 12px;

		transition:
			border 0.2s,
			box-shadow 0.2s;
	}

	.field input:focus {
		border-color: #6e9a51;

		box-shadow: 0 0 0 3px rgba(112, 157, 78, 0.12);
	}

	.form-actions {
		margin-top: 19px;

		display: flex;
		justify-content: flex-end;
		gap: 9px;
	}

	.cancel-button,
	.save-button {
		padding: 11px 17px;

		border-radius: 11px;

		font-size: 11px;
		font-weight: 700;
	}

	.cancel-button {
		border: 1px solid #d7c7aa;

		background: transparent;
		color: #756958;
	}

	.save-button {
		border: 0;

		background: #14784c;
		color: white;
	}

	.save-button:disabled {
		opacity: 0.6;
		cursor: wait;
	}

	.medicine-list {
		margin-top: 8px;
	}

	.medicine-row {
		min-height: 92px;

		display: grid;

		grid-template-columns:
			68px
			32px
			48px
			minmax(0, 1fr)
			auto;

		align-items: center;

		border-bottom: 1px solid #eadfc9;

		transition: background 0.2s;
	}

	.medicine-row:hover {
		background: rgba(242, 245, 214, 0.25);
	}

	.medicine-row.taken {
		opacity: 0.76;
	}

	.time {
		display: flex;
		flex-direction: column;
	}

	.time strong {
		color: #29714f;
		font-size: 13px;
	}

	.time span {
		margin-top: 2px;

		color: #739078;
		font-size: 7px;
	}

	.timeline {
		height: 100%;

		position: relative;

		display: grid;
		place-items: center;
	}

	.timeline::before {
		content: "";

		position: absolute;
		top: 0;
		bottom: 0;

		width: 1px;

		background: #dfd6be;
	}

	.dot {
		position: relative;
		z-index: 2;

		width: 19px;
		height: 19px;

		border: 2px solid #a7ad7b;
		border-radius: 50%;

		background: #fffaf0;
		color: white;

		display: grid;
		place-items: center;

		font-size: 9px;
		font-weight: bold;
	}

	.taken-line .dot {
		border-color: #64a15d;
		background: #64a15d;
	}

	.pill-icon {
		width: 35px;
		height: 35px;

		border-radius: 11px;

		background: #f1f1c9;

		display: grid;
		place-items: center;

		font-size: 16px;
	}

	.medicine-details {
		padding-left: 4px;

		display: flex;
		flex-direction: column;
		gap: 5px;
	}

	.medicine-details strong {
		color: #35463d;
		font-size: 12px;
	}

	.medicine-details span {
		color: #887d6d;
		font-size: 9px;
	}

	.status-area {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.taken-badge,
	.pending-badge {
		padding: 7px 10px;

		border-radius: 9px;

		font-size: 9px;
		font-weight: 700;
	}

	.taken-badge {
		background: #e8f0d6;
		color: #528149;
	}

	.pending-badge {
		background: #f5edcf;
		color: #957826;
	}

	.take-button,
	.tiny-button {
		padding: 8px 11px;

		border-radius: 9px;

		font-size: 9px;
		font-weight: 700;
	}

	.take-button {
		border: 1px solid #78a65f;

		background: #f9f8e9;
		color: #397043;
	}

	.tiny-button {
		border: 1px solid #d8cab0;

		background: transparent;
		color: #827563;
	}

	.empty-state {
		min-height: 310px;

		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;

		text-align: center;
	}

	.empty-icon {
		width: 66px;
		height: 66px;

		margin-bottom: 17px;

		border-radius: 20px;

		background: #eef2cb;

		display: grid;
		place-items: center;

		font-size: 28px;
	}

	.empty-state h3 {
		margin: 0;

		color: #355545;

		font-family: Georgia, serif;
		font-size: 23px;
		font-weight: 500;
	}

	.empty-state p {
		max-width: 380px;

		margin: 9px 0 20px;

		color: #837664;
		font-size: 11px;
		line-height: 1.6;
	}

	.empty-add {
		padding: 11px 15px;

		border: 0;
		border-radius: 11px;

		background: #14784c;
		color: white;

		font-size: 10px;
		font-weight: 700;
	}

	.info-card {
		margin-top: 21px;
		padding: 21px 24px;

		border: 1px solid #d9d8aa;
		border-radius: 19px;

		background:
			linear-gradient(
				90deg,
				#edf2cf,
				#f8f2df
			);

		display: flex;
		align-items: center;
		gap: 15px;
	}

	.info-heart {
		width: 45px;
		height: 45px;

		flex-shrink: 0;

		border-radius: 14px;

		background: rgba(255, 255, 255, 0.55);
		color: #61904d;

		display: grid;
		place-items: center;

		font-size: 27px;
	}

	.info-card strong {
		color: #386447;
		font-size: 12px;
	}

	.info-card p {
		margin: 5px 0 0;

		color: #796e5d;
		font-size: 10px;
		line-height: 1.55;
	}

	.back-button {
		margin-top: 20px;
		padding: 10px 0;

		border: 0;

		background: transparent;
		color: #27704d;

		font-size: 11px;
		font-weight: 700;
	}

	@media (max-width: 760px) {
		.topbar {
			height: 75px;
			padding: 0 18px;
		}

		.brand-copy span {
			display: none;
		}

		.content {
			width: calc(100% - 28px);
			padding-top: 39px;
		}

		.hero {
			align-items: flex-start;
			flex-direction: column;
		}

		.hero-pill {
			width: 100%;
		}

		.medicine-card {
			padding: 23px 18px;
		}

		.section-header {
			flex-direction: column;
		}

		.add-button {
			width: 100%;
			justify-content: center;
		}

		.form-grid {
			grid-template-columns: 1fr;
		}

		.medicine-row {
			padding: 17px 0;

			grid-template-columns:
				55px
				32px
				42px
				minmax(0, 1fr);

			row-gap: 14px;
		}

		.status-area {
			grid-column: 1 / -1;

			justify-content: flex-end;
		}
	}
</style>
