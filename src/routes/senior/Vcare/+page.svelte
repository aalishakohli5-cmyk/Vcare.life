<script>
	import { goto } from '$app/navigation';

	let calls = $state([
		{
			id: 1,
			date: 'Today',
			time: '12:24 AM',
			status: 'completed',
			duration: '1m 18s',
			mood: 'Good',
			summary: 'Medication check-in completed.',
			details: 'Vcare asked about the scheduled medicine and completed the check-in.'
		},
		{
			id: 2,
			date: 'Yesterday',
			time: '6:02 PM',
			status: 'completed',
			duration: '3m 42s',
			mood: 'Okay',
			summary: 'Daily wellness check-in completed.',
			details: 'Discussed mood, medicines and the senior’s daily routine.'
		},
		{
			id: 3,
			date: '14 Aug',
			time: '6:05 PM',
			status: 'missed',
			duration: '—',
			mood: '—',
			summary: 'Vcare could not reach you.',
			details: 'The call was not answered.'
		}
	]);

	let selectedCall = $state(null);

	function goBack() {
		goto('/senior/dashboard');
	}

	function openCall(call) {
		selectedCall = call;
	}

	function closeCall() {
		selectedCall = null;
	}

	function statusText(call) {
		return call.status === 'completed'
			? 'Completed'
			: 'Missed';
	}
</script>

<svelte:head>
	<title>Vcare Calls — Vcare.life</title>
</svelte:head>

