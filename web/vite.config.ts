import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import { fileURLToPath, URL } from 'node:url'



export default ({ command, mode }: ConfigEnv): UserConfigExport => {
    // console.log(`command: ${command}, mode: ${mode}`);  
    console.log('vite----command----', command);

    return defineConfig({
        plugins: [
          vue(),
          UnoCSS(),
        ],
        resolve: {
          alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
          }
        },
        server: {
          proxy: {
            '/web-api': {
              // target: 'http://localhost:8002',
              target: 'http://127.0.0.1:8002',
              changeOrigin: true,
              rewrite: (path) => path.replace(/^\/web-api/, '')
            }
          }
        }
      }) 
  };

// https://vitejs.dev/config/
// export default defineConfig({
//   plugins: [
//     vue(),
//     UnoCSS(),
//   ],
//   resolve: {
//     alias: {
//       '@': fileURLToPath(new URL('./src', import.meta.url))
//     }
//   },
//   server: {
//     proxy: {
//       '/api': {
//         target: 'http://localhost:8002',
//         changeOrigin: true,
//         rewrite: (path) => path.replace(/^\/api/, '')
//       }
//     }
//   }
// }) 