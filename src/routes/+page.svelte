<svelte:head>
  <title>Vcare.life — A Voice That Cares</title>
  <meta
    name="description"
    content="Vcare.life is an AI voice companion for seniors and their families."
  />
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link
    href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..500&family=Public+Sans:wght@300..700&display=swap"
    rel="stylesheet"
  />
</svelte:head>

<div class="welcome-page">

  <!-- LEFT SIDE -->
  <section class="hero">

    <img
      src="/grandma.jpg"
      alt="Senior woman happily talking on the phone"
      class="hero-image"
      width="1536"
      height="1024"
      decoding="async"
      fetchpriority="high"
    />

    <div class="hero-overlay"></div>

    <div class="brand">
      <div class="logo-mark">♥</div>

      <div class="brand-copy">
        <strong>Vcare.life</strong>
        <span>A Voice That Cares</span>
      </div>
    </div>

    <div class="hero-copy">
      <p class="eyebrow">CARE THAT STAYS CLOSE</p>

      <h1>
        They cared for us.
        <span>Now we care for them.</span>
      </h1>

      <p>
        An AI voice companion for your loved ones —
        checking in, remembering the little things and
        keeping family close.
      </p>
    </div>

    <div class="benefits">

      <div class="benefit">
        <div class="benefit-icon">💊</div>
        <div>
          <strong>Medication</strong>
          <span>Smart reminders</span>
        </div>
      </div>

      <div class="benefit">
        <div class="benefit-icon">♡</div>
        <div>
          <strong>Wellness</strong>
          <span>Daily check-ins</span>
        </div>
      </div>

      <div class="benefit">
        <div class="benefit-icon">👥</div>
        <div>
          <strong>Family</strong>
          <span>Always informed</span>
        </div>
      </div>

    </div>

  </section>


  <!-- RIGHT SIDE -->
  <section class="role-section">

    <div class="soft-glow glow-one"></div>
    <div class="soft-glow glow-two"></div>

    <div class="role-content">

      <p class="welcome-label">WELCOME TO VCARE</p>

      <h2>
        Care begins with
        <span>staying connected.</span>
      </h2>

      <p class="intro">
        Whether you're caring for someone you love,
        or being cared for — you're in the right place.
      </p>

      <div class="choice-block">

        <p class="choice-title">
          How would you like to continue?
        </p>

        <p class="choice-subtitle">
          Choose the experience that feels right for you.
        </p>


        <!-- CAREGIVER -->
       <a href="/auth?role=caregiver" class="role-card caregiver">


          <div class="role-icon">
            👥
          </div>

          <div class="role-copy">
            <span class="role-main">
              I'm caring for someone
            </span>

            <strong>
              Caregiver / Family Member
            </strong>

            <p>
              Stay informed and support your loved one's care.
            </p>
          </div>

          <div class="arrow">
            →
          </div>

        </a>


        <!-- SENIOR -->
        <a href="/auth?role=senior" class="role-card senior">

          <div class="role-icon senior-heart">
            ♡
          </div>

          <div class="role-copy">
            <span class="role-main">
              I'm receiving care
            </span>

            <strong>
              Senior / Loved One
            </strong>

            <p>
              Your reminders, check-ins and daily support.
            </p>
          </div>

          <div class="arrow">
            →
          </div>

        </a>

      </div>


      <div class="privacy">
        <!-- Canonical SVG shield — standardized trust reassurance icon -->
        <div class="privacy-icon" aria-hidden="true">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="m9 12 2 2 4-4"/>
          </svg>
        </div>

        <div>
          <strong>Private &amp; secure</strong>
          <span>Your care information stays yours.</span>
        </div>
      </div>

    </div>


    <div class="footer">
      <span>♡</span>
      Because care should always feel close.
    </div>

  </section>

</div>


