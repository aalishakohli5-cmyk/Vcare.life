<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { supabase } from '$lib/supabase';

  let fullName = $state('');
  let email = $state('');
  let dateOfBirth = $state('');
  let phone = $state('');
  let countryCode = $state('+91');
  let countrySearch = $state('');
let countryDropdownOpen = $state(false);

let filteredCountries = $derived(
    countryCodes.filter((item) =>
        item.country.toLowerCase().includes(countrySearch.toLowerCase()) ||
        item.code.includes(countrySearch)
    )
);

function selectCountry(item) {
    countryCode = item.code;
    countrySearch = '';
    countryDropdownOpen = false;
}

const countryCodes = [
    { country: 'India', flag: '🇮🇳', code: '+91' },
    { country: 'United States', flag: '🇺🇸', code: '+1' },
    { country: 'United Kingdom', flag: '🇬🇧', code: '+44' },
    { country: 'Canada', flag: '🇨🇦', code: '+1' },
    { country: 'Australia', flag: '🇦🇺', code: '+61' },
    { country: 'UAE', flag: '🇦🇪', code: '+971' },
    { country: 'Singapore', flag: '🇸🇬', code: '+65' },
    { country: 'Germany', flag: '🇩🇪', code: '+49' },
    { country: 'France', flag: '🇫🇷', code: '+33' },
    { country: 'Japan', flag: '🇯🇵', code: '+81' },
    { country: 'South Korea', flag: '🇰🇷', code: '+82' },
    { country: 'China', flag: '🇨🇳', code: '+86' },
    { country: 'New Zealand', flag: '🇳🇿', code: '+64' },
    { country: 'Italy', flag: '🇮🇹', code: '+39' },
    { country: 'Spain', flag: '🇪🇸', code: '+34' },
    { country: 'Netherlands', flag: '🇳🇱', code: '+31' },
    { country: 'Switzerland', flag: '🇨🇭', code: '+41' },
    { country: 'Saudi Arabia', flag: '🇸🇦', code: '+966' },
    { country: 'Qatar', flag: '🇶🇦', code: '+974' },
    { country: 'Malaysia', flag: '🇲🇾', code: '+60' }
];

  let gender = $state('');
  let language = $state('English');

  let emergencyName = $state('');
  let emergencyRelationship = $state('');
  let emergencyPhone = $state('');
  

  let step = $state(1);
  let loading = $state(true);
  let saving = $state(false);
  let errorMessage = $state('');

  let phoneDropped = $state(false);

  onMount(async () => {
    const {
      data: { user }
    } = await supabase.auth.getUser();

    if (!user) {
      goto('/auth?role=senior');
      return;
    }

    email = user.email ?? '';

    fullName =
      user.user_metadata?.full_name ??
      user.user_metadata?.name ??
      '';

    loading = false;
  });

  function togglePhone() {
    phoneDropped = !phoneDropped;
  }

  function nextStep() {
    errorMessage = '';

    if (step === 1) {
      if (!fullName.trim()) {
        errorMessage = 'Please enter your name.';
        return;
      }

      if (!dateOfBirth) {
        errorMessage = 'Please enter your date of birth.';
        return;
      }

      if (!phone.trim()) {
        errorMessage = 'Please enter your phone number.';
        return;
      }
    }

    if (step < 3) {
      step += 1;
    }
  }

  function previousStep() {
    errorMessage = '';

    if (step > 1) {
      step -= 1;
    }
  }

  async function finishSetup() {
    errorMessage = '';

    if (!emergencyName.trim()) {
      errorMessage = 'Please add someone from your support circle.';
      return;
    }

    if (!emergencyPhone.trim()) {
      errorMessage = 'Please enter their phone number.';
      return;
    }

    saving = true;

    const {
      data: { user },
      error: userError
    } = await supabase.auth.getUser();

    if (userError || !user) {
      saving = false;
      errorMessage = 'Your session expired. Please sign in again.';
      return;
    }

    const { error } = await supabase
      .from('profiles')
      .upsert({
        id: user.id,
        role: 'senior',
        full_name: fullName.trim(),
        email: user.email,
        date_of_birth: dateOfBirth,
        phone: phone.trim(),
        gender: gender || null,
        preferred_language: language,
        emergency_contact_name: emergencyName.trim(),
        emergency_contact_relationship:
          emergencyRelationship.trim() || null,
        emergency_contact_phone: emergencyPhone.trim(),
        onboarding_complete: true,
        updated_at: new Date().toISOString()
      });

    if (error) {
      console.error(error);

      saving = false;
      errorMessage =
        'Your profile could not be saved yet. Please try again.';

      return;
    }

    goto('/senior/dashboard');
  }
</script>

<svelte:head>
  <title>Set up your Vcare profile — Vcare.life</title>
</svelte:head>

