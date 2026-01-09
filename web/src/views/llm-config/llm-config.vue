<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">LLM配置管理</h1>
      <p class="text-gray-600">管理AI大模型配置，支持多模型切换</p>
    </div>

    <!-- 测试UI内容 -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-center h-64 border-2 border-dashed border-gray-300 rounded-lg">
        <div class="text-center">
          <span class="i-carbon-settings text-6xl text-gray-400 mb-4 block"></span>
          <p class="text-gray-500">LLM配置管理页面</p>
          <p class="text-sm text-gray-400 mt-2">功能开发中...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

onMounted(() => {
  console.log('LLM配置管理页面已加载')
})
</script>

<style scoped>
</style>

