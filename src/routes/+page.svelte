<svelte:head>
  <title>Vcare.life — A Voice That Cares</title>
  <meta
    name="description"
    content="Vcare.life is an AI voice companion for seniors and their families."
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
        <div class="privacy-icon">⌾</div>

        <div>
          <strong>Private & secure</strong>
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

  :global(*) {
    box-sizing: border-box;
  }

  :global(html),
  :global(body) {
    margin: 0;
    padding: 0;
    width: 100%;
    min-height: 100%;
  }

  :global(body) {
    font-family:
      Inter,
      -apple-system,
      BlinkMacSystemFont,
      "Segoe UI",
      sans-serif;

    background: #f8f4ea;
    color: #153d32;
  }


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

    background:
      linear-gradient(
        90deg,
        rgba(5, 49, 36, 0.88) 0%,
        rgba(5, 49, 36, 0.58) 45%,
        rgba(5, 49, 36, 0.20) 82%
      ),
      linear-gradient(
        180deg,
        rgba(5, 45, 34, 0.36) 0%,
        transparent 48%,
        rgba(4, 42, 31, 0.78) 100%
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

    font-weight: 800;

    letter-spacing: 0.18em;

    color: #e0edbd;
  }


  h1 {
    margin: 0;

    max-width: 610px;

    font-family:
      Georgia,
      "Times New Roman",
      serif;

    font-size:
      clamp(48px, 4.4vw, 70px);

    line-height: 0.98;

    letter-spacing:
      -0.045em;

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


  .benefit-icon {
    width: 36px;
    height: 36px;

    display: grid;

    place-items: center;

    border-radius: 11px;

    background:
      rgba(255, 255, 255, 0.58);

    font-size: 20px;
  }


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
  max-width: 650px;
}


  .welcome-label {
    margin:
      0
      0
      12px;

    text-align: center;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 0.18em;

    color: #3b795e;
  }

h2 {
  margin: 0;
  text-align: center;

  font-family:
    Georgia,
    "Times New Roman",
    serif;

  font-size: clamp(52px, 4.5vw, 72px);
  line-height: 0.98;
  font-weight: 500;
  letter-spacing: -0.045em;

  color: #0d382d;
}

h2 span {
  display: block;
  margin-top: 7px;
  color: #367a59;
}


  h2 span {
    display: block;

    margin-top: 5px;

    color: #4d8968;
  }


  .intro {
    max-width: 500px;

    margin:
      23px auto 0;

    text-align: center;

    font-size: 14px;

    line-height: 1.65;

    color: #66776f;
  }


  /* CHOICE */

  .choice-block {
    margin-top: 40px;
  }


  .choice-title {
    margin: 0;

    text-align: center;

    font-size: 17px;

    font-weight: 750;

    color: #294b40;
  }


  .choice-subtitle {
    margin:
      5px
      0
      18px;

    text-align: center;

    font-size: 11px;

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


  .caregiver {
    border-left-color: #58a878;
  }


  .senior {
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
    border-color: #b9d8c3;
    border-left-color: #32865a;
  }


  .senior:hover {
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

    font-size: 10px;

    font-weight: 650;

    color: #648076;
  }


  .role-copy strong {
    font-size: 15px;
  }


  .role-copy p {
    margin:
      5px
      0
      0;

    font-size: 11px;

    line-height: 1.4;

    color: #65766f;
  }


  .arrow {
    width: 39px;
    height: 39px;

    display: grid;

    place-items: center;

    border-radius: 50%;

    background: #ebf4ee;

    font-size: 20px;

    transition:
      transform 0.22s ease;
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
      font-size: 41px;
    }


    .intro {
      font-size: 13px;
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
      font-size: 13px;
    }


    .role-copy p {
      font-size: 10px;
    }

  }

</style>
