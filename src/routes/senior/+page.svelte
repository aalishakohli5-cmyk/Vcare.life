<svelte:head>
  <title>Vcare.life — Senior Dashboard</title>
  <meta
    name="description"
    content="Simple daily care dashboard for seniors using Vcare.life."
  />
</svelte:head>

<script>
  let medicines = [
    {
      name: "Morning Medicine",
      time: "8:00 AM",
      status: "taken"
    },
    {
      name: "Blood Sugar Check",
      time: "11:00 AM",
      status: "pending"
    },
    {
      name: "Lunch Medicine",
      time: "1:00 PM",
      status: "pending"
    },
    {
      name: "Evening Walk",
      time: "5:00 PM",
      status: "pending"
    }
  ];

  let mood = "Happy";

  function markTaken(index) {
    medicines[index].status = "taken";
    medicines = [...medicines];
  }
</script>

<div class="senior-page">

  <!-- =========================
       TOP BAR
       ========================= -->
  <header class="topbar">

    <a href="/" class="brand">
      <div class="logo">♥</div>

      <div>
        <strong>Vcare.life</strong>
        <span>A Voice That Cares</span>
      </div>
    </a>

    <div class="top-actions">
      <button class="icon-button" aria-label="Notifications">
        🔔
      </button>

      <div class="profile">
        <div class="avatar">SD</div>

        <div class="profile-copy">
          <strong>Shanta Devi</strong>
          <span>My Vcare</span>
        </div>
      </div>
    </div>

  </header>


  <!-- =========================
       MAIN
       ========================= -->
  <main class="main">

    <!-- GREETING -->
    <section class="greeting">

      <div>
        <p class="eyebrow">GOOD MORNING</p>

        <h1>
          Namaste, Shanta 👋
        </h1>

        <p class="greeting-text">
          I'm here with you today.
          Let's take things one step at a time.
        </p>
      </div>

      <div class="status-pill">
        <span class="status-dot"></span>
        Doing well
      </div>

    </section>


    <!-- =========================
         AI COMPANION HERO
         ========================= -->
    <section class="ai-card">

      <div class="ai-decoration glow-one"></div>
      <div class="ai-decoration glow-two"></div>

      <div class="ai-left">

        <div class="ai-orb">

          <div class="orb-ring ring-one"></div>
          <div class="orb-ring ring-two"></div>

          <div class="robot-face">
            <div class="eyes">
              <span></span>
              <span></span>
            </div>

            <div class="smile"></div>
          </div>

        </div>

      </div>


      <div class="ai-copy">

        <p class="ai-label">
          YOUR VCARE COMPANION
        </p>

        <h2>
          How are you feeling today?
        </h2>

        <p>
          You can talk to me anytime.
          I can remind you about medicines,
          appointments and help you stay connected.
        </p>

        <div class="ai-actions">

          <button class="talk-button">
            <span class="mic">🎙</span>
            Talk to Vcare
          </button>

          <button class="secondary-button">
            ☎ Call Family
          </button>

        </div>

      </div>

    </section>


    <!-- =========================
         TODAY
         ========================= -->
    <section class="today-section">

      <div class="section-heading">

        <div>
          <p class="eyebrow dark">YOUR DAY</p>
          <h2>Today's plan</h2>
        </div>

        <div class="progress">
          {
            medicines.filter((item) => item.status === "taken").length
          }
          / {medicines.length} done
        </div>

      </div>


      <div class="task-list">

        {#each medicines as medicine, index}

          <div
            class:done={medicine.status === "taken"}
            class="task"
          >

            <button
              class="check"
              onclick={() => markTaken(index)}
              aria-label="Mark task as done"
            >
              {medicine.status === "taken" ? "✓" : ""}
            </button>

            <div class="task-copy">
              <strong>{medicine.name}</strong>
              <span>{medicine.time}</span>
            </div>

            <div class="task-status">
              {medicine.status === "taken" ? "Done" : "Upcoming"}
            </div>

          </div>

        {/each}

      </div>

    </section>


    <!-- =========================
         QUICK CARDS
         ========================= -->
    <section class="quick-grid">

      <a href="/senior/medications" class="quick-card">
        <div class="quick-icon medicine">💊</div>

        <div>
          <strong>My Medicines</strong>
          <span>View reminders and medicines</span>
        </div>

        <div class="quick-arrow">→</div>
      </a>


      <a href="/senior/dashboard" class="quick-card">
        <div class="quick-icon appointment">📅</div>

        <div>
          <strong>Appointments & Routine</strong>
          <span>See what's coming next</span>
        </div>

        <div class="quick-arrow">→</div>
      </a>


      <a href="/senior/dashboard" class="quick-card">
        <div class="quick-icon wellness">♡</div>

        <div>
          <strong>How I'm Feeling</strong>
          <span>Share your mood with Vcare</span>
        </div>

        <div class="quick-arrow">→</div>
      </a>


      <a href="/senior/dashboard" class="quick-card">
        <div class="quick-icon family">👨‍👩‍👧</div>

        <div>
          <strong>Care Circle & Family</strong>
          <span>Stay connected with loved ones</span>
        </div>

        <div class="quick-arrow">→</div>
      </a>

    </section>


    <!-- =========================
         UPCOMING APPOINTMENT
         ========================= -->
    <section class="upcoming">

      <div class="upcoming-icon">
        📅
      </div>

      <div class="upcoming-copy">
        <span>NEXT APPOINTMENT</span>

        <strong>
          Dr. Malik — Cardiology
        </strong>

        <p>
          Thursday · 10:00 AM
        </p>
      </div>

      <button class="view-button">
        View
      </button>

    </section>


    <!-- =========================
         MOOD
         ========================= -->
    <section class="mood-section">

      <div>

        <p class="eyebrow dark">
          DAILY WELLNESS
        </p>

        <h2>
          How are you feeling?
        </h2>

        <p class="mood-subtitle">
          Tap what feels closest today.
        </p>

      </div>


      <div class="moods">

        <button
          class:active={mood === "Happy"}
          onclick={() => (mood = "Happy")}
        >
          😊
          <span>Happy</span>
        </button>

        <button
          class:active={mood === "Okay"}
          onclick={() => (mood = "Okay")}
        >
          🙂
          <span>Okay</span>
        </button>

        <button
          class:active={mood === "Tired"}
          onclick={() => (mood = "Tired")}
        >
          😴
          <span>Tired</span>
        </button>

        <button
          class:active={mood === "Not well"}
          onclick={() => (mood = "Not well")}
        >
          😕
          <span>Not well</span>
        </button>

      </div>

    </section>


    <!-- =========================
         HELP
         ========================= -->
    <section class="help-card">

      <div>

        <p class="help-label">
          NEED SOMEONE?
        </p>

        <h2>
          Your family is only a call away.
        </h2>

        <p>
          If you ever need help, Vcare can help you
          reach someone you trust.
        </p>

      </div>

      <button class="family-call">
        ☎ Call Priya
      </button>

    </section>

  </main>


  <!-- =========================
       MOBILE NAV
       ========================= -->
  <nav class="mobile-nav">

    <a href="/senior" class="active">
      <span>⌂</span>
      Home
    </a>

    <a href="/senior/medications">
      <span>💊</span>
      Medicines
    </a>

    <button class="voice-nav">
      🎙
    </button>

    <a href="/senior/dashboard">
      <span>▣</span>
      Routines
    </a>

    <a href="/senior/dashboard">
      <span>♡</span>
      Care Circle
    </a>

  </nav>

</div>


<style>

  :global(*) {
    box-sizing: border-box;
  }

  :global(html),
  :global(body) {
    margin: 0;
    padding: 0;
    min-height: 100%;
  }

  :global(body) {
    font-family:
      Inter,
      -apple-system,
      BlinkMacSystemFont,
      "Segoe UI",
      sans-serif;

    background: #f5f7f1;
    color: #153d32;
  }

  :global(button) {
    font-family: inherit;
  }


  /* =========================
     PAGE
     ========================= */

  .senior-page {
    min-height: 100vh;

    background:
      radial-gradient(
        circle at 100% 0%,
        rgba(193, 223, 178, 0.28),
        transparent 26%
      ),
      linear-gradient(
        180deg,
        #f9faf5 0%,
        #f4f7f0 100%
      );
  }


  /* =========================
     TOP BAR
     ========================= */

  .topbar {
    height: 86px;

    padding:
      0
      clamp(22px, 5vw, 74px);

    display: flex;

    align-items: center;

    justify-content: space-between;

    border-bottom:
      1px solid
      rgba(39, 78, 62, 0.08);

    background:
      rgba(250, 251, 247, 0.82);

    backdrop-filter:
      blur(18px);

    position: sticky;

    top: 0;

    z-index: 30;
  }


  .brand {
    display: flex;

    align-items: center;

    gap: 11px;

    text-decoration: none;

    color: #153d32;
  }


  .logo {
    width: 40px;
    height: 40px;

    display: grid;

    place-items: center;

    border-radius: 13px;

    background: #176348;

    color: white;

    font-size: 20px;
  }


  .brand > div:last-child {
    display: flex;
    flex-direction: column;
  }


  .brand strong {
    font-size: 18px;
  }


  .brand span {
    margin-top: 2px;

    font-size: 9px;

    color: #7b8b84;
  }


  .top-actions {
    display: flex;

    align-items: center;

    gap: 17px;
  }


  .icon-button {
    width: 43px;
    height: 43px;

    border: 0;

    border-radius: 13px;

    background: white;

    cursor: pointer;

    box-shadow:
      0 6px 20px
      rgba(34, 70, 54, 0.06);
  }


  .profile {
    display: flex;

    align-items: center;

    gap: 9px;
  }


  .avatar {
    width: 42px;
    height: 42px;

    display: grid;

    place-items: center;

    border-radius: 50%;

    background:
      linear-gradient(
        135deg,
        #dcead5,
        #f3dfaf
      );

    color: #1d5c46;

    font-size: 12px;

    font-weight: 800;
  }


  .profile-copy {
    display: flex;

    flex-direction: column;
  }


  .profile-copy strong {
    font-size: 12px;
  }


  .profile-copy span {
    margin-top: 2px;

    font-size: 9px;

    color: #839087;
  }


  /* =========================
     MAIN
     ========================= */

  .main {
    width: min(1180px, calc(100% - 40px));

    margin: auto;

    padding:
      54px
      0
      100px;
  }


  /* =========================
     GREETING
     ========================= */

  .greeting {
    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 30px;

    margin-bottom: 33px;
  }


  .eyebrow {
    margin:
      0
      0
      8px;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 0.18em;

    color: #4e8469;
  }


  .eyebrow.dark {
    color: #5b796d;
  }


  .greeting h1 {
    margin: 0;

    font-family:
      Georgia,
      "Times New Roman",
      serif;

    font-size:
      clamp(40px, 5vw, 62px);

    line-height: 1;

    font-weight: 500;

    letter-spacing: -0.045em;
  }


  .greeting-text {
    margin:
      13px
      0
      0;

    color: #6d7c75;

    font-size: 14px;
  }


  .status-pill {
    padding:
      11px
      15px;

    display: flex;

    align-items: center;

    gap: 8px;

    border-radius: 99px;

    background: #e8f5e2;

    color: #347055;

    font-size: 12px;

    font-weight: 700;
  }


  .status-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #3da968;

    box-shadow:
      0 0 0 5px
      rgba(61, 169, 104, 0.12);
  }


  /* =========================
     AI CARD
     ========================= */

  .ai-card {
    position: relative;

    min-height: 330px;

    padding:
      clamp(30px, 4vw, 50px);

    display: grid;

    grid-template-columns:
      0.72fr
      1.28fr;

    align-items: center;

    gap: 40px;

    overflow: hidden;

    border-radius: 32px;

    color: white;

    background:
      linear-gradient(
        135deg,
        #0e4938 0%,
        #176248 58%,
        #31805c 100%
      );

    box-shadow:
      0 25px 60px
      rgba(21, 80, 58, 0.18);

    margin-bottom: 46px;
  }


  .ai-decoration {
    position: absolute;

    border-radius: 50%;

    pointer-events: none;
  }


  .glow-one {
    width: 350px;
    height: 350px;

    top: -190px;
    right: -100px;

    background:
      radial-gradient(
        circle,
        rgba(225, 241, 176, 0.20),
        transparent 70%
      );
  }


  .glow-two {
    width: 280px;
    height: 280px;

    bottom: -170px;
    left: -100px;

    background:
      radial-gradient(
        circle,
        rgba(242, 210, 141, 0.14),
        transparent 70%
      );
  }


  .ai-left {
    display: grid;

    place-items: center;

    position: relative;

    z-index: 2;
  }


  .ai-orb {
    position: relative;

    width: 180px;
    height: 180px;

    display: grid;

    place-items: center;

    border-radius: 50%;

    background:
      radial-gradient(
        circle,
        #f4fff0 0%,
        #dbeed5 55%,
        #a9d4a2 100%
      );

    box-shadow:
      0 0 60px
      rgba(217, 240, 201, 0.28);
  }


  .orb-ring {
    position: absolute;

    border-radius: 50%;

    border:
      1px solid
      rgba(231, 247, 219, 0.28);

    animation:
      pulseRing
      3s
      ease-out
      infinite;
  }


  .ring-one {
    width: 215px;
    height: 215px;
  }


  .ring-two {
    width: 250px;
    height: 250px;

    animation-delay: 1.5s;
  }


  @keyframes pulseRing {

    0% {
      transform: scale(0.82);
      opacity: 0;
    }

    35% {
      opacity: 0.7;
    }

    100% {
      transform: scale(1.1);
      opacity: 0;
    }

  }


  .robot-face {
    width: 88px;
    height: 88px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    border-radius: 28px;

    background:
      linear-gradient(
        145deg,
        #126044,
        #1c7955
      );

    box-shadow:
      0 14px 34px
      rgba(5, 55, 38, 0.18);
  }


  .eyes {
    display: flex;

    gap: 22px;
  }


  .eyes span {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: white;
  }


  .smile {
    width: 28px;
    height: 14px;

    margin-top: 11px;

    border-bottom:
      3px solid white;

    border-radius:
      0 0 30px 30px;
  }


  .ai-copy {
    position: relative;

    z-index: 2;
  }


  .ai-label {
    margin:
      0
      0
      10px;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 0.18em;

    color: #dcecbf;
  }


  .ai-copy h2 {
    margin: 0;

    max-width: 550px;

    font-family:
      Georgia,
      "Times New Roman",
      serif;

    font-size:
      clamp(38px, 4vw, 52px);

    line-height: 1;

    font-weight: 500;

    letter-spacing: -0.04em;
  }


  .ai-copy > p:not(.ai-label) {
    max-width: 540px;

    margin:
      18px
      0
      0;

    color:
      rgba(255, 255, 255, 0.74);

    font-size: 13px;

    line-height: 1.65;
  }


  .ai-actions {
    margin-top: 25px;

    display: flex;

    flex-wrap: wrap;

    gap: 11px;
  }


  .talk-button,
  .secondary-button {
    min-height: 50px;

    padding:
      0
      20px;

    border-radius: 15px;

    cursor: pointer;

    font-size: 13px;

    font-weight: 750;

    transition:
      transform 0.2s ease;
  }


  .talk-button {
    border: 0;

    color: #134d3a;

    background:
      linear-gradient(
        135deg,
        #f4f7dc,
        #dceab9
      );

    box-shadow:
      0 12px 27px
      rgba(4, 45, 31, 0.16);
  }


  .secondary-button {
    border:
      1px solid
      rgba(255, 255, 255, 0.24);

    color: white;

    background:
      rgba(255, 255, 255, 0.10);
  }


  .talk-button:hover,
  .secondary-button:hover {
    transform:
      translateY(-3px);
  }


  .mic {
    margin-right: 6px;
  }


  /* =========================
     TODAY
     ========================= */

  .today-section,
  .mood-section {
    padding:
      30px;

    border-radius: 25px;

    background: white;

    border:
      1px solid
      rgba(40, 79, 63, 0.08);

    box-shadow:
      0 10px 35px
      rgba(31, 67, 52, 0.05);

    margin-bottom: 30px;
  }


  .section-heading {
    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 20px;

    margin-bottom: 22px;
  }


  .section-heading h2,
  .mood-section h2,
  .help-card h2 {
    margin: 0;

    font-family:
      Georgia,
      "Times New Roman",
      serif;

    font-size: 31px;

    font-weight: 500;

    letter-spacing:
      -0.035em;
  }


  .progress {
    padding:
      8px
      11px;

    border-radius: 99px;

    background: #edf6e9;

    color: #4a765f;

    font-size: 10px;

    font-weight: 700;
  }


  .task-list {
    display: grid;

    gap: 9px;
  }


  .task {
    min-height: 70px;

    padding:
      12px
      15px;

    display: grid;

    grid-template-columns:
      auto
      1fr
      auto;

    align-items: center;

    gap: 13px;

    border-radius: 17px;

    border:
      1px solid
      #e4e9e2;

    background: #fbfcf9;
  }


  .task.done {
    background: #f0f7ec;

    border-color: #d5e7ce;
  }


  .check {
    width: 34px;
    height: 34px;

    display: grid;

    place-items: center;

    border-radius: 50%;

    border:
      2px solid #b8c4bd;

    background: white;

    color: white;

    cursor: pointer;
  }


  .done .check {
    border-color: #44a864;

    background: #44a864;
  }


  .task-copy {
    display: flex;

    flex-direction: column;
  }


  .task-copy strong {
    font-size: 13px;
  }


  .task-copy span {
    margin-top: 4px;

    font-size: 10px;

    color: #859089;
  }


  .task-status {
    font-size: 10px;

    color: #849089;
  }


  .done .task-status {
    color: #3f815b;
  }


  /* =========================
     QUICK GRID
     ========================= */

  .quick-grid {
    margin-bottom: 30px;

    display: grid;

    grid-template-columns:
      repeat(2, 1fr);

    gap: 13px;
  }


  .quick-card {
    min-height: 105px;

    padding:
      18px;

    display: grid;

    grid-template-columns:
      auto 1fr auto;

    align-items: center;

    gap: 14px;

    border-radius: 20px;

    text-decoration: none;

    color: #163e33;

    border:
      1px solid
      rgba(42, 79, 63, 0.09);

    background: white;

    transition:
      transform 0.22s ease,
      box-shadow 0.22s ease;
  }


  .quick-card:hover {
    transform: translateY(-4px);

    box-shadow:
      0 15px 35px
      rgba(31, 67, 52, 0.08);
  }


  .quick-icon {
    width: 52px;
    height: 52px;

    display: grid;

    place-items: center;

    border-radius: 15px;

    font-size: 22px;
  }


  .quick-icon.medicine {
    background: #e9f3e5;
  }


  .quick-icon.appointment {
    background: #edf0ff;
  }


  .quick-icon.wellness {
    background: #fff3df;

    color: #2d7a5b;

    font-size: 30px;
  }


  .quick-icon.family {
    background: #f0eafd;
  }


  .quick-card strong {
    display: block;

    font-size: 13px;
  }


  .quick-card span {
    display: block;

    margin-top: 4px;

    color: #78877f;

    font-size: 10px;
  }


  .quick-arrow {
    font-size: 18px;

    transition:
      transform 0.2s ease;
  }


  .quick-card:hover
  .quick-arrow {
    transform:
      translateX(4px);
  }


  /* =========================
     UPCOMING
     ========================= */

  .upcoming {
    min-height: 120px;

    padding:
      20px
      24px;

    display: grid;

    grid-template-columns:
      auto 1fr auto;

    align-items: center;

    gap: 17px;

    border-radius: 22px;

    background:
      linear-gradient(
        120deg,
        #fff7e7,
        #fffdf4
      );

    border:
      1px solid
      #eeddb8;

    margin-bottom: 30px;
  }


  .upcoming-icon {
    width: 55px;
    height: 55px;

    display: grid;

    place-items: center;

    border-radius: 16px;

    background: white;

    font-size: 23px;
  }


  .upcoming-copy {
    display: flex;

    flex-direction: column;
  }


  .upcoming-copy > span {
    font-size: 8px;

    font-weight: 800;

    letter-spacing: 0.14em;

    color: #aa8652;
  }


  .upcoming-copy strong {
    margin-top: 5px;

    font-size: 14px;
  }


  .upcoming-copy p {
    margin:
      4px
      0
      0;

    font-size: 11px;

    color: #897b68;
  }


  .view-button {
    min-width: 70px;

    height: 40px;

    border: 0;

    border-radius: 12px;

    background: #f0e6cb;

    color: #6e5a36;

    cursor: pointer;

    font-weight: 700;
  }


  /* =========================
     MOOD
     ========================= */

  .mood-subtitle {
    margin:
      9px
      0
      20px;

    font-size: 12px;

    color: #7e8a84;
  }


  .moods {
    display: grid;

    grid-template-columns:
      repeat(4, 1fr);

    gap: 10px;
  }


  .moods button {
    min-height: 95px;

    border:
      1px solid
      #e2e7e0;

    border-radius: 18px;

    background: #fafbf8;

    cursor: pointer;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    gap: 7px;

    font-size: 26px;

    transition:
      transform 0.18s ease,
      background 0.18s ease,
      border-color 0.18s ease;
  }


  .moods button:hover {
    transform: translateY(-3px);
  }


  .moods button span {
    font-size: 10px;

    color: #5d7167;
  }


  .moods button.active {
    background: #e9f5e5;

    border-color: #abd19f;
  }


  /* =========================
     HELP
     ========================= */

  .help-card {
    min-height: 190px;

    padding:
      30px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 30px;

    border-radius: 26px;

    background:
      linear-gradient(
        120deg,
        #edf6e7,
        #faf5e6
      );

    border:
      1px solid
      rgba(79, 120, 83, 0.13);
  }


  .help-label {
    margin:
      0
      0
      8px;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 0.17em;

    color: #507a64;
  }


  .help-card > div > p:last-child {
    max-width: 520px;

    margin:
      11px
      0
      0;

    font-size: 12px;

    line-height: 1.6;

    color: #76827c;
  }


  .family-call {
    min-width: 145px;

    height: 51px;

    border: 0;

    border-radius: 16px;

    background: #176348;

    color: white;

    cursor: pointer;

    font-weight: 750;

    box-shadow:
      0 14px 28px
      rgba(23, 99, 72, 0.15);
  }


  /* =========================
     MOBILE NAV
     ========================= */

  .mobile-nav {
    display: none;
  }


  /* =========================
     TABLET
     ========================= */

  @media (max-width: 850px) {

    .ai-card {
      grid-template-columns: 1fr;

      text-align: center;
    }


    .ai-copy > p:not(.ai-label) {
      margin-left: auto;
      margin-right: auto;
    }


    .ai-actions {
      justify-content: center;
    }


    .quick-grid {
      grid-template-columns: 1fr;
    }

  }


  /* =========================
     MOBILE
     ========================= */

  @media (max-width: 600px) {

    .topbar {
      height: 69px;

      padding:
        0
        15px;
    }


    .brand span,
    .profile-copy {
      display: none;
    }


    .top-actions {
      gap: 8px;
    }


    .icon-button {
      width: 38px;
      height: 38px;
    }


    .avatar {
      width: 38px;
      height: 38px;
    }


    .main {
      width:
        calc(100% - 28px);

      padding:
        31px
        0
        105px;
    }


    .greeting {
      align-items: flex-start;

      flex-direction: column;

      gap: 16px;
    }


    .greeting h1 {
      font-size: 42px;
    }


    .status-pill {
      padding:
        9px
        12px;
    }


    .ai-card {
      min-height: 530px;

      padding:
        35px
        20px;

      border-radius: 26px;
    }


    .ai-orb {
      width: 140px;
      height: 140px;
    }


    .ring-one {
      width: 170px;
      height: 170px;
    }


    .ring-two {
      width: 195px;
      height: 195px;
    }


    .robot-face {
      width: 72px;
      height: 72px;
    }


    .ai-copy h2 {
      font-size: 37px;
    }


    .ai-actions {
      display: grid;

      grid-template-columns: 1fr;

      width: 100%;
    }


    .talk-button,
    .secondary-button {
      width: 100%;
    }


    .today-section,
    .mood-section {
      padding: 21px;

      border-radius: 21px;
    }


    .section-heading {
      align-items: flex-start;
    }


    .section-heading h2,
    .mood-section h2,
    .help-card h2 {
      font-size: 27px;
    }


    .task {
      min-height: 68px;
    }


    .task-status {
      display: none;
    }


    .quick-card {
      min-height: 92px;

      padding: 15px;
    }


    .upcoming {
      padding: 17px;

      grid-template-columns:
        auto
        1fr;
    }


    .view-button {
      grid-column:
        1 / -1;

      width: 100%;
    }


    .moods {
      grid-template-columns:
        repeat(2, 1fr);
    }


    .help-card {
      flex-direction: column;

      align-items: flex-start;
    }


    .family-call {
      width: 100%;
    }


    /* fixed mobile navigation */

    .mobile-nav {
      position: fixed;

      display: grid;

      grid-template-columns:
        repeat(5, 1fr);

      align-items: center;

      bottom: 0;
      left: 0;

      width: 100%;

      height: 72px;

      padding:
        6px
        9px;

      z-index: 50;

      border-top:
        1px solid
        rgba(30, 66, 51, 0.08);

      background:
        rgba(252, 252, 248, 0.94);

      backdrop-filter:
        blur(18px);
    }


    .mobile-nav a {
      display: flex;

      flex-direction: column;

      align-items: center;

      gap: 3px;

      text-decoration: none;

      color: #77847e;

      font-size: 8px;
    }


    .mobile-nav a span {
      font-size: 18px;
    }


    .mobile-nav a.active {
      color: #176348;
    }


    .voice-nav {
      width: 52px;
      height: 52px;

      margin: auto;

      border: 0;

      border-radius: 50%;

      background: #176348;

      color: white;

      font-size: 20px;

      box-shadow:
        0 10px 25px
        rgba(23, 99, 72, 0.25);
    }

  }

</style>
