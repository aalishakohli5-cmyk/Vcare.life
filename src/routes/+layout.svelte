<script>
	import 'uno.css'
	import "$asset/stylesheet/global.css"
	import favicon from '$lib/assets/favicon.svg';

	import Tabbar from "$component/Tabbar"

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="page">
  <main class="page__content" w-screen-2xl>
    {@render children()}
  </main>
</div>
<Tabbar/>
