<script>
	/**
	 * @typedef {Object} Props
	 * @property {string} label
	 * @property {string | number} value
	 * @property {string | import('svelte').Snippet} [icon]
	 * @property {'total' | 'taken' | 'success' | 'pending' | 'warning' | 'distress' | 'danger' | 'alert' | 'sentiment' | 'latest' | 'neutral'} [variant]
	 * @property {string} [subtext]
	 * @property {string} [class]
	 */

	let {
		label,
		value,
		icon,
		variant = 'neutral',
		subtext = '',
		class: className = ''
	} = $props();

	let normalizedVariant = $derived(
		variant === 'taken' || variant === 'sentiment'
			? 'success'
			: variant === 'pending'
				? 'warning'
				: variant === 'distress' || variant === 'danger'
					? 'alert'
					: variant === 'latest'
						? 'neutral'
						: variant
	);
</script>

<div class="metric-card metric-{normalizedVariant} {className}">
	{#if icon}
		<div class="metric-icon metric-icon-{normalizedVariant}" aria-hidden="true">
			{#if typeof icon === 'string'}
				{icon}
			{:else}
				{@render icon()}
			{/if}
		</div>
	{/if}
	<div class="metric-body">
		<small class="metric-label">{label}</small>
		<strong class="metric-value">{value}</strong>
		{#if subtext}
			<span class="metric-subtext">{subtext}</span>
		{/if}
	</div>
</div>

<style>
	.metric-card {
		background: var(--color-surface, #ffffff);
		padding: 20px 22px;
		border-radius: var(--radius-lg, 18px);
		display: flex;
		align-items: center;
		gap: 16px;
		border: 1px solid var(--color-border, #e2e8e0);
		box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
		transition: transform 0.18s ease, box-shadow 0.18s ease;
	}

	.metric-card:hover {
		box-shadow: var(--shadow-md, 0 4px 14px rgba(23, 63, 49, 0.05));
	}

	.metric-icon {
		width: 48px;
		height: 48px;
		border-radius: var(--radius-md, 14px);
		display: grid;
		place-items: center;
		font-size: 20px;
		flex-shrink: 0;
	}

	/* Semantic Brand Mappings */
	.metric-icon-total {
		background: var(--color-success-bg, #e8f7ee);
		color: var(--color-brand-primary, #116240);
	}

	.metric-icon-success {
		background: var(--color-success-icon-bg, #dcfce7);
		color: var(--color-success-icon, #15803d);
	}

	.metric-icon-warning {
		background: var(--color-warning-icon-bg, #fef3c7);
		color: var(--color-warning-icon, #b45309);
	}

	.metric-icon-alert {
		background: var(--color-danger-icon-bg, #fee2e2);
		color: var(--color-danger-icon, #dc2626);
	}

	.metric-icon-neutral {
		background: var(--color-neutral-bg, #f1f4f2);
		color: var(--color-neutral-text, #334e44);
	}

	.metric-body {
		min-width: 0;
		display: flex;
		flex-direction: column;
	}

	.metric-label {
		display: block;
		font-size: 11px;
		font-weight: 700;
		color: var(--color-text-secondary, #475569);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	.metric-value {
		margin-top: 2px;
		font-size: 22px;
		font-weight: 700;
		color: var(--color-text-primary, #153d30);
		line-height: 1.15;
	}

	.metric-subtext {
		margin-top: 3px;
		font-size: 12px;
		color: var(--color-text-muted, #64748b);
	}
</style>
