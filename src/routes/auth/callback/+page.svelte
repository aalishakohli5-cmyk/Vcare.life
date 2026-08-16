<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { supabase } from '$lib/supabase';

  let message = 'Finishing your Google sign-in...';

  onMount(() => {
    const role = page.url.searchParams.get('role') ?? 'senior';

    const { data: authListener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (session) {
          goto(`/onboarding/${role}`);
        }
      }
    );

    async function finishLogin() {
      const { data, error } = await supabase.auth.getSession();

      if (error) {
        console.error(error);
        message = 'We could not finish signing you in.';
        return;
      }

      if (data.session) {
        goto(`/onboarding/${role}`);
      }
    }

    finishLogin();

    return () => {
      authListener.subscription.unsubscribe();
    };
  });
</script>

<svelte:head>
  <title>Signing in — Vcare.life</title>
</svelte:head>

<div class="callback-page">
  <div class="loader"></div>

  <h1>Welcome to Vcare.life</h1>
  <p>{message}</p>
</div>

<style>
  :global(body) {
    margin: 0;
    font-family: Inter, system-ui, sans-serif;
    background: #f8f7ef;
  }

  .callback-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #153d32;
  }

  h1 {
    margin: 20px 0 8px;
    font-family: Georgia, serif;
    font-size: 42px;
    font-weight: 500;
  }

  p {
    color: #718078;
  }

  .loader {
    width: 42px;
    height: 42px;
    border: 4px solid #dbe8d8;
    border-top-color: #176348;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
