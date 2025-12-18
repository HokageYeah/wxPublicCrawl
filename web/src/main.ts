import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

// Import global styles
import './assets/main.css'

// Import UnoCSS
import 'uno.css'

const app = createApp(App)

// Use Pinia for state management
app.use(createPinia())

app.mount('#app') 