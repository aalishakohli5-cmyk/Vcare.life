<script>
  import './styling.css'
</script>

<nav class="navbar flex" md="hidden">
  <ol class="container max-w-3/4">
    <li class="">
      <a class="navbar__tab navbar__tab--active" href="/">
        <i class="tab__icon lucide:map"></i>
        <p class="tab__title">Map</p>
      </a>
    </li>
    <li>
      <a class="navbar__tab" href="/quests">
        <i class="tab__icon lucide:swords"></i>
        <p class="tab__title">Quests</p>
      </a>
    </li>
    <li>
      <a class="navbar__tab" href="/bag">
        <i class="tab__icon lucide:backpack"></i>
        <p class="tab__title">Bag</p>
      </a>
    </li>
    <li>
      <a class="navbar__tab" href="/settings">
        <i class="tab__icon lucide:settings"></i>
        <p class="tab__title">Settings</p>
      </a>
    </li>
  </ol>
</nav>
