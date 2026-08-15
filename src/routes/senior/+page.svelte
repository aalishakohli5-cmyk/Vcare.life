<div class="min-h-screen bg-blue-50 p-8">

  <div class="flex items-center gap-4 mb-8">
    <div class="w-16 h-16 rounded-full bg-white shadow-sm flex items-center justify-center">
      <i class="lucide:user text-blue-500 text-3xl"></i>
    </div>
    <div>
      <h1 class="text-2xl font-bold text-gray-800">Hi Sarah 👋</h1>
      <p class="text-base text-gray-500">Here's your day</p>
    </div>
  </div>

  <!-- Today's Check-In -->
  <div class="bg-white rounded-3xl shadow-sm p-8 mb-6">
    <h2 class="text-xl font-semibold text-gray-800 mb-4">Today's Check-In</h2>

    <div class="flex gap-4 mb-6">
      <div class="flex-1 bg-emerald-50 rounded-2xl p-4 text-center">
        <i class="lucide:check-circle text-emerald-500 text-3xl mb-2"></i>
        <p class="text-sm text-gray-600">Morning Meds</p>
      </div>
      <div class="flex-1 bg-emerald-50 rounded-2xl p-4 text-center">
        <i class="lucide:check-circle text-emerald-500 text-3xl mb-2"></i>
        <p class="text-sm text-gray-600">Evening Meds</p>
      </div>
      <div class="flex-1 bg-amber-50 rounded-2xl p-4 text-center">
        <i class="lucide:clock text-amber-500 text-3xl mb-2"></i>
        <p class="text-sm text-gray-600">Evening Walk</p>
      </div>
    </div>

    <button class="w-full bg-blue-600 text-white text-xl font-semibold py-5 rounded-2xl flex items-center justify-center gap-3">
      <i class="lucide:phone-call"></i>
      Call Me
    </button>
  </div>

  <!-- Quick actions -->
  <div class="grid grid-cols-2 gap-4">
    <button class="bg-white rounded-2xl shadow-sm p-6 flex flex-col items-center gap-2">
      <i class="lucide:message-circle text-indigo-500 text-3xl"></i>
      <span class="text-base font-medium text-gray-700">Text with AI</span>
    </button>
    <button class="bg-white rounded-2xl shadow-sm p-6 flex flex-col items-center gap-2">
      <i class="lucide:calendar text-blue-500 text-3xl"></i>
      <span class="text-base font-medium text-gray-700">Appointments</span>
    </button>
    <button class="bg-white rounded-2xl shadow-sm p-6 flex flex-col items-center gap-2">
      <i class="lucide:smile text-amber-500 text-3xl"></i>
      <span class="text-base font-medium text-gray-700">How I'm Feeling</span>
    </button>
    <button class="bg-white rounded-2xl shadow-sm p-6 flex flex-col items-center gap-2 relative">
      <i class="lucide:alert-circle text-red-500 text-3xl"></i>
      <span class="text-base font-medium text-gray-700">Emergency</span>
    </button>
  </div>

</div>