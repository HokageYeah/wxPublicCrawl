import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import UnoCSS from 'unocss/vite'
import { fileURLToPath, URL } from 'node:url'



export default ({ command, mode }: ConfigEnv): UserConfigExport => {
    // console.log(`command: ${command}, mode: ${mode}`);  
    console.log('vite----command----', command);

    return defineConfig({
        base: '/crawl-desktop/', // 项目部署路径，如果部署到子路径下，需要设置为子路径
        plugins: [
          vue(),
          UnoCSS(),
        ],
        resolve: {
          // 设置别名，@ 代表 src 目录
          alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
          }
        },
        server: {
          // 设置代理，/web-api 代表接口前缀，target 代表接口地址，changeOrigin 代表是否改变源，rewrite 代表是否重写路径
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