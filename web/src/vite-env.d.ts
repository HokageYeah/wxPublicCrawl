/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  // 在这里添加更多的环境变量类型定义
  // readonly VITE_ANOTHER_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

