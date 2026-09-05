<script>
	import 'uno.css';
	import '../app.css';
	import '$asset/stylesheet/global.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..500&family=Public+Sans:ital,wght@0,300..800;1,300..800&display=swap"
		rel="stylesheet"
	/>
  <link rel="icon" href={favicon} />
  <meta name="description" content="Vcare.life helps seniors and their families stay connected with voice check-ins, medication reminders, and shared care updates." />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Vcare.life" />
  <meta property="og:title" content="Vcare.life — A Voice That Cares" />
  <meta property="og:description" content="Voice check-ins, medication reminders, and simple care updates for seniors and their families." />
  <meta property="og:image" content="/grandma.jpg" />
  <meta name="twitter:card" content="summary_large_image" />
</svelte:head>

{@render children()}
