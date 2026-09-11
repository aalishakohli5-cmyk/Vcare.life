<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabase';

  let message = $state('Finishing your Google sign-in...');

  onMount(() => {
    let role = 'senior';
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      role = params.get('role') || 'senior';
    }

    async function handleRedirect(session) {
      if (!session?.user) return;

      try {
        const { data: profile } = await supabase
          .from('profiles')
          .select('role, onboarding_complete')
          .eq('id', session.user.id)
          .maybeSingle();

        const userRole = profile?.role || role;

        if (profile?.onboarding_complete) {
          goto(`/${userRole}/dashboard`);
        } else {
          goto(`/onboarding/${userRole}`);
        }
      } catch (err) {
        console.error('Redirect check error:', err);
        goto(`/onboarding/${role}`);
      }
    }

    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        if (session) {
          await handleRedirect(session);
        }
      }
    );

    async function finishLogin() {
      try {
        const { data, error } = await supabase.auth.getSession();

        if (error) {
          console.error(error);
          message = 'We could not finish signing you in. Please try again.';
          return;
        }

        if (data?.session) {
          await handleRedirect(data.session);
        }
      } catch (err) {
        console.error(err);
      }
    }

    finishLogin();

    return () => {
      authListener?.subscription?.unsubscribe();
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
