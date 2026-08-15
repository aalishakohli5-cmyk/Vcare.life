import * as uno from 'unocss'

// https://unocss.dev/guide/config-file
export default uno.defineConfig({
  presets: [
    uno.presetWind3(),
    uno.presetMini(),
    uno.presetAttributify(),
    uno.presetIcons({
      prefix: String(/*empty*/),
      extraProperties: {
        'display'				 : 'inline-block',
        'vertical-align' : 'center'
      }
    })
  ],
  transformers: [
    uno.transformerDirectives(),
    uno.transformerVariantGroup()
  ]
})
