<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let reminders = $state([]);
	let showAddForm = $state(false);

	let title = $state('');
	let reminderTime = $state('');
	let note = $state('');

	onMount(() => {
		const saved = localStorage.getItem('vcare-reminders');

		if (saved) {
			try {
				reminders = JSON.parse(saved);
			} catch {
				reminders = [];
			}
		}
	});

	function saveReminders() {
		localStorage.setItem(
			'vcare-reminders',
			JSON.stringify(reminders)
		);
	}

	function addReminder() {
		if (!title.trim() || !reminderTime) return;

		const reminder = {
			id: Date.now(),
			title: title.trim(),
			time: reminderTime,
			note: note.trim(),
			completed: false
		};

		reminders = [...reminders, reminder];

		saveReminders();

		title = '';
		reminderTime = '';
		note = '';
		showAddForm = false;
	}

	function toggleReminder(id) {
		reminders = reminders.map((reminder) =>
			reminder.id === id
				? {
						...reminder,
						completed: !reminder.completed
					}
				: reminder
		);

		saveReminders();
	}

	function deleteReminder(id) {
		reminders = reminders.filter(
			(reminder) => reminder.id !== id
		);

		saveReminders();
	}

	function formatTime(time) {
		if (!time) return '';

		const [hourString, minute] = time.split(':');
		let hour = Number(hourString);

		const suffix = hour >= 12 ? 'PM' : 'AM';

		hour = hour % 12 || 12;

		return `${hour}:${minute} ${suffix}`;
	}

	function openPreset(presetTitle, presetNote) {
		title = presetTitle;
		note = presetNote;
		showAddForm = true;
	}

	function goBack() {
		goto('/senior/dashboard');
	}
</script>

<svelte:head>
	<title>Reminders — Vcare.life</title>
</svelte:head>

