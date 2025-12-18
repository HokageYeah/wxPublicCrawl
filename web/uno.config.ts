import { defineConfig, presetUno, presetIcons, presetTypography } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetIcons({
      scale: 1.2,
      cdn: 'https://esm.sh/'
    }),
    presetTypography(),
  ],
  shortcuts: {
    'btn': 'py-2 px-4 font-semibold rounded-lg shadow-md transition-colors duration-200',
    'btn-primary': 'btn bg-primary hover:bg-primary/90 text-white',
    'btn-secondary': 'btn bg-surface hover:bg-surface/90 text-white',
    'input-field': 'p-2 border border-gray-600 rounded-lg bg-surface text-white w-full focus:outline-none focus:ring-2 focus:ring-primary',
    'card': 'bg-surface p-6 rounded-xl shadow-lg',
  }
}) 