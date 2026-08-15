<script>
  let { children } = $props();
</script>

<!-- Some classes will be seperated to it's own ./styling.css also will add attribute thingies  -->
<div class="bg-blue rounded-lg min-h-24 p-2">
  <div class="flex items-center gap-2">
    <div class="bg-red size-6 rounded-full"></div>
    <div class="text-md font-bold">Username</div>
  </div>
  <div class="mt-2">
    <p>
      {@render children()}
    </p>
  </div>
  <div class="footer flex gap-2 mt-4">
    <div>
      <i class="tab__icon lucide:heart"></i>
      <span text-sm>202 Hugs</span>
    </div>
    <div>
      <i class="tab__icon lucide:reply"></i>
      <span text-sm>Reply</span>
    </div>
  </div>
</div>