{#if loading}

  <div class="loading-screen">
    <div class="loading-heart">♥</div>
    <h2>Getting Vcare ready...</h2>
  </div>

{:else}

  <main class="onboarding">

    <!-- =====================================================
         LEFT PANEL
         ===================================================== -->

    <aside class="left-panel">

      <!-- doodles -->

      <span class="doodle doodle-one">♡</span>
      <span class="doodle doodle-two">✦</span>
      <span class="doodle doodle-three">⌁</span>
      
      <span class="doodle doodle-five">~</span>


      <!-- logo -->

      <a href="/" class="brand">

        <div class="brand-heart">
          ♥
        </div>

        <div>
          <strong>Vcare.life</strong>
          <span>A Voice That Cares</span>
        </div>

      </a>


      <!-- PHONE -->

      <button
        type="button"
        class="phone-area"
        class:dropped={phoneDropped}
        onclick={togglePhone}
        aria-label="Play with Vcare phone"
      >

        <div class="cord">

          <div class="cord-line"></div>

          <div class="cord-curl curl-one"></div>
          <div class="cord-curl curl-two"></div>
          <div class="cord-curl curl-three"></div>

        </div>


        <div class="hook">
          ●
        </div>


        <div class="retro-phone">

          <div class="speaker">

            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>

          </div>


          <div class="phone-screen">

            <small>
              VCARE CALLING
            </small>

            <strong>
              {phoneDropped ? 'Pick me up!' : 'Hello there'}
            </strong>

            <span>
              ♡
            </span>

          </div>


          <div class="phone-buttons">

            <div class="call">
              ☎
            </div>

            <div class="circle-control">

              <span>‹</span>

              <b>●</b>

              <span>›</span>

            </div>

            <div class="hang">
              ×
            </div>

          </div>


          <div class="numbers">

            <span>1</span>
            <span>2</span>
            <span>3</span>

            <span>4</span>
            <span>5</span>
            <span>6</span>

            <span>7</span>
            <span>8</span>
            <span>9</span>

            <span>*</span>
            <span>0</span>
            <span>#</span>

          </div>

        </div>

      </button>


      <div class="tap-phone">
        <span>↖</span>
        <strong>Tap me!</strong>
        <small>I love it ♡</small>
      </div>


      <!-- LEFT TEXT -->

      <div class="left-content">

        <p class="left-eyebrow">
          YOUR CARE, YOUR WAY
        </p>

        <h1>
          Let's make
          <br />

          Vcare
          <br />

          <span>
            feel like yours!
          </span>
        </h1>


        <p class="left-description">
          Just a few little details help
          Vcare remember what matters to you.
        </p>


        <!-- steps -->

        <div class="side-steps">

          <div
            class:active={step === 1}
            class:complete={step > 1}
          >

            <span>
              {step > 1 ? '✓' : '1'}
            </span>

            <div>
              <strong>About you</strong>
              <p>Your basic information</p>
            </div>

          </div>


          <div
            class:active={step === 2}
            class:complete={step > 2}
          >

            <span>
              {step > 2 ? '✓' : '2'}
            </span>

            <div>
              <strong>Your preferences</strong>
              <p>Make Vcare comfortable for you</p>
            </div>

          </div>


          <div
            class:active={step === 3}
          >

            <span>
              3
            </span>

            <div>
              <strong>Your support circle</strong>
              <p>Someone Vcare should keep close</p>
            </div>

          </div>

        </div>

      </div>


     
    </aside>



    <!-- =====================================================
         RIGHT PANEL
         ===================================================== -->

    <section class="right-panel">

      <div class="form-card">

        <!-- top -->

        <header class="topbar">

          <div>

            <p>
              STEP {step} OF 3
            </p>

            <div class="progress">

              <span class:filled={step >= 1}></span>
              <span class:filled={step >= 2}></span>
              <span class:filled={step >= 3}></span>

            </div>

          </div>


          <div class="secure-pill">
            🛡 Private & secure
          </div>

        </header>


        <!-- =================================================
             STEP 1
             ================================================= -->

        {#if step === 1}

          <section class="form-section">

            <p class="welcome">
              WELCOME TO VCARE
            </p>

            <h2>
              Tell us a little
              <span>about you.</span>
            </h2>

            <p class="subtitle">
              We'll use this to personalise your reminders,
              check-ins and everyday Vcare experience.
            </p>


            <div class="fields">

              <div class="field full">

                <label for="name">
                  Full name
                </label>

                <div class="input-shell">

                  <input
                    id="name"
                    type="text"
                    bind:value={fullName}
                    placeholder="What should Vcare call you?"
                  />

                  <span class="input-icon">
                    ☺
                  </span>

                </div>

              </div>


              <div class="field full">

                <label for="email">
                  Email
                </label>

                <input
                  id="email"
                  type="email"
                  value={email}
                  disabled
                />

                <small class="connected">
                  ✓ Connected through your Google account
                </small>

              </div>


              <div class="field">

                <label for="dob">
                  Date of birth
                </label>

                <input
                  id="dob"
                  type="date"
                  bind:value={dateOfBirth}
                />

              </div>


              <div class="field">

                <label for="phone">
                  Phone number
                </label>

               <div class="phone-input">

  <div class="country-picker">

    <button
        type="button"
        class="country-trigger"
        onclick={() => countryDropdownOpen = !countryDropdownOpen}
    >
        <span>
            {countryCodes.find((c) => c.code === countryCode)?.flag}
        </span>

        <span>{countryCode}</span>

        <span class="chevron">⌄</span>
    </button>

    {#if countryDropdownOpen}
        <div class="country-menu">

            <input
                class="country-search"
                type="text"
                placeholder="Search country..."
                bind:value={countrySearch}
            />

            <div class="country-list">
                {#each filteredCountries as item}
                    <button
                        type="button"
                        class="country-option"
                        onclick={() => selectCountry(item)}
                    >
                        <span>{item.flag}</span>
                        <span>{item.code}</span>
                        <span class="country-name">{item.country}</span>
                    </button>
                {/each}

                {#if filteredCountries.length === 0}
                    <div class="no-country">
                        No country found
                    </div>
                {/if}
            </div>

        </div>
    {/if}

</div>


    <input
        id="phone"
        type="tel"
        bind:value={phone}
        placeholder="Phone number"
        inputmode="tel"
    />

</div>


              </div>


              <div class="field full">

                <label for="gender">
                  Gender

                  <span class="optional">
                    optional
                  </span>
                </label>

                <select
                  id="gender"
                  bind:value={gender}
                >

                  <option value="">
                    Prefer not to say
                  </option>

                  <option value="female">
                    Female
                  </option>

                  <option value="male">
                    Male
                  </option>

                  <option value="other">
                    Other
                  </option>

                </select>

              </div>

            </div>

          </section>

        {/if}



        <!-- =================================================
             STEP 2
             ================================================= -->

        {#if step === 2}

          <section class="form-section">

            <p class="welcome">
              YOUR PREFERENCES
            </p>

            <h2>
              Make Vcare
              <span>feel comfortable.</span>
            </h2>

            <p class="subtitle">
              Choose how you would like Vcare to talk,
              remind and check in with you.
            </p>


            <div class="fields">

              <div class="field full">

                <label for="language">
                  Preferred language
                </label>

                <select
                  id="language"
                  bind:value={language}
                >

                  <option>English</option>
                  <option>Hindi</option>
                  <option>Hinglish</option>
                  <option>Punjabi</option>
                  <option>Gujarati</option>
                  <option>Marathi</option>
                  <option>Bengali</option>
                  <option>Tamil</option>
                  <option>Telugu</option>

                </select>

              </div>


            


              <div class="message-card">

                <div>
                  ☺
                </div>

                <section>

                  <strong>
                    Nothing is permanent.
                  </strong>

                  <p>
                    You can change medicines, appointment reminders
                    and check-in times whenever you want.
                  </p>

                </section>

              </div>

            </div>

          </section>

        {/if}



        <!-- =================================================
             STEP 3
             ================================================= -->

        {#if step === 3}

          <section class="form-section">

            <p class="welcome">
              YOUR SUPPORT CIRCLE
            </p>

            <h2>
              Who should we
              <span>keep close?</span>
            </h2>

            <p class="subtitle">
              Add someone you trust — a child, sibling,
              partner or caregiver.
            </p>


            <div class="fields">

              <div class="field full">

                <label for="emergencyName">
                  Their name
                </label>

                <input
                  id="emergencyName"
                  type="text"
                  bind:value={emergencyName}
                  placeholder="e.g. Priya"
                />

              </div>


              <div class="field">

                <label for="relationship">
                  Relationship
                </label>

                <input
                  id="relationship"
                  type="text"
                  bind:value={emergencyRelationship}
                  placeholder="e.g. Daughter"
                />

              </div>


              <div class="field">

                <label for="emergencyPhone">
                  Phone number
                </label>

                <input
                  id="emergencyPhone"
                  type="tel"
                  bind:value={emergencyPhone}
                  placeholder="+91"
                />

              </div>


              <div class="message-card ready">

                <div>
                  ♥
                </div>

                <section>

                  <strong>
                    You're ready!
                  </strong>

                  <p>
                    Your personal Vcare space is almost ready.
                  </p>

                </section>

              </div>

            </div>

          </section>

        {/if}



        <!-- error -->

        {#if errorMessage}

          <div class="error-message">
            ⚠ {errorMessage}
          </div>

        {/if}



        <!-- buttons -->

        <footer class="actions">

          {#if step > 1}

            <button
              class="back-button"
              type="button"
              onclick={previousStep}
            >
              ← Back
            </button>

          {:else}

            <span></span>

          {/if}


          {#if step < 3}

            <button
              class="continue-button"
              type="button"
              onclick={nextStep}
            >

              Continue

              <span>
                →
              </span>

            </button>

          {:else}

            <button
              class="continue-button"
              type="button"
              onclick={finishSetup}
              disabled={saving}
            >

              {saving
                ? 'Preparing Vcare...'
                : 'Enter my Vcare'}

              <span>
                →
              </span>

            </button>

          {/if}

        </footer>


        <p class="privacy-note">
          🔒 Your information stays yours.
        </p>

      </div>

    </section>

  </main>

{/if}



<style>

  /* =====================================================
     GLOBAL
     ===================================================== */

  :global(*) {
    box-sizing: border-box;
  }

  :global(html),
  :global(body) {
    margin: 0;

    width: 100%;
    min-height: 100%;
  }

  :global(body) {
    font-family:
      "Comic Sans MS",
      "Comic Sans",
      "Chalkboard SE",
      "Marker Felt",
      cursive;

    background: #F9F0E0;

    color: #153d30;
  }

  button,
  input,
  select {
    font-family:
      "Comic Sans MS",
      "Comic Sans",
      "Chalkboard SE",
      "Marker Felt",
      cursive;
  }



  /* =====================================================
     LOADING
     ===================================================== */

  .loading-screen {
    min-height: 100vh;

    display: flex;

    flex-direction: column;

    justify-content: center;
    align-items: center;

    gap: 15px;

    background: #F9F0E0;

    color: #176146;
  }

  .loading-heart {
    font-size: 58px;

    animation: beat 1.2s ease-in-out infinite;
  }

  @keyframes beat {

    50% {
      transform: scale(1.18);
    }

  }



  /* =====================================================
     MAIN
     ===================================================== */

  .onboarding {
    min-height: 100vh;

    display: grid;

    grid-template-columns:
      minmax(470px, 42%)
      1fr;

    background: #F9F0E0;
  }



  /* =====================================================
     LEFT PANEL
     ===================================================== */

  .left-panel {
    position: relative;

    min-height: 100vh;

    padding:
      38px
      40px
      30px;

    overflow: visible;

    color: #ffffff;

    background:
      radial-gradient(
        circle at 20% 82%,
        rgba(173, 222, 92, 0.14),
        transparent 30%
      ),

      linear-gradient(
        145deg,
        #083c2a 0%,
        #075136 40%,
        #086c45 100%
      );
  }



  /* CURVED RIGHT EDGE */

  .left-panel::after {
    content: "";

    position: absolute;

    z-index: 20;

    top: -3%;

    right: -31px;

    width: 65px;
    height: 106%;

    border-radius: 50%;

    background: #F9F0E0;

    pointer-events: none;
  }



  /* =====================================================
     DOODLES
     ===================================================== */

  .doodle {
    position: absolute;

    color: rgba(210, 230, 80, 0.34);

    pointer-events: none;

    font-weight: bold;
  }

  .doodle-one {
    left: 53%;
    top: 13%;

    font-size: 40px;

    transform: rotate(-14deg);
  }

  .doodle-two {
    left: 68%;
    top: 75%;

    font-size: 35px;

    transform: rotate(20deg);
  }

  .doodle-three {
    left: 40%;
    top: 51%;

    font-size: 35px;
  }

 
  .doodle-five {
    left: 87%;
    top: 20%;

    font-size: 36px;
  }



  /* =====================================================
     BRAND
     ===================================================== */

  .brand {
    position: relative;

    z-index: 30;

    display: flex;

    align-items: center;

    gap: 12px;

    width: fit-content;

    color: white;

    text-decoration: none;
  }

  .brand-heart {
    width: 52px;
    height: 52px;

    display: grid;

    place-items: center;

    border-radius: 15px;

    background: #ffffff;

    color: #0b6142;

    font-size: 27px;
  }

  .brand > div:last-child {
    display: flex;

    flex-direction: column;
  }

  .brand strong {
    font-size: 26px;

    line-height: 1;
  }

  .brand span {
    margin-top: 4px;

    font-size: 12px;

    color: rgba(255,255,255,0.82);
  }



  /* =====================================================
     PHONE
     ===================================================== */

  .phone-area {
    position: absolute;

    z-index: 12;

    top: -5px;
    right: 70px;

    width: 230px;
    height: 565px;

    padding: 0;

    border: 0;

    outline: 0;

    background: transparent;

    cursor: pointer;

    transform-origin: top center;

    animation:
      swing 4s ease-in-out infinite;
  }


  @keyframes swing {

    0%,
    100% {
      transform: rotate(-2deg);
    }

    50% {
      transform: rotate(2deg);
    }

  }


  .phone-area.dropped {
    animation:
      dropPhone 0.85s
      cubic-bezier(.2,.8,.2,1)
      forwards;
  }


  @keyframes dropPhone {

    0% {
      transform:
        translateY(0)
        rotate(0deg);
    }

    35% {
      transform:
        translateY(115px)
        rotate(9deg);
    }

    70% {
      transform:
        translateY(175px)
        rotate(-6deg);
    }

    100% {
      transform:
        translateY(145px)
        rotate(3deg);
    }

  }



  /* cord */

  .cord {
    position: absolute;

    left: 50%;
    top: 0;

    width: 34px;
    height: 125px;

    transform: translateX(-50%);
  }

  .cord-line {
    position: absolute;

    left: 50%;
    top: 0;

    width: 5px;
    height: 58px;

    transform: translateX(-50%);

    border-radius: 20px;

    background: #c9da47;
  }


  .cord-curl {
    position: absolute;

    left: 50%;

    width: 22px;
    height: 22px;

    transform: translateX(-50%);

    border:
      4px solid #c9da47;

    border-left-color: transparent;

    border-radius: 50%;
  }

  .curl-one {
    top: 48px;
  }

  .curl-two {
    top: 65px;

    transform:
      translateX(-50%)
      rotate(180deg);
  }

  .curl-three {
    top: 82px;
  }


  .hook {
    position: absolute;

    z-index: 5;

    top: 103px;
    left: 50%;

    transform:
      translateX(-50%);

    width: 31px;
    height: 31px;

    display: grid;

    place-items: center;

    border-radius: 50%;

    border:
      5px solid #31572d;

    background: #c9d946;

    color: #44652f;

    font-size: 8px;

    box-shadow:
      0 5px 10px
      rgba(0,0,0,0.2);
  }



  /* phone body */

  .retro-phone {
    position: absolute;

    top: 125px;
    left: 50%;

    transform:
      translateX(-50%);

    width: 185px;

    padding:
      18px
      15px
      20px;

    border:
      6px solid
      #405f24;

    border-radius:
      42px
      42px
      34px
      34px;

    background:
      linear-gradient(
        145deg,
        #c0d93d,
        #8fb72e 55%,
        #72982b
      );

    box-shadow:
      0 22px 35px
      rgba(0, 36, 22, 0.42),
      inset 3px 3px 5px
      rgba(255,255,255,0.2);
  }



  /* speaker */

  .speaker {
    width: 120px;
    height: 27px;

    margin:
      0
      auto
      12px;

    display: flex;

    align-items: center;
    justify-content: center;

    gap: 6px;

    border-radius: 15px;

    background: #4c6829;
  }

  .speaker span {
    width: 4px;
    height: 4px;

    border-radius: 50%;

    background: #cfe173;
  }



  /* phone screen */

  .phone-screen {
    height: 112px;

    padding:
      12px
      8px;

    display: flex;

    flex-direction: column;

    justify-content: center;
    align-items: center;

    border:
      6px solid
      #254c2a;

    border-radius: 19px;

    background:
      linear-gradient(
        145deg,
        #f0f844,
        #d7ee3b
      );

    color: #173b25;

    box-shadow:
      inset
      0 0 20px
      rgba(97, 112, 17, 0.15);
  }

  .phone-screen small {
    font-size: 10px;

    font-weight: bold;
  }

  .phone-screen strong {
    margin-top: 8px;

    font-size: 19px;
  }

  .phone-screen > span {
    margin-top: 4px;

    font-size: 22px;
  }



  /* phone controls */

  .phone-buttons {
    margin:
      13px
      0
      11px;

    display: flex;

    align-items: center;
    justify-content: space-around;
  }

  .call,
  .hang {
    width: 38px;
    height: 28px;

    display: grid;

    place-items: center;

    border-radius: 20px;

    color: white;

    font-size: 14px;

    font-weight: bold;
  }

  .call {
    background: #24824a;
  }

  .hang {
    background: #f25a35;
  }


  .circle-control {
    width: 53px;
    height: 53px;

    display: flex;

    align-items: center;
    justify-content: space-around;

    border-radius: 50%;

    background: #f5f1cf;

    color: #355634;

    box-shadow:
      0 2px 3px
      rgba(0,0,0,0.2);
  }

  .circle-control b {
    width: 17px;
    height: 17px;

    display: grid;

    place-items: center;

    border-radius: 50%;

    background: white;

    font-size: 6px;
  }



  /* number buttons */

  .numbers {
    display: grid;

    grid-template-columns:
      repeat(3, 1fr);

    gap: 6px;
  }

  .numbers span {
    height: 25px;

    display: grid;

    place-items: center;

    border-radius: 9px;

    background: #f8f2c9;

    color: #203f2d;

    font-size: 12px;

    font-weight: bold;

    box-shadow:
      0 2px 3px
      rgba(31,59,32,0.2);
  }



  /* tap text */

  .tap-phone {
    position: absolute;

    z-index: 15;

    top: 560px;
    right: 53px;

    display: flex;

    flex-direction: column;

    color: white;

    transform:
      rotate(-3deg);
  }

  .tap-phone > span {
    position: absolute;

    left: -30px;
    top: -28px;

    font-size: 36px;
  }

  .tap-phone strong {
    font-size: 22px;
  }

  .tap-phone small {
    margin-top: 3px;

    font-size: 13px;

    color: #dce866;
  }



  /* =====================================================
     LEFT CONTENT
     ===================================================== */

  .left-content {
    position: relative;

    z-index: 8;

    width: 64%;

    margin-top: 135px;
  }


  .left-eyebrow {
    margin:
      0
      0
      20px;

    color: #dce95b;

    font-size: 15px;

    font-weight: bold;

    letter-spacing: 0.06em;
  }


  .left-content h1 {
    margin: 0;

    color: white;

    font-size:
      clamp(52px, 4.5vw, 75px);

    line-height: 1.02;

    letter-spacing: -0.04em;

    font-weight: bold;
  }


  .left-content h1 span {
    color: #d8e95b;
  }


  .left-description {
    max-width: 355px;

    margin:
      28px
      0
      28px;

    color: rgba(255,255,255,0.95);

    font-size: 17px;

    line-height: 1.6;
  }



  /* =====================================================
     STEPS LEFT
     ===================================================== */

  .side-steps {
    display: grid;

    gap: 11px;
  }


  .side-steps > div {
    min-height: 67px;

    padding:
      10px
      13px;

    display: grid;

    grid-template-columns:
      48px 1fr;

    gap: 12px;

    align-items: center;

    border:
      1px solid
      rgba(255,255,255,0.13);

    border-radius: 17px;

    background:
      rgba(255,255,255,0.06);

    opacity: 0.68;

    transition:
      0.25s ease;
  }


  .side-steps > div.active {
    opacity: 1;

    transform:
      translateX(8px);

    background:
      rgba(255,255,255,0.15);

    border-color:
      rgba(223,235,95,0.33);
  }


  .side-steps > div.complete {
    opacity: 0.90;
  }


  .side-steps > div > span {
    width: 43px;
    height: 43px;

    display: grid;

    place-items: center;

    border-radius: 13px;

    background:
      rgba(202,218,68,0.28);

    color: #eff4b1;

    font-size: 16px;

    font-weight: bold;
  }


  .side-steps strong {
    display: block;

    color: white;

    font-size: 16px;
  }


  .side-steps p {
    margin:
      4px
      0
      0;

    color:
      rgba(255,255,255,0.72);

    font-size: 11px;
  }



  


  /* =====================================================
     RIGHT PANEL
     ===================================================== */

  .right-panel {
    min-height: 100vh;

    padding:
      32px
      clamp(35px, 5vw, 75px);

    display: flex;

    justify-content: center;
    align-items: center;

    background:
      radial-gradient(
        circle at 100% 0%,
        rgba(239,207,124,0.28),
        transparent 30%
      ),
      #F9F0E0;
  }



  /* =====================================================
     FORM CARD
     ===================================================== */

  .form-card {
    width: 100%;

    max-width: 760px;

    padding:
      34px
      42px
      28px;

    border:
      1px solid
      #ead9b7;

    border-radius: 34px;

    background:
      rgba(255, 248, 235, 0.65);

    box-shadow:
      0 24px 60px
      rgba(105,76,30,0.08);
  }



  /* =====================================================
     TOP
     ===================================================== */

  .topbar {
    display: flex;

    align-items: flex-start;
    justify-content: space-between;

    margin-bottom: 40px;
  }


  .topbar p {
    margin:
      0
      0
      9px;

    color: #176142;

    font-size: 15px;

    font-weight: bold;

    letter-spacing: 0.05em;
  }


  .progress {
    display: flex;

    gap: 8px;
  }


  .progress span {
    width: 64px;
    height: 6px;

    border-radius: 10px;

    background: #e5d4b4;
  }


  .progress span.filled {
    background: #176342;
  }


  .secure-pill {
    padding:
      10px
      17px;

    border-radius: 50px;

    background: #ecf0b2;

    color: #235f3c;

    font-size: 13px;

    font-weight: bold;
  }



  /* =====================================================
     FORM HEADING
     ===================================================== */

  .welcome {
    margin:
      0
      0
      10px;

    color: #176143;

    font-size: 15px;

    font-weight: bold;

    letter-spacing: 0.06em;
  }


  .form-section h2 {
    margin: 0;

    color: #124c37;

    font-size:
      clamp(48px, 4vw, 66px);

    line-height: 1.03;

    letter-spacing: -0.045em;
  }


  .form-section h2 span {
    color: #6c983f;
  }


  .subtitle {
    max-width: 640px;

    margin:
      18px
      0
      29px;

    color: #564b3e;

    font-size: 17px;

    line-height: 1.55;
  }



  /* =====================================================
     FIELDS
     ===================================================== */

  .fields {
    display: grid;

    grid-template-columns:
      1fr 1fr;

    gap:
      20px
      18px;
  }


  .field {
    display: flex;

    flex-direction: column;
  }


  .field.full {
    grid-column:
      1 / -1;
  }


  label {
    margin-bottom: 8px;

    color: #342c23;

    font-size: 16px;

    font-weight: bold;
  }


  .optional {
    margin-left: 5px;

    color: #739250;

    font-size: 11px;

    font-weight: normal;
  }


  input,
  select {
    width: 100%;

    height: 62px;

    padding:
      0
      17px;

    border:
      2px solid
      #decdb0;

    border-radius: 17px;

    outline: none;

    background:
      rgba(255,255,255,0.46);

    color: #322b25;

    font-size: 16px;

    transition:
      border-color 0.2s ease,
      box-shadow 0.2s ease,
      transform 0.2s ease;
  }


  input:hover,
  select:hover {
    border-color: #b8b47c;
  }


  input:focus,
  select:focus {
    border-color: #6e9b43;

    box-shadow:
      0 0 0 5px
      rgba(117,153,68,0.10);

    transform:
      translateY(-1px);
  }


  input:disabled {
    background:
      rgba(224,215,199,0.40);

    color: #716b63;
  }


  .input-shell {
    position: relative;
  }


  .input-shell input {
    padding-right: 55px;
  }


  .input-icon {
    position: absolute;

    right: 18px;
    top: 50%;

    transform:
      translateY(-50%);

    font-size: 21px;
  }


  .connected {
    margin-top: 7px;

    color: #668a39;

    font-size: 11px;

    font-weight: bold;
  }



  /* =====================================================
     MESSAGE CARDS
     ===================================================== */

  .message-card {
    grid-column:
      1 / -1;

    padding:
      16px;

    display: flex;

    gap: 14px;

    align-items: center;

    border:
      1px solid
      #d5dba2;

    border-radius: 17px;

    background: #f1f2c9;
  }


  .message-card.ready {
    background: #f8e9bc;

    border-color: #e4ce8d;
  }


  .message-card > div {
    width: 48px;
    height: 48px;

    display: grid;

    place-items: center;

    flex-shrink: 0;

    border-radius: 14px;

    background:
      rgba(255,255,255,0.65);

    color: #4b853e;

    font-size: 22px;
  }


  .message-card strong {
    font-size: 15px;

    color: #275841;
  }


  .message-card p {
    margin:
      4px
      0
      0;

    color: #645b4d;

    font-size: 12px;

    line-height: 1.5;
  }



  /* =====================================================
     ERROR
     ===================================================== */

  .error-message {
    margin-top: 20px;

    padding:
      12px
      15px;

    border-radius: 13px;

    background: #ffe1d4;

    color: #a34a35;

    font-size: 13px;
  }



  /* =====================================================
     BUTTONS
     ===================================================== */

  .actions {
    margin-top: 30px;

    display: flex;

    justify-content: space-between;
    align-items: center;

    gap: 14px;
  }


  .back-button {
    height: 57px;

    padding:
      0
      22px;

    border:
      2px solid
      #ddcba9;

    border-radius: 17px;

    background:
      rgba(255,255,255,0.4);

    color: #365b46;

    cursor: pointer;

    font-size: 15px;

    font-weight: bold;
  }


  .continue-button {
    min-width: 220px;

    height: 61px;

    padding:
      0
      22px;

    display: flex;

    align-items: center;
    justify-content: space-between;

    border: 0;

    border-radius: 17px;

    background:
      linear-gradient(
        120deg,
        #18683f,
        #168d4c
      );

    color: white;

    cursor: pointer;

    font-size: 18px;

    font-weight: bold;

    box-shadow:
      0 16px 30px
      rgba(15,103,56,0.21);

    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;
  }


  .continue-button:hover {
    transform:
      translateY(-3px)
      scale(1.01);

    box-shadow:
      0 21px 38px
      rgba(15,103,56,0.28);
  }


  .continue-button span {
    font-size: 27px;
  }


  .continue-button:disabled {
    opacity: 0.65;

    cursor: wait;
  }


  .privacy-note {
    margin:
      25px
      0
      0;

    text-align: center;

    color: #8d7148;

    font-size: 12px;
  }



  /* =====================================================
     TABLET
     ===================================================== */

  @media (max-width: 1000px) {

    .onboarding {
      grid-template-columns: 1fr;
    }


    .left-panel {
      min-height: 720px;
    }


    .left-panel::after {
      display: none;
    }


    .left-content {
      width: 57%;

      margin-top: 150px;
    }


    .phone-area {
      right: 65px;
    }


    .right-panel {
      min-height: auto;

      padding:
        60px
        25px;
    }

  }



  /* =====================================================
     MOBILE
     ===================================================== */

  @media (max-width: 650px) {

    .left-panel {
      min-height: 650px;

      padding:
        25px
        20px;
    }


    .brand-heart {
      width: 44px;
      height: 44px;

      font-size: 22px;
    }


    .brand strong {
      font-size: 21px;
    }


    .phone-area {
      top: -25px;
      right: -5px;

      transform:
        scale(0.72);

      transform-origin:
        top right;
    }


    .tap-phone {
      display: none;
    }


    .left-content {
      width: 72%;

      margin-top: 230px;
    }


    .left-content h1 {
      font-size: 46px;
    }


    .left-eyebrow {
      font-size: 12px;
    }


    .left-description {
      font-size: 14px;
    }


    .side-steps {
      display: none;
    }


    .right-panel {
      margin-top: -20px;

      position: relative;

      z-index: 30;

      padding:
        38px
        14px
        65px;

      border-radius:
        28px 28px 0 0;
    }


    .form-card {
      padding:
        26px
        19px;

      border-radius: 25px;
    }


    .form-section h2 {
      font-size: 43px;
    }


    .subtitle {
      font-size: 14px;
    }


    .fields {
      grid-template-columns: 1fr;
    }


    .field.full,
    .message-card {
      grid-column: auto;
    }


    input,
    select {
      height: 59px;

      font-size: 15px;
    }


    .secure-pill {
      font-size: 9px;
    }


    .continue-button {
      min-width: 175px;

      font-size: 15px;
    }

  }
/* ==============================
   COMPACT PHONE INPUT
   ============================== */

.phone-input {
    width: 100%;
    height: 62px;

    display: flex;
    align-items: center;

    border: 2px solid #decdb0;
    border-radius: 17px;

    background: rgba(255, 255, 255, 0.46);

    overflow: hidden;
    transition: 0.2s ease;
}

.phone-input:focus-within {
    border-color: #6e9b43;
    box-shadow: 0 0 0 5px rgba(117, 153, 68, 0.10);
}

/* LEFT SMALL COUNTRY PART */
.phone-input .country-code {
    width: 125px;
    height: 100%;

    flex-shrink: 0;

    padding: 0 10px;

    border: none;
    border-right: 2px solid #decdb0;
    border-radius: 0;

    background: rgba(235, 238, 207, 0.55);

    box-shadow: none;
    outline: none;

    font-family: "Comic Sans MS", "Comic Sans", "Chalkboard SE", cursive;
    font-size: 15px;
    font-weight: bold;

    color: #315b3d;
    cursor: pointer;
}

/* RIGHT PHONE NUMBER PART */
.phone-input input {
    flex: 1;
    width: auto;
    min-width: 0;
    height: 100%;

    padding: 0 15px;

    border: none;
    border-radius: 0;

    background: transparent;

    box-shadow: none;
    outline: none;

    font-family: "Comic Sans MS", "Comic Sans", "Chalkboard SE", cursive;
    font-size: 16px;

    color: #322b25;
}

/* STOP GLOBAL HOVER/FOCUS FROM MAKING
   THE TWO INNER FIELDS HUGE */
.phone-input .country-code:hover,
.phone-input .country-code:focus,
.phone-input input:hover,
.phone-input input:focus {
    border-top: none;
    border-bottom: none;
    border-left: none;

    box-shadow: none;
    transform: none;
}

.phone-input input:hover,
.phone-input input:focus {
    border-right: none;
}

.phone-input .country-code:hover,
.phone-input .country-code:focus {
    border-right: 2px solid #decdb0;
}
.country-picker {
    position: relative;
    flex-shrink: 0;
}

.country-trigger {
    height: 100%;
    min-height: 58px;
    padding: 0 16px;
    border: none;
    background: #f3eedb;
    color: #315c42;

    display: flex;
    align-items: center;
    gap: 8px;

    font-family: "Comic Sans MS", "Comic Sans", cursive;
    font-size: 18px;
    font-weight: bold;

    cursor: pointer;
}

.chevron {
    font-size: 18px;
    margin-left: 3px;
}

.country-menu {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;

    width: 280px;
    max-height: 330px;

    padding: 10px;

    background: #f9f0e0;
    border: 2px solid #65953f;
    border-radius: 18px;

    box-shadow: 0 12px 30px rgba(31, 70, 47, 0.2);

    z-index: 1000;
}

.country-search {
    width: 100%;
    height: 46px;

    padding: 0 14px;
    margin-bottom: 8px;

    border: 2px solid #d8c9a8;
    border-radius: 12px;

    background: #fffaf0;
    color: #342c23;

    font-family: "Comic Sans MS", "Comic Sans", cursive;
    font-size: 15px;

    outline: none;
    box-sizing: border-box;
}

.country-search:focus {
    border-color: #65953f;
}

.country-list {
    max-height: 250px;
    overflow-y: auto;
}

.country-option {
    width: 100%;
    padding: 10px 12px;

    border: none;
    border-radius: 10px;
    background: transparent;

    display: flex;
    align-items: center;
    gap: 10px;

    color: #342c23;
    font-family: "Comic Sans MS", "Comic Sans", cursive;
    font-size: 15px;

    cursor: pointer;
    text-align: left;
}

.country-option:hover {
    background: #e8edcf;
}

.country-name {
    opacity: 0.7;
    font-size: 13px;
}

.no-country {
    padding: 18px;
    text-align: center;
    color: #776f63;
    font-family: "Comic Sans MS", "Comic Sans", cursive;
}

.phone-input {
    position: relative;
    overflow: visible;
}

.country-picker {
    position: relative;
    height: 100%;
    flex-shrink: 0;
    z-index: 50;
}

.country-trigger {
    height: 100%;
    min-width: 95px;

    padding: 0 12px;

    border: none;
    border-right: 2px solid #decdb0;
    border-radius: 15px 0 0 15px;

    background: rgba(235, 238, 207, 0.65);

    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;

    color: #315b3d;

    font-family: "Comic Sans MS", "Comic Sans", cursive;
    font-size: 15px;
    font-weight: bold;

    cursor: pointer;
}

.country-menu {
    position: absolute;

    top: calc(100% + 8px);
    left: 0;

    width: 285px;
    max-height: 330px;

    padding: 10px;

    background: #F9F0E0;

    border: 2px solid #65953f;
    border-radius: 16px;

    box-shadow: 0 15px 35px rgba(28, 65, 43, 0.22);

    z-index: 9999;
}

.country-search {
    width: 100%;
    height: 44px;

    padding: 0 12px;
    margin-bottom: 8px;

    border: 2px solid #d8c9a8;
    border-radius: 11px;

    background: #fffaf1;

    font-size: 14px;

    box-shadow: none !important;
    transform: none !important;
}

.country-list {
    max-height: 240px;
    overflow-y: auto;
}

.country-option {
    width: 100%;

    padding: 9px 10px;

    border: none;
    border-radius: 9px;

    background: transparent;

    display: grid;
    grid-template-columns: 28px 48px 1fr;
    align-items: center;

    text-align: left;

    cursor: pointer;

    color: #342c23;
    font-family: "Comic Sans MS", "Comic Sans", cursive;
}

.country-option:hover {
    background: #e7ebcb;
}

.country-name {
    font-size: 13px;
    opacity: 0.75;
}

</style>
