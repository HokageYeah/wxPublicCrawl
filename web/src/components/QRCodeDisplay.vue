<template>
  <div class="card p-8 flex flex-col items-center justify-center">
    <div 
      class="relative w-64 h-64 rounded-lg overflow-hidden border-2 border-gray-700"
      :class="{ 'opacity-50': isExpired }"
    >
      <!-- QR Code image -->
      <img 
        v-if="isValidQrCode" 
        :src="qrCodeUrl" 
        alt="WeChat QR Code" 
        class="w-full h-full object-cover"
        @error="handleImageError"
      />
      
      <!-- Loading state -->
      <div v-else-if="!errorLoadingImage" class="w-full h-full bg-gray-800 flex items-center justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
      
      <!-- Image error state -->
      <div v-else class="w-full h-full bg-gray-800 flex items-center justify-center">
        <div class="text-center p-4">
          <div class="text-xl font-bold text-error mb-2">二维码加载失败</div>
          <button @click="refresh" class="btn-primary mt-2">重试</button>
        </div>
      </div>
      
      <!-- Expired overlay -->
      <div 
        v-if="isExpired" 
        class="absolute inset-0 bg-background/70 flex items-center justify-center"
      >
        <div class="text-center p-4">
          <div class="text-xl font-bold text-error mb-2">二维码已过期</div>
          <button @click="refresh" class="btn-primary mt-2">刷新</button>
        </div>
      </div>
    </div>
    
    <!-- Status text -->
    <div class="mt-4 text-center">
      <p class="text-lg" :class="statusTextClass">{{ statusText }}</p>
      <p v-if="errorMessage" class="text-error mt-2">{{ errorMessage }}</p>
    </div>

    <!-- Debug info (可选) -->
    <div v-if="errorLoadingImage" class="mt-4 p-2 bg-gray-800 rounded text-xs text-red-400">
      <p>图片加载失败，请重试</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { QRCodeStatus } from '@/types/wechat';

const props = defineProps<{
  qrCodeUrl: string;
  status: number;
  statusText: string;
  errorMessage?: string | null;
}>();

const emit = defineEmits<{
  (e: 'refresh'): void;
}>();

// 状态变量
const errorLoadingImage = ref(false);

// 监听URL变化，重置错误状态
watch(() => props.qrCodeUrl, () => {
  errorLoadingImage.value = false;
});

// 计算属性
const isValidQrCode = computed(() => {
  return !!props.qrCodeUrl && !errorLoadingImage.value;
});

const isExpired = computed(() => {
  return props.status === QRCodeStatus.EXPIRED;
});

const statusTextClass = computed(() => {
  switch (props.status) {
    case QRCodeStatus.WAITING:
      return 'text-secondary';
    case QRCodeStatus.SCANNED:
      return 'text-primary';
    case QRCodeStatus.CONFIRMED:
      return 'text-success';
    case QRCodeStatus.EXPIRED:
      return 'text-error';
    default:
      return 'text-secondary';
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