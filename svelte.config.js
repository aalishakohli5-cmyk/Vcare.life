import adapter from '@sveltejs/adapter-vercel'
import * as vite from '@sveltejs/vite-plugin-svelte'

// https://svelte.dev/docs/kit/configuration
/** @type {import('@sveltejs/kit').Config} */
export default {
  preprocess: vite.vitePreprocess(),
  compilerOptions: {
    runes: ({ filename }) =>
      filename.split(/[\/\\]/).includes('node_modules') ? undefined : true
  },
  kit: {
    adapter: adapter({
      runtime: 'nodejs20.x'
    }),
    alias: {
      "$asset": "src/lib/assets",
      "$component": "src/lib/components"
    }
  }
}
