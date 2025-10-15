// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  
  // Compatibility Date
  compatibilityDate: '2025-10-14',

  // Disable automatic pages and layouts since we're using a single-page app
  pages: false,

  // CSS Framework
  css: ['~/assets/css/main.css'],
  
  // Modules
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxt/icon'
  ],
  
  // TypeScript Configuration
  typescript: {
    strict: false,
    typeCheck: false
  },
  
  // Runtime Config
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      wsUrl: process.env.NUXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
      appName: 'AL-Tech Academy Q&A',
      appVersion: '1.0.0'
    }
  },
  
  // App Configuration
  app: {
    head: {
      title: 'AL-Tech Academy Q&A System',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI-Powered Q&A System for AL-Tech Academy' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },
  
  
  // Build Configuration
  build: {
    transpile: ['vue-toastification']
  },
  
  // SSR Configuration
  ssr: true,
  
  // Nitro Configuration
  nitro: {
    experimental: {
      wasm: true
    }
  },

  // Vite Configuration
  vite: {
    define: {
      __VUE_OPTIONS_API__: true,
      __VUE_PROD_DEVTOOLS__: false
    }
  }
})