<style>
  /* PAGE */

  .welcome-page {
    min-height: 100vh;

    display: grid;

    grid-template-columns:
      52% 48%;

    overflow: hidden;
  }


  /* LEFT SIDE */

  .hero {
    position: relative;

    min-height: 100vh;

    padding:
      52px
      64px;

    display: flex;

    flex-direction: column;

    overflow: hidden;

    color: white;
  }


  .hero-image {
    position: absolute;

    inset: 0;

    width: 100%;
    height: 100%;

    object-fit: cover;

    object-position:
      53% center;

    z-index: 0;
  }


  .hero-overlay {
    position: absolute;

    inset: 0;

    z-index: 1;

    /* Warm amber/sepia duotone — reads "cozy home" not corporate-dark.
       Dark-channel: warm brown-sepia instead of cold green-black.
       Highlight-channel: soft amber blush blended in. */
    background:
      linear-gradient(
        90deg,
        rgba(48, 26, 8, 0.87) 0%,
        rgba(72, 40, 12, 0.52) 45%,
        rgba(90, 54, 18, 0.18) 82%
      ),
      linear-gradient(
        180deg,
        rgba(44, 24, 8, 0.40) 0%,
        transparent 48%,
        rgba(36, 20, 6, 0.80) 100%
      ),
      linear-gradient(
        135deg,
        rgba(200, 130, 40, 0.12) 0%,
        transparent 60%
      );
  }


  /* LOGO */

  .brand {
    position: relative;

    z-index: 3;

    display: flex;

    align-items: center;

    gap: 12px;
  }


  .logo-mark {
    width: 44px;
    height: 44px;

    display: grid;

    place-items: center;

    border-radius: 14px;

    background:
      rgba(255, 255, 255, 0.94);

    color: #176348;

    font-size: 22px;
  }


  .brand-copy {
    display: flex;

    flex-direction: column;
  }


  .brand-copy strong {
    font-size: 22px;
  }


  .brand-copy span {
    margin-top: 2px;

    font-size: 11px;

    color:
      rgba(255, 255, 255, 0.72);
  }


  /* HERO COPY */

  .hero-copy {
    position: relative;

    z-index: 3;

    max-width: 610px;

    margin:
      auto 0;
  }


  .eyebrow {
    margin-bottom: 18px;

    font-size: 11px;

    /* Dropped to medium — eyebrow labels should whisper, not shout */
    font-weight: 500;

    letter-spacing: 0.20em;

    color: #e0edbd;
  }


  h1 {
    margin: 0;

    max-width: 610px;

    /* Fraunces — warmer, softer display serif */
    font-family:
      "Fraunces",
      Georgia,
      serif;

    font-size:
      clamp(48px, 4.4vw, 70px);

    line-height: 0.98;

    letter-spacing:
      -0.03em;

    font-weight: 500;
  }


  h1 span {
    display: block;

    margin-top: 7px;

    color: #e7efc1;
  }


  .hero-copy > p {
    max-width: 490px;

    margin-top: 27px;

    font-size: 16px;

    line-height: 1.7;

    color:
      rgba(255, 255, 255, 0.84);
  }


  /* BENEFITS */

  .benefits {
    position: relative;

    z-index: 3;

    display: grid;

    grid-template-columns:
      repeat(3, 1fr);

    gap: 12px;
  }


  .benefit {
    min-height: 82px;

    padding: 15px;

    display: flex;

    align-items: center;

    gap: 10px;

    border-radius: 17px;

    background:
      rgba(251, 246, 224, 0.82);

    backdrop-filter:
      blur(16px);

    border:
      1px solid
      rgba(255, 255, 255, 0.32);

    color: #173b31;

    box-shadow:
      0 15px 35px
      rgba(3, 31, 22, 0.14);

    transition:
      transform 0.22s ease,
      box-shadow 0.22s ease;
  }


  .benefit:hover {
    transform:
      translateY(-4px);

    box-shadow:
      0 20px 42px
      rgba(3, 31, 22, 0.20);
  }


  /* Standardised chip — one neutral background, icon color carries the
     category distinction (Medication: green, Wellness: rose, Family: teal) */
  .benefit-icon {
    width: 36px;
    height: 36px;

    display: grid;

    place-items: center;

    border-radius: 11px;

    /* Uniform warm-white glass chip for all three */
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.45);

    font-size: 20px;
  }

  /* Medication — green tint */
  .benefit:nth-child(1) .benefit-icon { color: #2d7a52; }
  /* Wellness — warm rose */
  .benefit:nth-child(2) .benefit-icon { color: #c0595e; }
  /* Family — teal */
  .benefit:nth-child(3) .benefit-icon { color: #2a6e82; }


  .benefit strong {
    display: block;

    font-size: 12px;
  }


  .benefit span {
    display: block;

    margin-top: 3px;

    font-size: 10px;

    color: #66766f;
  }


  /* RIGHT SIDE */

  .role-section {
    position: relative;

    min-height: 100vh;

    display: flex;

    align-items: center;

    justify-content: center;

    padding:
      60px
      clamp(48px, 6vw, 100px);

    overflow: hidden;

    background:
      linear-gradient(
        145deg,
        #fffaf0 0%,
        #faf7ed 55%,
        #eef5e9 100%
      );
  }


  /* soft decorations ONLY on right */

  .soft-glow {
    position: absolute;

    border-radius: 50%;

    pointer-events: none;

    filter: blur(3px);
  }


  .glow-one {
    width: 450px;
    height: 450px;

    top: -230px;
    right: -220px;

    background:
      radial-gradient(
        circle,
        rgba(158, 205, 143, 0.30),
        transparent 70%
      );
  }


  .glow-two {
    width: 350px;
    height: 350px;

    bottom: -220px;
    left: -180px;

    background:
      radial-gradient(
        circle,
        rgba(238, 202, 129, 0.16),
        transparent 70%
      );
  }

.role-content {
  position: relative;
  z-index: 3;
  width: 100%;
  max-width: 760px;
}


  .welcome-label {
    margin:
      0
      0
      12px;

    text-align: center;

    font-size: 13px;

    /* Medium weight — eyebrow, not headline */
    font-weight: 500;

    letter-spacing: 0.20em;

    color: #3b795e;
  }

h2 {
  margin: 0;
  text-align: center;

  /* Fraunces for hero headline on right panel */
  font-family:
    "Fraunces",
    Georgia,
    serif;

  font-size: clamp(60px, 5.2vw, 88px);
  line-height: 0.98;
  font-weight: 500;
  letter-spacing: -0.03em;

  color: #0d382d;
}

h2 span {
  display: block;
  margin-top: 7px;
  color: #367a59;
}


  /* (duplicate h2 span block kept for specificity; values merged above) */


  .intro {
	max-width: 620px;

    margin:
      23px auto 0;

    text-align: center;

	font-size: 17px;

    line-height: 1.65;

    color: #66776f;
  }


  /* CHOICE */

  .choice-block {
    /* Extra breathing room — separates pitch copy from action cards visually */
    margin-top: 72px;
  }


  .choice-title {
    margin: 0;

    text-align: center;

    font-size: 21px;

    font-weight: 750;

    color: #294b40;
  }


  .choice-subtitle {
    margin:
      5px
      0
      18px;

    text-align: center;

    font-size: 14px;

    color: #7b8882;
  }


  /* ROLE CARDS */

 .role-card {
  width: 100%;
  min-height: 112px;

  margin-bottom: 16px;

  padding: 22px 28px 22px 24px;

  display: grid;
  grid-template-columns: auto 1fr auto;

  align-items: center;
  gap: 18px;

  border: 1px solid #dfe6e1;
  border-left-width: 6px;
  border-radius: 22px;

  background: rgba(255, 255, 255, 0.96);

  box-shadow:
    0 8px 24px rgba(35, 70, 55, 0.06);

  text-decoration: none;
  color: #173d32;

  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease,
    border-color 0.25s ease;
}


  /* Flat white cards — color coding lives in the left accent border,
     not the card fill, so the page gradient stays readable */
  .caregiver {
    background: #ffffff;

    border: 1px solid #e2e8e4;
    border-left: 4px solid #4e9e72;  /* green accent */

    box-shadow: 0 2px 12px rgba(78, 158, 114, 0.07);
    border-left-color: #58a878;
  }


  .senior {
    background: #ffffff;

    border: 1px solid #e8e3d8;
    border-left: 4px solid #d4943a;  /* amber accent */

    box-shadow: 0 2px 12px rgba(212, 148, 58, 0.07);
    border-left-color: #dc9b38;
  }


  .role-card:hover {
    transform:
      translateY(-4px);

    box-shadow:
      0 17px 38px
      rgba(37, 75, 58, 0.11);
  }


  .caregiver:hover {
    border-left-color: #3b845c;
    box-shadow: 0 17px 38px rgba(78, 158, 114, 0.14);
    border-color: #b9d8c3;
    border-left-color: #32865a;
  }


  .senior:hover {
    border-left-color: #b87a28;
    box-shadow: 0 17px 38px rgba(212, 148, 58, 0.14);
    border-color: #ead5ae;
    border-left-color: #bd7620;
  }


  .role-icon {
  width: 58px;
  height: 58px;

  display: grid;
  place-items: center;

  border-radius: 0;

  background: transparent;

  font-size: 25px;
}


  .senior-heart {
    color: #2e7457;

    font-size: 30px;
  }


  .role-copy {
    display: flex;

    flex-direction: column;
  }


  .role-main {
    margin-bottom: 3px;

    font-size: 13px;

    font-weight: 650;

    color: #648076;
  }


  .role-copy strong {
    font-size: 19px;
  }


  .role-copy p {
    margin:
      5px
      0
      0;

    font-size: 14px;

    line-height: 1.4;

    color: #65766f;
  }


  .arrow {
    width: 39px;
    height: 39px;

    display: grid;

    place-items: center;

    border-radius: 50%;

    /* Base — overridden per-card below */
    background:
      rgba(38, 106, 77, 0.07);
    background: #ebf4ee;

    font-size: 20px;

    transition:
      transform 0.22s ease;
  }

  /* Tint arrow circle to match each card's accent */
  .caregiver .arrow {
    background: rgba(78, 158, 114, 0.12);  /* soft green */
    color: #3b845c;
  }

  .senior .arrow {
    background: rgba(212, 148, 58, 0.13);  /* soft amber */
    color: #9c6b1e;
  }


  .senior .arrow {
    background: #fbf1e2;
    color: #9b651e;
  }


  .role-card:focus-visible {
    outline: 3px solid #2d7a57;
    outline-offset: 4px;
  }


  .role-card:hover
  .arrow {
    transform:
      translateX(5px);
  }


  /* PRIVACY */

  .privacy {
    width: fit-content;

    margin:
      26px
      auto 0;

    padding:
      10px 14px;

    display: flex;

    align-items: center;

    gap: 9px;

    border-radius: 13px;

    background:
      rgba(255, 255, 255, 0.36);

    color: #65766f;
  }


  .privacy-icon {
    width: 29px;
    height: 29px;

    display: grid;

    place-items: center;

    border-radius: 9px;

    background: #e5efdf;

    color: #3b795d;

    font-size: 14px;
  }


  .privacy > div:last-child {
    display: flex;

    flex-direction: column;
  }


  .privacy strong {
    font-size: 10px;

    color: #405d52;
  }


  .privacy span {
    margin-top: 2px;

    font-size: 9px;

    color: #819087;
  }


  /* FOOTER */

  .footer {
    position: absolute;

    bottom: 26px;

    left: 50%;

    transform:
      translateX(-50%);

    width: max-content;

    display: flex;

    align-items: center;

    gap: 6px;

    font-size: 10px;

    color: #78877f;
  }


  .footer span {
    font-size: 15px;

    color: #4e8a6b;
  }


  /* MOBILE */

  @media (max-width: 900px) {

    .welcome-page {
      grid-template-columns: 1fr;
    }


    .hero {
      min-height: 720px;
    }


    .role-section {
      min-height: 720px;
    }

  }


  @media (max-width: 600px) {

    .hero {
      min-height: 660px;

      padding:
        28px
        20px;
    }


    .hero-image {
      object-position:
        57% center;
    }


    .brand {
      justify-content: center;
    }


    .hero-copy {
      margin-top: 90px;

      text-align: center;
    }


    .eyebrow {
      font-size: 9px;
    }


    h1 {
      font-size:
        clamp(40px, 11vw, 50px);
    }


    .hero-copy > p {
      max-width: 350px;

      margin:
        20px
        auto 0;

      font-size: 14px;
    }


    .benefits {
      grid-template-columns:
        repeat(3, 1fr);

      gap: 7px;
    }


    .benefit {
      min-height: 88px;

      padding:
        10px
        5px;

      flex-direction: column;

      justify-content: center;

      text-align: center;
    }


    .benefit-icon {
      width: 30px;
      height: 30px;

      font-size: 16px;
    }


    .benefit strong {
      font-size: 10px;
    }


    .benefit span {
      font-size: 9px;
    }


    .role-section {
      min-height: 700px;

      padding:
        60px
        20px
        80px;
    }


    h2 {
      font-size: 48px;
    }


    .intro {
      font-size: 15px;
    }


    .choice-block {
      margin-top: 34px;
    }


    .role-card {
      min-height: 96px;

      padding:
        14px;
    }


    .role-icon {
      width: 45px;
      height: 45px;
    }


    .role-copy strong {
      font-size: 16px;
    }


    .role-copy p {
      font-size: 13px;
    }

  }

</style>
