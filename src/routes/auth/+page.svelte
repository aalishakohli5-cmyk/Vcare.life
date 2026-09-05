<script>

  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabase';

  let email = $state('');
  let password = $state('');
  let showPassword = $state(false);
  let mode = $state('signin');
  let loading = $state(false);
  let errorMessage = $state('');

  const role = page.url.searchParams.get('role') ?? 'senior';

  const isSenior = role === 'senior';

  async function continueWithEmail() {
    errorMessage = '';

    if (!email || !password) {
      errorMessage = 'Please enter your email and password.';
      return;
    }

    if (password.length < 6) {
      errorMessage = 'Password must be at least 6 characters.';
      return;
    }

    loading = true;

    try {
      if (mode === 'signup') {
        // Sign up
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              role: role
            }
          }
        });

        if (error) {
          errorMessage = error.message;
          loading = false;
          return;
        }

        // Redirect to onboarding
        goto(`/onboarding/${role}`);
      } else {
        // Sign in
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password
        });

        if (error) {
          errorMessage = error.message;
          loading = false;
          return;
        }

        // Redirect to dashboard
        goto(`/${role}/dashboard`);
      }
    } catch (error) {
      errorMessage = 'An error occurred. Please try again.';
      console.error(error);
    } finally {
      loading = false;
    }
  }

  async function continueWithGoogle() {
    errorMessage = '';
    loading = true;

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback?role=${role}`
        }
      });

      if (error) {
        errorMessage = error.message;
      }
    } catch (error) {
      errorMessage = 'Google sign-in failed. Please try again.';
      console.error(error);
    } finally {
      loading = false;
    }
  }

  function toggleMode() {
    errorMessage = '';
    mode = mode === 'signin' ? 'signup' : 'signin';
    email = '';
    password = '';
  }

</script>


<svelte:head>
  <title>
    {mode === 'signin' ? 'Sign in' : 'Create account'} — Vcare.life
  </title>

  <meta
    name="description"
    content="Sign in to your Vcare.life account."
  />

  <!-- Fonts — same as landing page -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link
    href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..500&family=Public+Sans:wght@300..700&display=swap"
    rel="stylesheet"
  />
</svelte:head>


<div class="auth-page">

  <!-- =====================================================
       LEFT SIDE
       ===================================================== -->

  <section class="auth-story">

    <!-- Same grandma.jpg + warm amber/sepia overlay as the landing page -->
    <img
      src="/grandma.jpg"
      alt="Senior woman happily talking on the phone"
      class="story-photo"
    />

    <div class="story-overlay"></div>

    <a href="/" class="brand">
      <div class="brand-heart">♥</div>

      <div>
        <strong>Vcare.life</strong>
        <span>A Voice That Cares</span>
      </div>
    </a>


    <div class="story-content">

      <p class="eyebrow">
        {isSenior ? 'YOUR CARE, YOUR SPACE' : 'CARE THAT STAYS CLOSE'}
      </p>

      {#if isSenior}

        <h1>
          A little support,
          <span>whenever you need it.</span>
        </h1>

        <p>
          Your reminders, appointments, wellness check-ins
          and Vcare companion — all in one calm, simple place.
        </p>

      {:else}

        <h1>
          Stay close,
          <span>even when you're apart.</span>
        </h1>

        <p>
          Keep up with medicines, appointments, check-ins
          and the little moments that matter.
        </p>

      {/if}


      <div class="story-points">

        <div>
          <span>✓</span>
          Private & secure
        </div>

        <div>
          <span>✓</span>
          One connected care space
        </div>

        <div>
          <span>✓</span>
          Made for families
        </div>

      </div>

    </div>


    <p class="story-footer">
      ♡ Because care should always feel close.
    </p>

  </section>



  <!-- =====================================================
       RIGHT SIDE
       ===================================================== -->

  <section class="auth-panel">

    <div class="panel-glow"></div>

    <div class="auth-box">

      <!-- Role -->

      <div class="role-pill">

        <span class="role-icon">
          {isSenior ? '♡' : '👥'}
        </span>

        <div>
          <span>CONTINUING AS</span>

          <strong>
            {isSenior
              ? 'Senior / Loved One'
              : 'Caregiver / Family Member'}
          </strong>
        </div>

        <a href="/" class="change-role">
          Change
        </a>

      </div>


      <!-- Heading -->

      <div class="heading">

        <p class="welcome">
          {mode === 'signin'
            ? 'WELCOME BACK'
            : 'WELCOME TO VCARE'}
        </p>

        <h2>
          {mode === 'signin'
            ? 'Good to see you again.'
            : 'Create your Vcare account.'}
        </h2>

        <p>
          {mode === 'signin'
            ? 'Sign in to continue to your care space.'
            : 'It only takes a moment to get started.'}
        </p>

      </div>

      <!-- Error Message -->
      {#if errorMessage}
        <div class="error-banner">
          <span class="error-icon">⚠️</span>
          <p>{errorMessage}</p>
        </div>
      {/if}

      <!-- Google -->

      <button
        type="button"
        class="google-button"
        onclick={continueWithGoogle}
        disabled={loading}
      >

        <span class="google-logo">
          G
        </span>

        <span>
          {loading ? 'Loading...' : 'Continue with Google'}
        </span>

      </button>


      <!-- Divider -->

      <div class="divider">
        <span></span>
        <p>or continue with email</p>
        <span></span>
      </div>


      <!-- Email -->

      <form onsubmit={(event) => {
        event.preventDefault();
        continueWithEmail();
      }}>

        <label for="email">
          Email address
        </label>

        <input
          id="email"
          type="email"
          bind:value={email}
          placeholder="you@example.com"
          autocomplete="email"
          disabled={loading}
        />


        <div class="password-label">

          <label for="password">
            Password
          </label>

          {#if mode === 'signin'}
            <button
              type="button"
              class="forgot"
            >
              Forgot password?
            </button>
          {/if}

        </div>


        <div class="password-input">

          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            bind:value={password}
            placeholder="Enter your password"
            autocomplete={
              mode === 'signin'
                ? 'current-password'
                : 'new-password'
            }
            disabled={loading}
          />

          <!-- Eye / eye-slash SVG — more universal than text "Show" -->
          <button
            type="button"
            class="show-password"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            onclick={() => {
              showPassword = !showPassword;
            }}
            disabled={loading}
          >
            {#if showPassword}
              <!-- eye-slash -->
              <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            {:else}
              <!-- eye -->
              <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            {/if}
          </button>

        </div>


        <button
          type="submit"
          class="primary-button"
          disabled={loading}
        >

          {loading 
            ? 'Loading...'
            : mode === 'signin'
            ? 'Sign in to Vcare'
            : 'Create my account'}

          {#if !loading}
            <span>→</span>
          {/if}

        </button>

      </form>


      <!-- Switch login/signup -->

      <div class="account-switch">

        {#if mode === 'signin'}

          <span>
            New to Vcare?
          </span>

          <button
            type="button"
            onclick={toggleMode}
            disabled={loading}
          >
            Create an account
          </button>

        {:else}

          <span>
            Already have an account?
          </span>

          <button
            type="button"
            onclick={toggleMode}
            disabled={loading}
          >
            Sign in instead
          </button>

        {/if}

      </div>


      <!-- Privacy -->

      <div class="privacy">

        <!-- Canonical SVG shield — standardized trust reassurance icon -->
        <div class="privacy-icon" aria-hidden="true">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="m9 12 2 2 4-4"/>
          </svg>
        </div>

        <div>
          <strong>
            Your information stays yours.
          </strong>

          <span>
            Vcare keeps your care information private and secure.
          </span>
        </div>

      </div>

    </div>

  </section>

</div>



<style>

  :global(*) {
    box-sizing: border-box;
  }


  :global(html) {
    margin: 0;
    padding: 0;
    width: 100%;
    min-height: 100%;
  }

  :global(button),
  :global(input) {
    font-family: inherit;
  }



  /* =====================================================
     PAGE
     ===================================================== */


  .auth-page {
    min-height: 100vh;

    display: grid;

    grid-template-columns:
      43% 57%;
  }



  /* =====================================================
     LEFT
     ===================================================== */


  .auth-story {
    position: relative;

    min-height: 100vh;

    padding:
      48px
      clamp(35px, 5vw, 72px);

    display: flex;

    flex-direction: column;

    overflow: hidden;

    color: white;

    /* Background is now the photo + warm overlay (see .story-photo / .story-overlay).
       Keep a fallback colour in case the image is slow to load. */
    background: #2a1806;
  }


  /* Photo layer — same image as landing page */
  .story-photo {
    position: absolute;

    inset: 0;

    width: 100%;
    height: 100%;

    object-fit: cover;
    object-position: 53% center;

    z-index: 0;
  }


  /* Warm amber/sepia overlay — exact same values as landing page */
  .story-overlay {
    position: absolute;

    inset: 0;

    z-index: 1;

    background:
      linear-gradient(
        90deg,
        rgba(48, 26, 8, 0.91) 0%,
        rgba(72, 40, 12, 0.65) 50%,
        rgba(90, 54, 18, 0.30) 100%
      ),
      linear-gradient(
        180deg,
        rgba(44, 24, 8, 0.42) 0%,
        transparent 48%,
        rgba(36, 20, 6, 0.82) 100%
      ),
      linear-gradient(
        135deg,
        rgba(200, 130, 40, 0.10) 0%,
        transparent 60%
      );
  }


  /* Removed .story-glow — the photo + overlay replaces it */



  /* brand */


  .brand {
    position: relative;

    /* Must sit above the photo overlay */
    z-index: 3;

    display: flex;

    align-items: center;

    gap: 12px;

    width: fit-content;

    color: white;

    text-decoration: none;
  }


  .brand-heart {
    width: 43px;
    height: 43px;

    display: grid;

    place-items: center;

    border-radius: 14px;

    background: white;

    color: #176348;

    font-size: 22px;
  }


  .brand > div:last-child {
    display: flex;

    flex-direction: column;
  }


  .brand strong {
    font-size: 21px;
  }


  .brand span {
    margin-top: 2px;

    font-size: 10px;

    color:
      rgba(255,255,255,0.70);
  }



  /* story */


  .story-content {
    position: relative;

    z-index: 3;

    max-width: 510px;

    margin:
      auto
      0;

    /* Ensure checklist and copy are legible above the photo layer */
    text-shadow: 0 1px 3px rgba(0,0,0,0.25);
  }


  .eyebrow {
    margin:
      0
      0
      18px;

    font-size: 10px;

    /* Medium weight — matches landing page eyebrow treatment */
    font-weight: 500;

    letter-spacing: 0.20em;

    color: #e0edbd;
  }


  .story-content h1 {
    margin: 0;

    /* Fraunces — matches landing page headlines */
    font-family:
      "Fraunces",
      Georgia,
      serif;

    font-size:
      clamp(48px, 4.8vw, 72px);

    line-height: 0.98;

    letter-spacing:
      -0.03em;

    font-weight: 500;
  }


  .story-content h1 span {
    display: block;

    margin-top: 8px;

    color: #e6efc0;
  }


  .story-content > p:not(.eyebrow) {
    max-width: 440px;

    margin:
      25px
      0
      0;

    font-size: 14px;

    line-height: 1.7;

    color:
      rgba(255,255,255,0.75);
  }



  /* story points */


  .story-points {
    margin-top: 32px;

    display: grid;

    gap: 12px;
  }


  .story-points div {
    display: flex;

    align-items: center;

    gap: 10px;

    font-size: 12px;

    /* Boosted from 0.82 → 0.95 for WCAG AA contrast over photo overlay */
    color:
      rgba(255,255,255,0.95);
  }


  .story-points span {
    width: 24px;
    height: 24px;

    display: grid;

    place-items: center;

    flex-shrink: 0;

    border-radius: 50%;

    /* Lighter fill + stronger checkmark color for ≥3:1 graphical contrast */
    background:
      rgba(224,239,188,0.22);

    color: #f0f9cf;

    font-size: 10px;
  }


  .story-footer {
    position: relative;

    z-index: 3;

    margin:
      35px
      0
      0;

    font-size: 10px;

    color:
      rgba(255,255,255,0.55);
  }



  /* =====================================================
     RIGHT PANEL
     ===================================================== */


  .auth-panel {
    position: relative;

    min-height: 100vh;

    display: flex;

    align-items: center;

    justify-content: center;

    padding:
      45px
      clamp(30px, 7vw, 105px);

    overflow: hidden;

    background:
      linear-gradient(
        145deg,
        #fffaf1 0%,
        #faf8ef 55%,
        #eef5e8 100%
      );
  }


  .panel-glow {
    position: absolute;

    width: 450px;
    height: 450px;

    right: -210px;
    top: -220px;

    border-radius: 50%;

    background:
      radial-gradient(
        circle,
        rgba(158,205,143,0.25),
        transparent 70%
      );
  }


  .auth-box {
    position: relative;

    z-index: 3;

    width: 100%;

    max-width: 510px;
  }



  /* =====================================================
     ROLE
     ===================================================== */


  .role-pill {
    min-height: 62px;

    padding:
      10px
      13px;

    display: grid;

    grid-template-columns:
      auto
      1fr
      auto;

    align-items: center;

    gap: 12px;

    /* Spacing group: context card is its own logical block */
    margin-bottom: 36px;

    border-radius: 16px;

    /* Flat white surface — same treatment as landing page role cards */
    background: #ffffff;

    border: 1px solid #e2e8e4;

    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  }


  .role-icon {
    width: 40px;
    height: 40px;

    display: grid;

    place-items: center;

    border-radius: 12px;

    background: white;

    font-size: 19px;

    color: #32765a;
  }


  .role-pill > div {
    display: flex;

    flex-direction: column;
  }


  .role-pill div span {
    font-size: 7px;

    font-weight: 800;

    letter-spacing: 0.14em;

    color: #719084;
  }


  .role-pill strong {
    margin-top: 3px;

    font-size: 12px;
  }


  .change-role {
    /* Styled as a secondary-button action — more visual weight than plain text */
    display: inline-flex;
    align-items: center;

    padding: 4px 10px;

    border-radius: 8px;

    background: rgba(78, 158, 114, 0.08);

    color: #2d7a52;

    font-size: 10px;
    font-weight: 700;

    text-decoration: none;

    border: 1px solid rgba(78, 158, 114, 0.22);

    transition: background 0.15s ease, border-color 0.15s ease;
  }


  .change-role:hover {
    background: rgba(78, 158, 114, 0.14);
    border-color: rgba(78, 158, 114, 0.40);
  }



  /* =====================================================
     HEADING
     ===================================================== */


  .welcome {
    margin:
      0
      0
      9px;

    font-size: 9px;

    /* Medium weight — consistent with landing-page eyebrow */
    font-weight: 500;

    letter-spacing: 0.20em;

    color: #458064;
  }


  .heading h2 {
    margin: 0;

    /* Fraunces — consistent with landing page h2 */
    font-family:
      "Fraunces",
      Georgia,
      serif;

    font-size:
      clamp(39px, 3.8vw, 52px);

    line-height: 1;

    font-weight: 500;

    letter-spacing:
      -0.03em;
  }


  .heading > p:last-child {
    /* Spacing group: extra gap before Google button */
    margin:
      13px
      0
      32px;

    font-size: 12px;

    color: #748179;
  }



  /* =====================================================
     GOOGLE
     ===================================================== */


  .google-button {
    width: 100%;
    height: 54px;

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 11px;

    /* Slightly heavier border + ambient shadow to read as primary fast-path,
       distinct from the input fields below */
    border:
      1.5px solid
      #c8d5cc;

    border-radius: 15px;

    background: white;

    color: #263f36;

    cursor: pointer;

    font-size: 13px;

    font-weight: 700;

    /* Resting shadow — gives the button lift vs the plain inputs */
    box-shadow: 0 2px 8px rgba(30,65,49,0.07);

    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;
  }


  .google-button:hover {
    transform:
      translateY(-2px);

    box-shadow:
      0 10px 25px
      rgba(30,65,49,0.12);
  }


  .google-logo {
    width: 28px;
    height: 28px;

    display: grid;

    place-items: center;

    border-radius: 50%;

    border:
      1px solid
      #e0e4df;

    font-weight: 800;

    color: #4285f4;
  }



  /* =====================================================
     DIVIDER
     ===================================================== */


  .divider {
    /* Spacing group: separate Google method from email method */
    margin:
      26px
      0;

    display: flex;

    align-items: center;

    gap: 11px;
  }


  .divider span {
    flex: 1;

    height: 1px;

    background: #dde2dc;
  }


  .divider p {
    margin: 0;

    font-size: 9px;

    color: #89948e;
  }



  /* =====================================================
     FORM
     ===================================================== */


  form {
    display: flex;

    flex-direction: column;
  }


  label {
    margin-bottom: 7px;

    font-size: 11px;

    font-weight: 700;

    color: #365247;
  }


  input {
    width: 100%;
    height: 52px;

    padding:
      0
      15px;

    border:
      1px solid
      #d9dfd9;

    border-radius: 14px;

    outline: none;

    background:
      rgba(255,255,255,0.92);

    font-size: 12px;

    color: #173d32;

    transition:
      border-color 0.18s ease,
      box-shadow 0.18s ease;
  }


  input:focus {
    border-color: #6c9f83;

    box-shadow:
      0 0 0 4px
      rgba(65,130,94,0.08);
  }


  #email {
    margin-bottom: 18px;
  }


  .password-label {
    display: flex;

    justify-content: space-between;

    align-items: center;
  }


  .forgot {
    padding: 0;

    border: 0;

    background: none;

    color: #3f7e61;

    font-size: 9px;

    font-weight: 700;

    cursor: pointer;
  }


  .password-input {
    position: relative;

    margin-bottom: 19px;
  }


  .password-input input {
    /* More room for the SVG eye icon (wider than text 'Show') */
    padding-right: 50px;
  }


  .show-password {
    position: absolute;

    right: 13px;

    top: 50%;

    transform:
      translateY(-50%);

    border: 0;

    background: transparent;

    /* Icon inherits the field's green accent */
    color: #51806a;

    line-height: 0;

    padding: 4px;

    cursor: pointer;

    transition: color 0.15s ease;
  }


  .show-password:hover {
    color: #2d7a52;
  }



  /* =====================================================
     PRIMARY
     ===================================================== */


  .primary-button {
    width: 100%;
    height: 55px;

    padding:
      0
      18px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    border: 0;

    border-radius: 15px;

    background:
      linear-gradient(
        120deg,
        #10503a,
        #19704f
      );

    color: white;

    cursor: pointer;

    font-size: 13px;

    font-weight: 750;

    box-shadow:
      0 14px 30px
      rgba(20,97,69,0.17);

    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;
  }


  .primary-button:hover {
    transform:
      translateY(-2px);

    box-shadow:
      0 18px 35px
      rgba(20,97,69,0.23);
  }


  .primary-button span {
    font-size: 18px;
  }



  /* =====================================================
     ACCOUNT SWITCH
     ===================================================== */


  .account-switch {
    /* Spacing group: separate from the submit button */
    margin-top: 26px;

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 6px;

    font-size: 10px;
  }


  .account-switch span {
    color: #849089;
  }


  .account-switch button {
    padding: 0;

    border: 0;

    background: transparent;

    color: #287253;

    font-size: 10px;

    font-weight: 800;

    cursor: pointer;
  }



  /* =====================================================
     PRIVACY
     ===================================================== */


  .privacy {
    /* Spacing group: trust box is its own visual block at the bottom */
    margin-top: 36px;

    padding:
      11px
      13px;

    display: flex;

    align-items: center;

    gap: 10px;

    border-radius: 14px;

    background:
      rgba(255,255,255,0.36);

    border:
      1px solid
      rgba(59,99,80,0.07);
  }


  .privacy-icon {
    width: 32px;
    height: 32px;

    display: grid;

    place-items: center;

    flex-shrink: 0;

    border-radius: 10px;

    background: #e5efdf;

    color: #34775a;

    font-size: 12px;
  }


  .privacy > div:last-child {
    display: flex;

    flex-direction: column;
  }


  .privacy strong {
    font-size: 9px;

    color: #425d52;
  }


  .privacy span {
    margin-top: 2px;

    font-size: 8px;

    color: #839089;
  }



  /* =====================================================
     TABLET
     ===================================================== */


  @media (max-width: 900px) {

    .auth-page {
      grid-template-columns: 1fr;
    }


    .auth-story {
      min-height: 520px;
    }


    .story-content {
      margin:
        90px
        0
        40px;
    }


    .auth-panel {
      min-height: 720px;

      padding:
        70px
        24px;
    }

  }



  /* =====================================================
     MOBILE
     ===================================================== */


  @media (max-width: 600px) {

    .auth-story {
      min-height: 420px;

      padding:
        27px
        21px;
    }


    .brand-heart {
      width: 38px;
      height: 38px;
    }


    .brand strong {
      font-size: 18px;
    }


    .story-content {
      margin:
        65px
        0
        30px;
    }


    .story-content h1 {
      font-size: 43px;
    }


    .story-content > p:not(.eyebrow) {
      font-size: 12px;
    }


    .story-points {
      display: none;
    }


    .story-footer {
      display: none;
    }


    .auth-panel {
      min-height: 700px;

      margin-top: -20px;

      padding:
        50px
        17px
        70px;

      z-index: 5;

      border-radius:
        27px 27px 0 0;
    }


    .auth-box {
      max-width: 480px;
    }


    .role-pill {
      margin-bottom: 27px;
    }


    .heading h2 {
      font-size: 39px;
    }


    .google-button {
      height: 53px;
    }

  }

</style>
