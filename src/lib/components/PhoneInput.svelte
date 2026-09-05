<script module>
	/* =====================================================
	   Vcare.life — Shared PhoneInput Component
	   Inline country-code selector + local phone number
	   ===================================================== */

	export const countryCodes = [
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
</script>

<script>

	let {
		id = 'phone',
		value = $bindable(''),
		countryCode = $bindable('+91'),
		placeholder = 'Phone number',
		disabled = false,
		name = '',
		required = false,
		inputmode = 'tel'
	} = $props();

	let dropdownOpen = $state(false);
	let countrySearch = $state('');

	let filteredCountries = $derived(
		countryCodes.filter(
			(item) =>
				item.country.toLowerCase().includes(countrySearch.toLowerCase()) ||
				item.code.includes(countrySearch)
		)
	);

	let selectedCountry = $derived(
		countryCodes.find((c) => c.code === countryCode) || countryCodes[0]
	);

	function toggleDropdown() {
		if (disabled) return;
		dropdownOpen = !dropdownOpen;
		if (!dropdownOpen) {
			countrySearch = '';
		}
	}

	function selectCountry(item) {
		countryCode = item.code;
		countrySearch = '';
		dropdownOpen = false;
	}

	function handleKeydown(e) {
		if (e.key === 'Escape' && dropdownOpen) {
			dropdownOpen = false;
			countrySearch = '';
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="phone-input-root" class:disabled class:is-open={dropdownOpen}>
	<!-- COUNTRY PICKER TRIGGER -->
	<div class="country-picker">
		<button
			type="button"
			class="country-trigger"
			onclick={toggleDropdown}
			{disabled}
			aria-haspopup="listbox"
			aria-expanded={dropdownOpen}
			aria-label="Select country code"
		>
			<span class="flag" aria-hidden="true">{selectedCountry.flag}</span>
			<span class="code">{countryCode}</span>
			<svg
				class="chevron"
				class:rotated={dropdownOpen}
				xmlns="http://www.w3.org/2000/svg"
				width="14"
				height="14"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2.5"
				stroke-linecap="round"
				stroke-linejoin="round"
				aria-hidden="true"
			>
				<path d="m6 9 6 6 6-6" />
			</svg>
		</button>

		<!-- DROPDOWN MENU -->
		{#if dropdownOpen}
			<!-- BACKDROP TO CLOSE ON CLICK OUTSIDE -->
			<div
				class="dropdown-backdrop"
				onclick={() => {
					dropdownOpen = false;
					countrySearch = '';
				}}
				aria-hidden="true"
			></div>

			<div class="country-menu" role="listbox">
				<div class="search-wrap">
					<svg
						class="search-icon"
						xmlns="http://www.w3.org/2000/svg"
						width="14"
						height="14"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						stroke-linecap="round"
						stroke-linejoin="round"
						aria-hidden="true"
					>
						<circle cx="11" cy="11" r="8" />
						<path d="m21 21-4.3-4.3" />
					</svg>
					<input
						type="text"
						class="country-search"
						placeholder="Search country or code..."
						bind:value={countrySearch}
					/>
				</div>

				<div class="country-list">
					{#each filteredCountries as item}
						<button
							type="button"
							class="country-option"
							class:selected={item.code === countryCode && item.country === selectedCountry.country}
							onclick={() => selectCountry(item)}
							role="option"
							aria-selected={item.code === countryCode}
						>
							<span class="option-flag">{item.flag}</span>
							<span class="option-code">{item.code}</span>
							<span class="option-name">{item.country}</span>
						</button>
					{/each}

					{#if filteredCountries.length === 0}
						<div class="no-country">No country found</div>
					{/if}
				</div>
			</div>
		{/if}
	</div>

	<!-- LOCAL PHONE NUMBER INPUT -->
	<input
		{id}
		{name}
		type="tel"
		{inputmode}
		bind:value
		{placeholder}
		{disabled}
		{required}
		class="phone-field"
	/>
</div>

<style>
	.phone-input-root {
		position: relative;
		width: 100%;
		height: 56px;
		display: flex;
		align-items: center;
		border: 1.5px solid var(--color-border, #decdb0);
		border-radius: var(--radius-md, 14px);
		background: var(--color-surface, #ffffff);
		transition: border-color 0.18s ease, box-shadow 0.18s ease;
		font-family: inherit;
		box-sizing: border-box;
	}

	.phone-input-root:focus-within {
		border-color: var(--color-brand-primary, #116240);
		box-shadow: 0 0 0 3px rgba(17, 98, 64, 0.12);
	}

	.phone-input-root.disabled {
		opacity: 0.6;
		cursor: not-allowed;
		background: #f1f5f9;
	}

	/* COUNTRY PICKER */
	.country-picker {
		position: relative;
		height: 100%;
		flex-shrink: 0;
	}

	.country-trigger {
		height: 100%;
		min-width: 96px;
		padding: 0 12px;
		border: none;
		border-right: 1.5px solid var(--color-border, #decdb0);
		border-radius: 12px 0 0 12px;
		background: rgba(235, 238, 207, 0.45);
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 7px;
		color: var(--color-text-primary, #153d30);
		font-family: inherit;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.15s ease;
	}

	.country-trigger:hover:not(:disabled) {
		background: rgba(235, 238, 207, 0.7);
	}

	.flag {
		font-size: 17px;
		line-height: 1;
	}

	.code {
		font-variant-numeric: tabular-nums;
		letter-spacing: -0.01em;
	}

	.chevron {
		color: var(--color-text-muted, #527568);
		transition: transform 0.2s ease;
	}

	.chevron.rotated {
		transform: rotate(180deg);
	}

	/* BACKDROP */
	.dropdown-backdrop {
		position: fixed;
		inset: 0;
		z-index: 999;
		background: transparent;
	}

	/* DROPDOWN MENU */
	.country-menu {
		position: absolute;
		top: calc(100% + 6px);
		left: 0;
		width: 290px;
		max-height: 320px;
		padding: 8px;
		background: #ffffff;
		border: 1.5px solid var(--color-border, #d9cdb8);
		border-radius: var(--radius-md, 14px);
		box-shadow: 0 14px 34px rgba(11, 61, 43, 0.16);
		z-index: 1000;
		box-sizing: border-box;
	}

	.search-wrap {
		position: relative;
		margin-bottom: 6px;
	}

	.search-icon {
		position: absolute;
		left: 10px;
		top: 50%;
		transform: translateY(-50%);
		color: var(--color-text-muted, #64748b);
		pointer-events: none;
	}

	.country-search {
		width: 100%;
		height: 38px;
		padding: 0 12px 0 32px;
		border: 1px solid var(--color-border, #d8c9a8);
		border-radius: 9px;
		background: #fafaf9;
		color: var(--color-text-primary, #1e293b);
		font-family: inherit;
		font-size: 13px;
		outline: none;
		box-sizing: border-box;
	}

	.country-search:focus {
		border-color: var(--color-brand-primary, #116240);
		background: #ffffff;
	}

	.country-list {
		max-height: 230px;
		overflow-y: auto;
	}

	.country-option {
		width: 100%;
		padding: 8px 10px;
		border: none;
		border-radius: 8px;
		background: transparent;
		display: grid;
		grid-template-columns: 24px 44px 1fr;
		align-items: center;
		text-align: left;
		cursor: pointer;
		color: var(--color-text-body, #1e293b);
		font-family: inherit;
		font-size: 13.5px;
		transition: background 0.12s ease;
	}

	.country-option:hover {
		background: #f1f5eb;
	}

	.country-option.selected {
		background: rgba(17, 98, 64, 0.08);
		font-weight: 600;
		color: var(--color-brand-primary, #116240);
	}

	.option-flag {
		font-size: 16px;
		line-height: 1;
	}

	.option-code {
		font-weight: 600;
		font-size: 13px;
		color: var(--color-text-secondary, #475569);
	}

	.option-name {
		font-size: 13px;
		color: inherit;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.no-country {
		padding: 16px;
		text-align: center;
		color: var(--color-text-muted, #64748b);
		font-size: 13px;
	}

	/* LOCAL PHONE INPUT */
	.phone-field {
		flex: 1;
		width: auto;
		min-width: 0;
		height: 100%;
		padding: 0 16px;
		border: none;
		border-radius: 0 12px 12px 0;
		background: transparent;
		box-shadow: none;
		outline: none;
		font-family: inherit;
		font-size: 15px;
		color: var(--color-text-body, #1e293b);
		box-sizing: border-box;
	}

	.phone-field::placeholder {
		color: #94a3b8;
	}
</style>