<div class="page">
	<aside class="senior-sidebar">
		<a class="side-brand" href="/senior/dashboard">
			<span class="side-logo">♥</span>
			<span><strong>Vcare.life</strong><small>A Voice That Cares</small></span>
		</a>

		<nav class="side-nav" aria-label="Senior navigation">
			<a href="/senior/dashboard"><span>⌂</span><div><strong>Home</strong><small>Your day at a glance</small></div></a>
			<a href="/senior/medications"><span>✚</span><div><strong>Medicines</strong><small>Your medication plan</small></div></a>
			<a href="/senior/reminder"><span>◷</span><div><strong>Reminders</strong><small>Your routine & plans</small></div></a>
			<a href="/senior/Vcare" class="active"><span>☎</span><div><strong>Vcare Calls</strong><small>Calls & summaries</small></div></a>
			<a href="/senior/care-circle"><span>♡</span><div><strong>Care Circle</strong><small>Your trusted people</small></div></a>
		</nav>

		<div class="side-note"><span>☎</span><div><strong>Daily check-ins</strong><small>Care that stays close.</small></div></div>
	</aside>

	<header class="topbar">

		<div class="profile">
			<div class="avatar">A</div>

			<div>
				<strong>Aalisha</strong>
				<span>My calls</span>
			</div>
		</div>

	</header>


	<main class="content">

		<!-- HERO -->

		<section class="hero">

			<div>
				<p class="eyebrow">
					YOUR CONVERSATIONS
				</p>

				<h1>
					Vcare <span>calls.</span>
				</h1>

				<p class="hero-copy">
					A simple history of your Vcare check-ins,
					conversations and daily moments of care.
				</p>
			</div>

			<div class="summary-card">

				<div class="summary-icon">
					☎
				</div>

				<div>
					<strong>{calls.length}</strong>
					<span>recent calls</span>
				</div>

			</div>

		</section>


		<!-- STATS -->

		<section class="stats">

			<div class="stat-card">

				<div class="stat-icon green">
					✓
				</div>

				<div>
					<strong>
						{calls.filter(
							(call) =>
								call.status === 'completed'
						).length}
					</strong>

					<span>Completed</span>
				</div>

			</div>


			<div class="stat-card">

				<div class="stat-icon yellow">
					☺
				</div>

				<div>
					<strong>Good</strong>
					<span>Latest mood</span>
				</div>

			</div>


			<div class="stat-card">

				<div class="stat-icon cream">
					◷
				</div>

				<div>
					<strong>Daily</strong>
					<span>Check-in routine</span>
				</div>

			</div>

		</section>


		<!-- NEXT CALL -->

		<section class="next-call">

			<div class="phone-visual">

				<div class="speaker"></div>

				<div class="screen">
					<small>VCARE</small>
					<strong>Hello there!</strong>
					<span>♡</span>
				</div>

				<div class="phone-buttons">
					<i>☎</i>
					<i>•</i>
					<i>×</i>
				</div>

			</div>


			<div class="next-copy">

				<p>NEXT VCARE CHECK-IN</p>

				<h2>
					Today at
					<span>6:00 PM</span>
				</h2>

				<p class="description">
					Vcare can check in about your medicines,
					how you're feeling and anything you'd like
					to remember.
				</p>

				<div class="chips">
					<span>♡ Daily check-in</span>
					<span>💊 Medicine</span>
					<span>◷ Reminders</span>
				</div>

			</div>


			<div class="scheduled-card">

				<small>STATUS</small>

				<strong>Scheduled</strong>

				<span>
					Vcare is ready for your next check-in.
				</span>

			</div>

		</section>


		<!-- CALL HISTORY -->

		<section class="history-card">

			<div class="section-header">

				<div>
					<p class="eyebrow">
						CALL HISTORY
					</p>

					<h2>
						Recent conversations
					</h2>

					<p>
						Your latest check-ins with Vcare.
					</p>
				</div>

				<div class="call-count">
					☎ {calls.length} calls
				</div>

			</div>


			<div class="calls-list">

				{#each calls as call}

					<button
						class="call-row"
						onclick={() => openCall(call)}
					>

						<div
							class="call-icon"
							class:missed={call.status === 'missed'}
						>
							☎
						</div>


						<div class="call-main">

							<div class="call-top">

								<div>
									<strong>
										{call.date},
										{call.time}
									</strong>

									<span>
										Daily Vcare check-in
									</span>
								</div>


								<div
									class="status"
									class:missed-status={call.status === 'missed'}
								>
									{statusText(call)}
								</div>

							</div>


							<div class="metadata">

								{#if call.status === 'completed'}

									<span>
										◷ {call.duration}
									</span>

									<i>•</i>

									<span>
										☺ Mood: {call.mood}
									</span>

								{:else}

									<span>
										No conversation recorded
									</span>

								{/if}

							</div>


							<p>
								{call.summary}
							</p>

						</div>


						<div class="arrow">
							→
						</div>

					</button>

				{/each}

			</div>

		</section>


		<!-- INFO -->

		<section class="info-card">

			<div class="info-heart">
				♡
			</div>

			<div>
				<strong>
					Small conversations. A little more care.
				</strong>

				<p>
					Vcare keeps your check-ins simple,
					personal and easy to look back on.
				</p>
			</div>

			<div class="big-heart">
				♡
			</div>

		</section>


		<button
			class="back-button"
			onclick={goBack}
		>
			← Back to dashboard
		</button>

	</main>


	<!-- DETAIL MODAL -->

	{#if selectedCall}

		<div
			class="modal-backdrop"
			onclick={closeCall}
		>

			<div
				class="modal"
				onclick={(event) =>
					event.stopPropagation()}
			>

				<div class="modal-header">

					<div class="modal-icon">
						☎
					</div>

					<button
						class="close-button"
						onclick={closeCall}
					>
						×
					</button>

				</div>


				<p class="eyebrow">
					VCARE CHECK-IN
				</p>

				<h2>
					{selectedCall.date},
					{selectedCall.time}
				</h2>


				<div class="modal-status-row">

					<span
						class="status"
						class:missed-status={
							selectedCall.status === 'missed'
						}
					>
						{statusText(selectedCall)}
					</span>

					{#if selectedCall.status === 'completed'}

						<span>
							◷ {selectedCall.duration}
						</span>

						<span>
							☺ {selectedCall.mood}
						</span>

					{/if}

				</div>


				<div class="summary-box">

					<small>SUMMARY</small>

					<strong>
						{selectedCall.summary}
					</strong>

					<p>
						{selectedCall.details}
					</p>

				</div>


				<button
					class="modal-done"
					onclick={closeCall}
				>
					Done
				</button>

			</div>

		</div>

	{/if}

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

	button {
		font: inherit;
		cursor: pointer;
	}

	.page {
		min-height: 100vh;

		background:
			radial-gradient(
				circle at 90% 4%,
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


	/* TOPBAR */

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


	/* MAIN */

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
		margin-bottom: 23px;

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

		color: #346545;

		display: grid;

		place-items: center;

		font-size: 19px;
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


	/* STATS */

	.stats {
		margin-bottom: 18px;

		display: grid;

		grid-template-columns:
			repeat(3, 1fr);

		gap: 11px;
	}

	.stat-card {
		padding: 15px 17px;

		border:
			1px solid #dfd1b8;

		border-radius: 16px;

		background:
			rgba(255, 250, 240, 0.92);

		display: flex;

		align-items: center;

		gap: 11px;
	}

	.stat-icon {
		width: 40px;

		height: 40px;

		border-radius: 12px;

		display: grid;

		place-items: center;

		font-size: 17px;
	}

	.stat-icon.green {
		background: #e5efd0;

		color: #4f8147;
	}

	.stat-icon.yellow {
		background: #f3edc5;

		color: #9a7d25;
	}

	.stat-icon.cream {
		background: #f3e7d3;

		color: #836748;
	}

	.stat-card > div:last-child {
		display: flex;

		flex-direction: column;
	}

	.stat-card strong {
		color: #35493d;

		font-size: 11px;
	}

	.stat-card span {
		margin-top: 3px;

		color: #8b7f6e;

		font-size: 7px;
	}


	/* NEXT CALL */

	.next-call {
		margin-bottom: 18px;

		min-height: 205px;

		padding: 27px 30px;

		border-radius: 24px;

		background:
			linear-gradient(
				110deg,
				#075f40,
				#08794c 62%,
				#076844
			);

		color: white;

		display: grid;

		grid-template-columns:
			100px
			minmax(0, 1fr)
			190px;

		align-items: center;

		gap: 26px;

		position: relative;

		overflow: hidden;

		box-shadow:
			0 16px 34px
			rgba(9, 91, 59, 0.13);
	}

	.next-call::after {
		content: "♡";

		position: absolute;

		right: 34%;

		top: -18px;

		color:
			rgba(
				218,
				232,
				80,
				0.12
			);

		font-size: 130px;
	}

	.phone-visual {
		width: 83px;

		height: 137px;

		padding: 10px 8px;

		border:
			5px solid #6d9134;

		border-radius: 20px;

		background: #a8ca3e;

		transform: rotate(-4deg);

		position: relative;

		z-index: 2;
	}

	.speaker {
		width: 32px;

		height: 5px;

		margin: 0 auto 7px;

		border-radius: 10px;

		background: #5c7932;
	}

	.screen {
		height: 72px;

		border:
			3px solid #35623a;

		border-radius: 9px;

		background: #ddea4e;

		color: #17442d;

		display: flex;

		flex-direction: column;

		align-items: center;

		justify-content: center;
	}

	.screen small {
		font-size: 5px;

		font-weight: 900;
	}

	.screen strong {
		margin-top: 3px;

		font-size: 7px;
	}

	.screen span {
		margin-top: 2px;

		font-size: 17px;
	}

	.phone-buttons {
		margin-top: 8px;

		display: flex;

		justify-content:
			space-between;
	}

	.phone-buttons i {
		width: 18px;

		height: 18px;

		border-radius: 50%;

		background:
			rgba(
				255,
				255,
				255,
				0.5
			);

		display: grid;

		place-items: center;

		color: #28573a;

		font-size: 7px;

		font-style: normal;
	}

	.phone-buttons i:first-child {
		background: #16754b;

		color: white;
	}

	.phone-buttons i:last-child {
		background: #e05d53;

		color: white;
	}

	.next-copy {
		position: relative;

		z-index: 2;
	}

	.next-copy > p:first-child {
		margin: 0 0 7px;

		color: #dce95b;

		font-size: 7px;

		font-weight: 900;

		letter-spacing: 1.4px;
	}

	.next-copy h2 {
		margin: 0;

		font-size: 27px;

		font-weight: 500;
	}

	.next-copy h2 span {
		color: #ddeb50;
	}

	.description {
		max-width: 500px;

		margin: 11px 0 14px;

		color:
			rgba(
				255,
				255,
				255,
				0.8
			);

		font-size: 8px;

		line-height: 1.6;
	}

	.chips {
		display: flex;

		gap: 7px;
	}

	.chips span {
		padding: 6px 8px;

		border:
			1px solid
			rgba(
				255,
				255,
				255,
				0.2
			);

		border-radius: 10px;

		background:
			rgba(
				255,
				255,
				255,
				0.06
			);

		font-size: 6px;
	}

	.scheduled-card {
		padding: 16px;

		border-left:
			1px solid
			rgba(
				255,
				255,
				255,
				0.18
			);

		display: flex;

		flex-direction: column;

		position: relative;

		z-index: 2;
	}

	.scheduled-card small {
		color: #dce95b;

		font-size: 6px;

		letter-spacing: 1.3px;
	}

	.scheduled-card strong {
		margin-top: 7px;

		font-size: 17px;
	}

	.scheduled-card span {
		margin-top: 6px;

		color:
			rgba(
				255,
				255,
				255,
				0.7
			);

		font-size: 7px;

		line-height: 1.5;
	}


	/* HISTORY */

	.history-card {
		padding: 28px 31px 20px;

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
		padding-bottom: 20px;

		border-bottom:
			1px solid #eadfc9;

		display: flex;

		align-items: flex-start;

		justify-content:
			space-between;
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

	.call-count {
		padding: 8px 11px;

		border-radius: 10px;

		background: #eff2ce;

		color: #527448;

		font-size: 8px;

		font-weight: 800;
	}

	.calls-list {
		margin-top: 3px;
	}

	.call-row {
		width: 100%;

		padding: 18px 3px;

		border: 0;

		border-bottom:
			1px solid #eadfc9;

		background: transparent;

		color: inherit;

		display: grid;

		grid-template-columns:
			48px
			minmax(0, 1fr)
			30px;

		align-items: center;

		gap: 13px;

		text-align: left;

		transition:
			background 0.18s;
	}

	.call-row:hover {
		background:
			rgba(
				239,
				242,
				207,
				0.28
			);
	}

	.call-icon {
		width: 39px;

		height: 39px;

		border-radius: 12px;

		background: #e7f0d5;

		color: #4e7e48;

		display: grid;

		place-items: center;
	}

	.call-icon.missed {
		background: #f5dfd5;

		color: #a55f50;
	}

	.call-main {
		min-width: 0;
	}

	.call-top {
		display: flex;

		align-items: flex-start;

		justify-content:
			space-between;

		gap: 15px;
	}

	.call-top > div:first-child {
		display: flex;

		flex-direction: column;
	}

	.call-top strong {
		color: #35463c;

		font-size: 10px;
	}

	.call-top span {
		margin-top: 3px;

		color: #897d6c;

		font-size: 7px;
	}

	.status {
		padding: 6px 9px;

		border-radius: 9px;

		background: #e6efd3;

		color: #508049;

		font-size: 7px;

		font-weight: 800;
	}

	.status.missed-status {
		background: #f5dfd5;

		color: #a25e50;
	}

	.metadata {
		margin-top: 9px;

		display: flex;

		align-items: center;

		gap: 7px;

		color: #918575;

		font-size: 7px;
	}

	.metadata i {
		font-style: normal;
	}

	.call-main > p {
		margin: 7px 0 0;

		color: #6f6658;

		font-size: 8px;

		line-height: 1.5;
	}

	.arrow {
		color: #72975a;

		font-size: 15px;
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

	.info-heart {
		width: 42px;

		height: 42px;

		border-radius: 12px;

		background:
			rgba(
				255,
				255,
				255,
				0.55
			);

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
	}

	.big-heart {
		position: absolute;

		right: 25px;

		top: -26px;

		color:
			rgba(
				86,
				133,
				72,
				0.08
			);

		font-size: 100px;
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


	/* MODAL */

	.modal-backdrop {
		position: fixed;

		inset: 0;

		z-index: 100;

		padding: 20px;

		background:
			rgba(
				25,
				39,
				31,
				0.36
			);

		backdrop-filter: blur(6px);

		display: grid;

		place-items: center;
	}

	.modal {
		width:
			min(470px, 100%);

		padding: 27px;

		border:
			1px solid #ded0b5;

		border-radius: 23px;

		background: #fffaf0;

		box-shadow:
			0 25px 70px
			rgba(30, 38, 31, 0.2);
	}

	.modal-header {
		display: flex;

		align-items: center;

		justify-content:
			space-between;

		margin-bottom: 17px;
	}

	.modal-icon {
		width: 48px;

		height: 48px;

		border-radius: 14px;

		background: #e8f0d5;

		color: #4e7d48;

		display: grid;

		place-items: center;

		font-size: 19px;
	}

	.close-button {
		width: 32px;

		height: 32px;

		border:
			1px solid #ddceb5;

		border-radius: 9px;

		background: transparent;

		color: #897c69;

		font-size: 17px;
	}

	.modal h2 {
		margin: 0;

		color: #294a3a;

		font-size: 24px;
	}

	.modal-status-row {
		margin-top: 13px;

		display: flex;

		align-items: center;

		gap: 8px;

		color: #847867;

		font-size: 8px;
	}

	.summary-box {
		margin-top: 20px;

		padding: 17px;

		border:
			1px solid #dcdbab;

		border-radius: 15px;

		background:
			linear-gradient(
				120deg,
				#eff3ce,
				#fff8e8
			);

		display: flex;

		flex-direction: column;
	}

	.summary-box small {
		color: #648151;

		font-size: 7px;

		font-weight: 900;

		letter-spacing: 1.2px;
	}

	.summary-box strong {
		margin-top: 8px;

		color: #354b3d;

		font-size: 10px;
	}

	.summary-box p {
		margin: 7px 0 0;

		color: #786e5e;

		font-size: 8px;

		line-height: 1.6;
	}

	.modal-done {
		width: 100%;

		margin-top: 18px;

		padding: 10px;

		border: 0;

		border-radius: 10px;

		background: #14784c;

		color: white;

		font-size: 9px;

		font-weight: 800;
	}


	@media (max-width: 760px) {

		.topbar {
			padding: 0 18px;
		}

		.content {
			width:
				calc(
					100% - 26px
				);

			padding-top: 34px;
		}

		.hero {
			align-items:
				flex-start;

			flex-direction:
				column;
		}

		.summary-card {
			width: 100%;
		}

		.stats {
			grid-template-columns:
				1fr;
		}

		.next-call {
			grid-template-columns:
				80px 1fr;

			padding: 22px;
		}

		.scheduled-card {
			grid-column:
				1 / -1;

			border-left: 0;

			border-top:
				1px solid
				rgba(
					255,
					255,
					255,
					0.18
				);
		}

		.history-card {
			padding:
				22px 17px;
		}

		.section-header {
			gap: 12px;
		}

		.call-row {
			grid-template-columns:
				44px
				1fr;
		}

		.arrow {
			display: none;
		}

		.call-top {
			flex-direction:
				column;
		}
	}

	/* Unified senior navigation and modern page shell */
	:global(body) { font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f3f5ef; }
	.page { display: grid; grid-template-columns: 250px minmax(0,1fr); grid-template-rows: auto 1fr; background: radial-gradient(circle at 86% 5%, rgba(203,230,99,.22), transparent 28%), linear-gradient(180deg,#f8faf5 0%,#f1f4ed 100%); }
	.topbar { grid-column: 2; height: 82px; justify-content: flex-end; border-color: rgba(25,82,61,.1); background: rgba(250,252,247,.88); backdrop-filter: blur(18px); }
	.content { grid-column: 2; width: min(1180px,92%); }
	.hero h1 { font-family: Georgia, "Times New Roman", serif; letter-spacing: -2.5px; }
	.hero h1 span { font-family: Inter, ui-sans-serif, sans-serif; font-weight: 650; }
	.stats .stat-card, .history-card, .summary-card, .info-card { border-color: rgba(32,83,63,.11); background: rgba(255,255,255,.78); box-shadow: 0 18px 56px rgba(24,62,47,.07); }
	.next-call { box-shadow: 0 24px 60px rgba(13,91,61,.17); }
	.call-row { border-radius: 16px; transition: background .2s ease, transform .2s ease; }
	.call-row:hover { background: #f5f8f2; transform: translateX(3px); }

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

	@media (max-width: 820px) { .page { display:block; } .senior-sidebar { display:none; } .topbar { padding-inline:20px; } }
</style>
