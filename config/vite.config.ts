import { defineConfig } from 'vite'

import { sveltekit } from '@sveltejs/kit/vite'
import UnoCSS        from 'unocss/vite'

// https://vite.dev/config
export default defineConfig({
	plugins: [
	  UnoCSS({ configFile: 'config/uno.config.ts' }),
    sveltekit()
  ]
})
