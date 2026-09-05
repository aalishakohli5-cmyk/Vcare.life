<script>
	import AccountSettings from '$lib/components/AccountSettings.svelte';
	import '../theme.css';
</script>

<div class="caregiver-settings-shell" data-caregiver-portal>
	<aside class="sidebar">
		<a href="/caregiver/dashboard" class="brand">
			<span class="brand-heart" aria-hidden="true">♥</span>
			<span><strong>Vcare.life</strong><small>A Voice That Cares</small></span>
		</a>

		<p class="care-label">CAREGIVER SPACE</p>
		<nav aria-label="Caregiver navigation">
			<a href="/caregiver/dashboard"><span aria-hidden="true">⌂</span>Home</a>
			<a href="/caregiver/medicines"><span aria-hidden="true">✚</span>Medicines</a>
			<a href="/caregiver/calls"><span aria-hidden="true">☎</span>Vcare Calls</a>
			<a href="/caregiver/senior"><span aria-hidden="true">♡</span>Senior Profile</a>
			<a href="/caregiver/settings" class="active" aria-current="page"><span aria-hidden="true">⚙</span>Settings</a>
		</nav>
	</aside>

	<div class="content">
		<AccountSettings role="caregiver" dashboardHref="/caregiver/dashboard" />
	</div>
</div>

<style>
	:global(body) { margin: 0; background: #f7faf7; }
	.caregiver-settings-shell { min-height: 100vh; display: grid; grid-template-columns: 270px minmax(0, 1fr); }
	.sidebar {
		position: sticky;
		top: 0;
		display: flex;
		min-height: 100vh;
		box-sizing: border-box;
		flex-direction: column;
		padding: 30px 20px;
		background: #123f31;
		color: #fff;
	}
	.brand { display: flex; align-items: center; gap: 13px; color: #fff; text-decoration: none; }
	.brand-heart { display: grid; width: 46px; height: 46px; place-items: center; border-radius: 13px; background: #d7ee59; color: #174b37; font-size: 22px; }
	.brand strong { display: block; font-size: 1.34rem; }
	.brand small { display: block; margin-top: 2px; color: #afc4bb; }
	.care-label { margin: 54px 12px 16px; color: #d7ee59; font-size: 0.78rem; font-weight: 900; letter-spacing: 0.13em; }
	nav { display: grid; gap: 8px; }
	nav a { display: flex; min-height: 52px; align-items: center; gap: 15px; padding: 8px 14px; border-radius: 13px; color: #d8e4df; font-size: 1.02rem; font-weight: 800; text-decoration: none; }
	nav a span { width: 28px; text-align: center; font-size: 1.2rem; }
	nav a:hover { background: rgba(255,255,255,0.08); color: #fff; }
	nav a.active { background: #d7ee59; color: #173f31; }
	.content { min-width: 0; background: radial-gradient(circle at 90% 0%, #edf8da 0, transparent 32%), #f8faf7; }

	@media (max-width: 820px) {
		.caregiver-settings-shell { display: block; }
		.sidebar { position: static; min-height: auto; padding: 16px; }
		.care-label { margin: 20px 4px 10px; }
		nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
		nav a { font-size: 0.9rem; }
	}
</style>
