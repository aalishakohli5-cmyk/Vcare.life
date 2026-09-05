<script>
	/**
	 * @typedef {Object} Props
	 * @property {'success' | 'warning' | 'alert' | 'danger' | 'distress' | 'neutral' | 'info' | 'normal'} [variant]
	 * @property {'sm' | 'md'} [size]
	 * @property {boolean} [dot]
	 * @property {import('svelte').Snippet} [children]
	 * @property {string} [class]
	 */

	let {
		variant = 'neutral',
		size = 'sm',
		dot = false,
		children,
		class: className = ''
	} = $props();

	// Normalize semantic aliases
	let normalizedVariant = $derived(
		variant === 'normal'
			? 'success'
			: variant === 'distress' || variant === 'danger'
				? 'alert'
				: variant
	);
</script>

<span class="badge badge-{normalizedVariant} badge-{size} {className}">
	{#if dot}
		<span class="badge-dot" aria-hidden="true"></span>
	{/if}
	{#if children}
		{@render children()}
	{/if}
</span>

<style>
	.badge {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-family: var(--font-body, 'Public Sans', sans-serif);
		font-weight: 600;
		line-height: 1;
		border-radius: var(--radius-full, 9999px);
		white-space: nowrap;
		letter-spacing: 0.02em;
	}

	.badge-sm {
		padding: 4px 9px;
		font-size: 11px;
	}

	.badge-md {
		padding: 6px 12px;
		font-size: 13px;
	}

	.badge-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	/* Semantic variants with WCAG AA contrast (solid readable text on soft tinted background with crisp border) */
	.badge-success {
		background: var(--color-success-bg, #e8f7ee);
		color: var(--color-success-text, #0f6e3c);
		border: 1px solid var(--color-success-border, #b7e8ca);
	}
	.badge-success .badge-dot {
		background: var(--color-success-icon, #15803d);
	}

	.badge-warning {
		background: var(--color-warning-bg, #fef4e2);
		color: var(--color-warning-text, #92400e);
		border: 1px solid var(--color-warning-border, #fbd38d);
	}
	.badge-warning .badge-dot {
		background: var(--color-warning-icon, #b45309);
	}

	.badge-alert {
		background: var(--color-danger-bg, #fdf0f0);
		color: var(--color-danger-text, #b91c1c);
		border: 1px solid var(--color-danger-border, #fecaca);
	}
	.badge-alert .badge-dot {
		background: var(--color-danger-icon, #dc2626);
	}

	.badge-neutral {
		background: var(--color-neutral-bg, #f1f4f2);
		color: var(--color-neutral-text, #334e44);
		border: 1px solid var(--color-neutral-border, #d5ded9);
	}
	.badge-neutral .badge-dot {
		background: #527568;
	}

	.badge-info {
		background: var(--color-info-bg, #e0f2fe);
		color: var(--color-info-text, #0369a1);
		border: 1px solid var(--color-info-border, #bae6fd);
	}
	.badge-info .badge-dot {
		background: #0284c7;
	}
</style>