<div class="page">
	<header class="topbar">
		<button class="brand" onclick={goBack}>
			<div class="logo">♥</div>

			<div class="brand-copy">
				<strong>Vcare.life</strong>
				<span>A Voice That Cares</span>
			</div>
		</button>

		<div class="profile">
			<div class="avatar">A</div>

			<div class="profile-copy">
				<strong>Aalisha</strong>
				<span>My reminders</span>
			</div>
		</div>
	</header>

	<main class="content">

		<!-- HERO -->

		<section class="hero">
			<div>
				<p class="eyebrow">YOUR DAY WITH VCARE</p>

				<h1>
					Your <span>reminders.</span>
				</h1>

				<p class="hero-copy">
					A calm little space for the things you don't
					want to forget.
				</p>
			</div>

			<div class="summary-card">
				<div class="summary-icon">◷</div>

				<div>
					<strong>{reminders.length}</strong>
					<span>
						{reminders.length === 1
							? 'reminder today'
							: 'reminders today'}
					</span>
				</div>
			</div>
		</section>

		<!-- QUICK ADD -->

		<section class="quick-section">
			<div class="quick-title">
				<span>QUICK ADD</span>
				<p>Things you may want Vcare to remember.</p>
			</div>

			<div class="quick-grid">
				<button
					onclick={() =>
						openPreset(
							'Take medicine',
							'Daily medication'
						)}
				>
					<div class="quick-icon medicine-icon">💊</div>

					<div>
						<strong>Medicine</strong>
						<span>Medication reminder</span>
					</div>

					<b>＋</b>
				</button>

				<button
					onclick={() =>
						openPreset(
							'Drink water',
							'Stay hydrated'
						)}
				>
					<div class="quick-icon water-icon">💧</div>

					<div>
						<strong>Water</strong>
						<span>Hydration check</span>
					</div>

					<b>＋</b>
				</button>

				<button
					onclick={() =>
						openPreset(
							'Evening walk',
							'A little movement'
						)}
				>
					<div class="quick-icon walk-icon">🚶</div>

					<div>
						<strong>Walk</strong>
						<span>Daily routine</span>
					</div>

					<b>＋</b>
				</button>
			</div>
		</section>

		<!-- MAIN REMINDER CARD -->

		<section class="reminder-card">

			<div class="section-header">
				<div>
					<p class="eyebrow">MY DAY</p>

					<h2>Today's routine</h2>

					<p>
						Everything you'd like Vcare to keep
						in mind today.
					</p>
				</div>

				<button
					class="add-button"
					onclick={() =>
						(showAddForm = !showAddForm)}
				>
					<span>＋</span>
					Add reminder
				</button>
			</div>

			<!-- ADD FORM -->

			{#if showAddForm}
				<div class="add-panel">

					<div class="form-heading">
						<div class="form-symbol">＋</div>

						<div>
							<strong>New reminder</strong>

							<p>
								Tell Vcare what you'd like
								to remember.
							</p>
						</div>
					</div>

					<div class="form-grid">

						<label>
							<span>Reminder</span>

							<input
								type="text"
								placeholder="e.g. Doctor appointment"
								bind:value={title}
							/>
						</label>

						<label>
							<span>Time</span>

							<input
								type="time"
								bind:value={reminderTime}
							/>
						</label>

						<label>
							<span>Small note</span>

							<input
								type="text"
								placeholder="Optional note"
								bind:value={note}
							/>
						</label>

					</div>

					<div class="form-actions">

						<button
							class="cancel-button"
							onclick={() =>
								(showAddForm = false)}
						>
							Cancel
						</button>

						<button
							class="save-button"
							onclick={addReminder}
						>
							Save reminder →
						</button>

					</div>
				</div>
			{/if}

			<!-- EMPTY STATE -->

			{#if reminders.length === 0}

				<div class="empty-state">

					<div class="empty-art">
						<div class="back-circle"></div>
						<div class="dotted-circle"></div>
						<div class="clock-icon">◷</div>
					</div>

					<h3>Nothing to remember yet.</h3>

					<p>
						Add your first reminder and Vcare will
						keep it ready for your day.
					</p>

					<button
						onclick={() =>
							(showAddForm = true)}
					>
						＋ Add your first reminder
					</button>

				</div>

			{:else}

				<!-- REMINDER TIMELINE -->

				<div class="timeline">

					{#each reminders as reminder}

						<article
							class="timeline-row"
							class:completed={reminder.completed}
						>

							<div class="time">
								<strong>
									{formatTime(reminder.time)}
								</strong>

								<span>
									{reminder.completed
										? 'COMPLETED'
										: 'TODAY'}
								</span>
							</div>

							<div class="timeline-marker">

								<button
									class:checked={reminder.completed}
									onclick={() =>
										toggleReminder(reminder.id)}
									aria-label="Toggle reminder"
								>
									{reminder.completed ? '✓' : ''}
								</button>

							</div>

							<div class="reminder-icon">
								◷
							</div>

							<div class="reminder-copy">

								<strong>
									{reminder.title}
								</strong>

								<span>
									{reminder.note ||
										'Vcare will keep this in mind.'}
								</span>

							</div>

							<div class="row-actions">

								{#if reminder.completed}
									<span class="status done">
										✓ Done
									</span>
								{:else}
									<span class="status pending">
										● Upcoming
									</span>
								{/if}

								<button
									class="delete-button"
									onclick={() =>
										deleteReminder(reminder.id)}
									aria-label="Delete reminder"
								>
									×
								</button>

							</div>

						</article>

					{/each}

				</div>

			{/if}

		</section>

		<!-- INFO CARD -->

		<section class="info-card">

			<div class="heart">
				♡
			</div>

			<div>
				<strong>
					Vcare remembers the little things.
				</strong>

				<p>
					Add appointments, walks, hydration,
					routines or anything else you'd like
					to keep in mind.
				</p>
			</div>

			<div class="info-decoration">
				♡
			</div>

		</section>

		<button class="back-button" onclick={goBack}>
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
				circle at 88% 4%,
				rgba(213, 230, 78, 0.19),
				transparent 27%
			),
			radial-gradient(
				circle at 12% 90%,
				rgba(94, 158, 103, 0.07),
				transparent 24%
			),
			#f9f0e0;
	}

	/* TOP BAR */

	.topbar {
		height: 78px;
		padding: 0 48px;

		border-bottom: 1px solid #e1d4bb;

		background:
			rgba(255, 250, 240, 0.96);

		display: flex;
		align-items: center;
		justify-content: space-between;

		position: sticky;
		top: 0;
		z-index: 20;

		backdrop-filter: blur(12px);
	}

	.brand {
		border: 0;
		padding: 0;

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

	.profile-copy {
		display: flex;
		flex-direction: column;
	}

	.profile-copy strong {
		color: #332e25;
		font-size: 11px;
	}

	.profile-copy span {
		margin-top: 3px;

		color: #887b69;
		font-size: 8px;
	}

	/* CONTENT */

	.content {
		width: min(
			1080px,
			calc(100% - 42px)
		);

		margin: 0 auto;

		padding: 58px 0 70px;
	}

	/* HERO */

	.hero {
		margin-bottom: 25px;

		display: flex;
		align-items: flex-end;
		justify-content: space-between;
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
			clamp(45px, 5vw, 65px);

		font-weight: 600;
		line-height: 0.98;

		letter-spacing: -2px;
	}

	.hero h1 span {
		color: #78a64a;
	}

	.hero-copy {
		margin: 15px 0 0;

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

		display: grid;
		place-items: center;

		font-size: 20px;
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

	/* QUICK ADD */

	.quick-section {
		margin-bottom: 18px;
	}

	.quick-title {
		margin-bottom: 10px;

		display: flex;
		align-items: baseline;
		gap: 12px;
	}

	.quick-title span {
		color: #45705a;

		font-size: 8px;
		font-weight: 900;
		letter-spacing: 1.4px;
	}

	.quick-title p {
		margin: 0;

		color: #968a78;

		font-size: 8px;
	}

	.quick-grid {
		display: grid;

		grid-template-columns:
			repeat(3, 1fr);

		gap: 11px;
	}

	.quick-grid button {
		padding: 15px 16px;

		border:
			1px solid #dfd1b8;

		border-radius: 16px;

		background:
			rgba(255, 250, 240, 0.9);

		color: #35493d;

		display: grid;

		grid-template-columns:
			42px 1fr auto;

		align-items: center;

		gap: 11px;

		text-align: left;

		transition:
			transform 0.18s,
			background 0.18s,
			box-shadow 0.18s;
	}

	.quick-grid button:hover {
		transform:
			translateY(-2px);

		background: #fffdf4;

		box-shadow:
			0 8px 20px
			rgba(62, 48, 27, 0.06);
	}

	.quick-icon {
		width: 40px;
		height: 40px;

		border-radius: 12px;

		display: grid;
		place-items: center;

		font-size: 19px;
	}

	.medicine-icon {
		background: #eef2c8;
	}

	.water-icon {
		background: #e6f1e7;
	}

	.walk-icon {
		background: #f5ead2;
	}

	.quick-grid button > div:nth-child(2) {
		display: flex;
		flex-direction: column;
	}

	.quick-grid strong {
		font-size: 11px;
	}

	.quick-grid button span {
		margin-top: 3px;

		color: #8b7f6e;

		font-size: 7px;
	}

	.quick-grid b {
		color: #7a9e59;

		font-size: 15px;
	}

	/* MAIN CARD */

	.reminder-card {
		padding: 28px 31px 23px;

		border:
			1px solid #ddceb2;

		border-radius: 24px;

		background:
			rgba(255, 250, 240, 0.96);

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
		justify-content: space-between;
		gap: 25px;
	}

	.section-header h2 {
		margin: 0;

		color: #294a3a;

		font-size: 27px;
		line-height: 1.1;
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

		display: flex;
		align-items: center;
		gap: 7px;

		font-size: 9px;
		font-weight: 800;
	}

	.add-button span {
		font-size: 14px;
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

		font-size: 19px;
		font-weight: 900;
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
			1.3fr 0.65fr 1fr;

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
		justify-content: flex-end;
		gap: 8px;
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

	.save-button:hover {
		background: #0e663f;
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

	.empty-art {
		width: 90px;
		height: 90px;

		margin-bottom: 8px;

		position: relative;
	}

	.back-circle {
		width: 70px;
		height: 70px;

		position: absolute;

		left: 5px;
		top: 5px;

		border-radius: 23px;

		background: #eef2c7;

		transform: rotate(-8deg);
	}

	.dotted-circle {
		width: 48px;
		height: 48px;

		position: absolute;

		right: 1px;
		bottom: 2px;

		border:
			1px dashed #85a568;

		border-radius: 50%;
	}

	.clock-icon {
		position: absolute;

		left: 26px;
		top: 25px;

		color: #597a4c;

		font-size: 30px;
	}

	.empty-state h3 {
		margin: 0;

		color: #355646;

		font-size: 20px;
	}

	.empty-state p {
		max-width: 360px;

		margin: 8px 0 17px;

		color: #837664;

		font-size: 9px;
		line-height: 1.55;
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

	/* TIMELINE */

	.timeline {
		margin-top: 4px;
	}

	.timeline-row {
		min-height: 86px;

		display: grid;

		grid-template-columns:
			100px
			40px
			46px
			minmax(0, 1fr)
			auto;

		align-items: center;

		border-bottom:
			1px solid #eadfc9;

		transition:
			background 0.2s,
			opacity 0.2s;
	}

	.timeline-row:hover {
		background:
			rgba(238, 242, 207, 0.22);
	}

	.timeline-row.completed {
		opacity: 0.58;
	}

	.time {
		display: flex;
		flex-direction: column;
	}

	.time strong {
		color: #28704e;

		font-size: 10px;
	}

	.time span {
		margin-top: 3px;

		color: #90947f;

		font-size: 6px;
		letter-spacing: 0.9px;
	}

	.timeline-marker {
		height: 100%;

		position: relative;

		display: grid;
		place-items: center;
	}

	.timeline-marker::before {
		content: "";

		position: absolute;

		top: 0;
		bottom: 0;

		width: 1px;

		background: #ddd5b7;
	}

	.timeline-marker button {
		width: 21px;
		height: 21px;

		z-index: 2;

		border:
			2px solid #8ea56b;

		border-radius: 50%;

		background: #fffaf0;
		color: white;

		display: grid;
		place-items: center;

		font-size: 8px;
		font-weight: 900;
	}

	.timeline-marker button.checked {
		border-color: #68a161;
		background: #68a161;
	}

	.reminder-icon {
		width: 35px;
		height: 35px;

		border-radius: 10px;

		background: #eff1ca;

		display: grid;
		place-items: center;

		color: #5d754d;

		font-size: 16px;
	}

	.reminder-copy {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.reminder-copy strong {
		color: #35473d;

		font-size: 10px;
	}

	.reminder-copy span {
		color: #887d6c;

		font-size: 7px;
	}

	.row-actions {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.status {
		padding: 6px 9px;

		border-radius: 9px;

		font-size: 7px;
		font-weight: 800;
	}

	.status.pending {
		background: #f5edcf;
		color: #957726;
	}

	.status.done {
		background: #e6efd3;
		color: #508049;
	}

	.delete-button {
		width: 27px;
		height: 27px;

		border:
			1px solid #dbcdb6;

		border-radius: 8px;

		background: transparent;
		color: #978a76;

		display: grid;
		place-items: center;

		font-size: 14px;
	}

	.delete-button:hover {
		background: #f5eadf;
		color: #a85e4a;
	}

	/* INFO */

	.info-card {
		margin-top: 17px;
		padding: 18px 20px;

		border:
			1px solid #d8d7a9;

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

	.heart {
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

	.info-card strong {
		color: #386346;

		font-size: 10px;
	}

	.info-card p {
		margin: 4px 0 0;

		color: #796e5d;

		font-size: 8px;
		line-height: 1.5;
	}

	.info-decoration {
		position: absolute;

		right: 25px;
		top: -15px;

		color:
			rgba(86, 133, 72, 0.08);

		font-size: 90px;
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

	/* MOBILE */

	@media (max-width: 760px) {
		.topbar {
			height: 72px;
			padding: 0 18px;
		}

		.brand-copy span {
			display: none;
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

		.quick-grid {
			grid-template-columns: 1fr;
		}

		.reminder-card {
			padding: 22px 17px;
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

		.timeline-row {
			padding: 14px 0;

			grid-template-columns:
				74px
				33px
				41px
				1fr;

			row-gap: 11px;
		}

		.row-actions {
			grid-column: 1 / -1;

			justify-content: flex-end;
		}
	}
</style>
