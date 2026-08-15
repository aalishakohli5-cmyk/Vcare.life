<div class="min-h-screen bg-gray-50 p-8">
  <header class="flex items-center justify-between bg-white rounded-2xl shadow-sm p-6 mb-6">
    <div class="flex items-center gap-4">
      <div class="w-14 h-14 rounded-full bg-indigo-100 flex items-center justify-center">
        <i class="lucide:user text-indigo-500 text-2xl"></i>
      </div>
      <div>
        <h1 class="text-xl font-semibold text-gray-800">Sarah Johnson</h1>
        <p class="text-sm text-gray-400">Patient overview</p>
      </div>
    </div>
    <button class="flex items-center gap-2 bg-gray-100 rounded-full px-4 py-2 text-sm text-gray-600">
      <i class="lucide:settings"></i>
      Settings
    </button>
  </header>

  <!-- Alert Banner -->
  <div class="flex items-center justify-between bg-amber-100 border border-amber-300 rounded-2xl px-6 py-4 mb-6">
    <div class="flex items-center gap-3">
      <i class="lucide:alert-triangle text-amber-600 text-xl"></i>
      <div>
        <p class="font-medium text-amber-800">Missed call detected</p>
        <p class="text-sm text-amber-600">1:30 PM check-in was not answered</p>
      </div>
    </div>
    <button class="bg-amber-600 text-white text-sm px-4 py-2 rounded-full">Resolve</button>
  </div>

  <section class="grid grid-cols-3 gap-6 mb-6">

    <!-- Medication Adherence Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:pill text-indigo-500"></i>
        <h2 class="font-semibold text-gray-800">Medication Adherence</h2>
      </div>
      <div class="flex items-end gap-2 h-32">
        <div class="flex-1 bg-indigo-400 rounded-t-md" style="height: 80%"></div>
        <div class="flex-1 bg-indigo-400 rounded-t-md" style="height: 100%"></div>
        <div class="flex-1 bg-indigo-400 rounded-t-md" style="height: 60%"></div>
        <div class="flex-1 bg-indigo-400 rounded-t-md" style="height: 100%"></div>
        <div class="flex-1 bg-indigo-400 rounded-t-md" style="height: 90%"></div>
        <div class="flex-1 bg-indigo-400 rounded-t-md" style="height: 100%"></div>
        <div class="flex-1 bg-indigo-400 rounded-t-md" style="height: 40%"></div>
      </div>
      <div class="flex justify-between text-xs text-gray-400 mt-2">
        <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span>
        <span>Thu</span><span>Fri</span><span>Sat</span>
      </div>
    </div>

    <!-- Mood Trend Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:smile text-amber-500"></i>
        <h2 class="font-semibold text-gray-800">Mood Trend</h2>
      </div>
      <svg viewBox="0 0 280 100" class="w-full h-32">
        <polyline points="0,60 40,40 80,50 120,20 160,35 200,15 240,30 280,25"
          fill="none" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <div class="flex justify-between text-xs text-gray-400 mt-2">
        <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span>
        <span>Thu</span><span>Fri</span><span>Sat</span>
      </div>
    </div>

    <!-- Recent Calls Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:phone-call text-emerald-500"></i>
        <h2 class="font-semibold text-gray-800">Recent Calls</h2>
      </div>
      <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <i class="lucide:check-circle text-emerald-500 text-sm"></i>
            <span class="text-sm text-gray-700">Answered</span>
          </div>
          <span class="text-xs text-gray-400">9:00 AM</span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <i class="lucide:x-circle text-red-500 text-sm"></i>
            <span class="text-sm text-gray-700">Missed</span>
          </div>
          <span class="text-xs text-gray-400">1:30 PM</span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <i class="lucide:refresh-ccw text-amber-500 text-sm"></i>
            <span class="text-sm text-gray-700">Rescheduled</span>
          </div>
          <span class="text-xs text-gray-400">1:45 PM</span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <i class="lucide:check-circle text-emerald-500 text-sm"></i>
            <span class="text-sm text-gray-700">Answered</span>
          </div>
          <span class="text-xs text-gray-400">6:00 PM</span>
        </div>
      </div>
    </div>

  </section>

  <section class="grid grid-cols-3 gap-6">

    <!-- Vitals Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:heart-pulse text-rose-500"></i>
        <h2 class="font-semibold text-gray-800">Vitals</h2>
      </div>
      <div class="flex justify-between mb-3">
        <span class="text-sm text-gray-500">Blood Pressure</span>
        <span class="text-sm font-medium text-gray-800">120/80 mmHg</span>
      </div>
      <div class="flex justify-between">
        <span class="text-sm text-gray-500">Blood Sugar</span>
        <span class="text-sm font-medium text-gray-800">8.7 mmol/L</span>
      </div>
    </div>

    <!-- Appointment Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:calendar text-blue-500"></i>
        <h2 class="font-semibold text-gray-800">Upcoming Appointment</h2>
      </div>
      <p class="text-sm text-gray-700 font-medium">Dr. Malik — Checkup</p>
      <p class="text-sm text-gray-400">Thursday, 10:00 AM</p>
    </div>

    <!-- Emergency Escalation Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:shield-alert text-red-500"></i>
        <h2 class="font-semibold text-gray-800">Emergency Escalation</h2>
      </div>
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm text-gray-700">1. Primary Caregiver</span>
        <span class="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full">Active</span>
      </div>
      <div class="flex items-center justify-between">
        <span class="text-sm text-gray-700">2. Emergency Contact</span>
        <span class="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded-full">Standby</span>
      </div>
    </div>

  </section>
  <section class="grid grid-cols-3 gap-6 mt-6">

    <!-- Add Medicine Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:plus-circle text-indigo-500"></i>
        <h2 class="font-semibold text-gray-800">Add Medicine</h2>
      </div>
      <div class="flex flex-col gap-3">
        <input
          type="text"
          placeholder="Medicine name"
          class="border border-gray-200 rounded-xl px-3 py-2 text-sm text-gray-700 outline-none focus:border-indigo-400"
        />
        <input
          type="time"
          class="border border-gray-200 rounded-xl px-3 py-2 text-sm text-gray-700 outline-none focus:border-indigo-400"
        />
        <button class="bg-indigo-600 text-white text-sm font-medium py-2 rounded-xl">
          Add
        </button>
      </div>
    </div>

    <!-- Mini Planner Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:list-checks text-emerald-500"></i>
        <h2 class="font-semibold text-gray-800">Today's Planner</h2>
      </div>
      <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-700">🍳 Breakfast</span>
          <span class="text-gray-400">8:00 AM</span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-700">💊 Morning Meds</span>
          <span class="text-gray-400">9:00 AM</span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-700">🚶 Evening Walk</span>
          <span class="text-gray-400">5:00 PM</span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-700">🩺 Checkup</span>
          <span class="text-gray-400">Thu, 10:00 AM</span>
        </div>
      </div>
    </div>

    <!-- Meds Refill Status Card -->
    <div class="bg-white rounded-2xl shadow-sm p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="lucide:package text-amber-500"></i>
        <h2 class="font-semibold text-gray-800">Meds Refill Status</h2>
      </div>
      <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-700">Metformin</span>
          <span class="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full">Low — 3 left</span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-700">Lisinopril</span>
          <span class="text-xs bg-emerald-100 text-emerald-600 px-2 py-1 rounded-full">Stocked</span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-700">Vitamin D</span>
          <span class="text-xs bg-emerald-100 text-emerald-600 px-2 py-1 rounded-full">Stocked</span>
        </div>
      </div>
    </div>

  </section>
</div>