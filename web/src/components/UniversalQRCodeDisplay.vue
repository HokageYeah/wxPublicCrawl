<template>
  <div class="card p-8 flex flex-col items-center justify-center bg-gray-900 border border-gray-700 rounded-xl">
    <div
      class="relative w-64 h-64 rounded-lg overflow-hidden border-2 border-gray-700"
      :class="{ 'opacity-50': isExpired }"
    >
      <!-- QR Code image -->
      <img
        v-if="isValidQrCode"
        :src="qrCodeSource"
        :alt="title || 'QR Code'"
        class="w-full h-full object-cover"
        @error="handleImageError"
      />

      <!-- Loading state -->
      <div v-else-if="!errorLoadingImage" class="w-full h-full bg-gray-800 flex items-center justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-orange-500"></div>
      </div>

      <!-- Image error state -->
      <div v-else class="w-full h-full bg-gray-800 flex items-center justify-center">
        <div class="text-center p-4">
          <div class="text-xl font-bold text-red-400 mb-2">二维码加载失败</div>
          <button @click="refresh" class="btn-primary mt-2 bg-orange-500 hover:bg-orange-600">重试</button>
        </div>
      </div>

      <!-- Expired overlay -->
      <div
        v-if="isExpired"
        class="absolute inset-0 bg-black/70 flex items-center justify-center"
      >
        <div class="text-center p-4">
          <div class="text-xl font-bold text-red-400 mb-2">二维码已过期</div>
          <button @click="refresh" class="btn-primary bg-orange-500 hover:bg-orange-600">刷新</button>
        </div>
      </div>
    </div>

    <!-- Status text -->
    <div class="mt-4 text-center">
      <p class="text-lg" :class="statusTextClass">{{ statusText }}</p>
      <p v-if="errorMessage" class="text-red-400 mt-2 text-sm">{{ errorMessage }}</p>
    </div>

    <!-- Debug info (可选) -->
    <div v-if="errorLoadingImage" class="mt-4 p-2 bg-gray-800 rounded text-xs text-red-400 border border-red-900">
      <p>图片加载失败，请重试</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';

const props = defineProps<{
  qrCodeUrl?: string;      // Blob URL格式（微信用）
  qrCodeImg?: string;      // Base64格式（喜马拉雅用）
  status: number;
  statusText: string;
  errorMessage?: string | null;
  pollingCount?: number;
  maxPollingCount?: number;
  title?: string;
}>();

const emit = defineEmits<{
  (e: 'refresh'): void;
}>();

// 状态变量
const errorLoadingImage = ref(false);

// 监听URL变化，重置错误状态
watch(() => props.qrCodeUrl || props.qrCodeImg, () => {
  errorLoadingImage.value = false;
});

// 计算属性
const isValidQrCode = computed(() => {
  return (props.qrCodeUrl || props.qrCodeImg) && !errorLoadingImage.value;
});

const qrCodeSource = computed(() => {
  // 优先使用base64，如果没有则使用Blob URL
  return props.qrCodeImg || props.qrCodeUrl || '';
});

const isExpired = computed(() => {
  return props.status === 3; // EXPIRED状态
});

const statusTextClass = computed(() => {
  switch (props.status) {
    case 0: // WAITING
      return 'text-gray-300';
    case 1: // SCANNED
      return 'text-orange-500';
    case 2: // CONFIRMED
      return 'text-green-400';
    case 3: // EXPIRED
      return 'text-red-400';
    default:
      return 'text-gray-300';
  }
});

// 方法
const handleImageError = (e: Event) => {
  console.error('QR code image failed to load:', e);
  errorLoadingImage.value = true;
};

const refresh = () => {
  errorLoadingImage.value = false;
  emit('refresh');
};
</script>
