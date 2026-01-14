<template>
  <div class="min-h-screen bg-black dark:bg-gray-900 text-gray-200 p-6">
    <div class="max-w-3xl mx-auto">
      <!-- 标题区域 -->
      <h1
        class="text-3xl font-bold mb-8 text-center text-white flex items-center justify-center"
      >
        <span class="i-carbon-search text-orange-500 mr-3"></span>
        喜马拉雅专辑订阅测试
      </h1>

      <!-- 主要操作卡片 -->
      <div
        class="bg-gray-900 border border-gray-700 rounded-xl p-8 mb-6 shadow-lg"
      >
        <div
          class="flex flex-col md:flex-row items-center justify-between gap-6"
        >
          <!-- 信息展示 -->
          <div class="flex items-center">
            <div class="mr-4 p-3 bg-gray-800 rounded-lg border border-gray-700">
              <span class="text-gray-400 text-sm block mb-1">测试专辑ID</span>
              <span class="text-xl font-mono text-orange-400 font-bold">{{
                testAlbumId
              }}</span>
            </div>
            <div v-if="loading" class="text-gray-400 flex items-center">
              <span
                class="i-carbon-circle-dash animate-spin mr-2 text-xl"
              ></span>
              <span>处理中...</span>
            </div>
          </div>

          <!-- 按钮组 -->
          <div class="flex gap-4">
            <button
              @click="handleSubscribe"
              :disabled="loading"
              class="px-6 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center bg-orange-600 hover:bg-orange-700 text-white disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              <span class="i-carbon-add-alt mr-2"></span>
              订阅专辑
            </button>

            <button
              @click="handleUnsubscribe"
              :disabled="loading"
              class="px-6 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center bg-red-600 hover:bg-red-700 text-white disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-gray-900"
            >
              <span class="i-carbon-trash-can mr-2"></span>
              取消订阅
            </button>
          </div>
        </div>

        <!-- 状态消息提示 -->
        <div
          v-if="statusMessage"
          :class="[
            'mt-6 p-4 rounded-lg flex items-center border',
            statusMessage.type === 'success'
              ? 'bg-green-900/30 border-green-700 text-green-400'
              : 'bg-red-900/30 border-red-700 text-red-400',
          ]"
        >
          <span
            :class="
              statusMessage.type === 'success'
                ? 'i-carbon-checkmark-filled'
                : 'i-carbon-warning-filled'
            "
            class="text-xl mr-3"
          ></span>
          <span class="font-medium">{{ statusMessage.text }}</span>
        </div>
      </div>

      <!-- 日志区域 -->
      <div
        class="bg-gray-900 border border-gray-700 rounded-xl overflow-hidden"
      >
        <div
          class="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between"
        >
          <h3 class="font-semibold text-gray-300 flex items-center">
            <span class="i-carbon-terminal mr-2"></span>
            操作日志
          </h3>
          <button
            @click="logs = []"
            class="text-xs text-gray-500 hover:text-white transition-colors"
          >
            清除日志
          </button>
        </div>

        <div class="p-4 h-64 overflow-y-auto font-mono text-sm bg-black/50">
          <transition-group name="list">
            <div
              v-for="(log, index) in logs"
              :key="index"
              class="mb-2 last:mb-0 break-all p-2 rounded hover:bg-white/5 transition-colors"
              :class="{
                'text-green-400': log.type === 'success',
                'text-red-400': log.type === 'error',
                'text-gray-400': log.type === 'info',
              }"
            >
              <span class="opacity-50 text-xs mr-2">[{{ log.time }}]</span>
              <span>{{ log.msg }}</span>
            </div>
          </transition-group>

          <div v-if="logs.length === 0" class="text-gray-600 text-center py-10">
            暂无日志记录
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { xmlyService } from "@/services/xmlyService";

// 状态定义
const loading = ref(false);
const testAlbumId = "31378010";
const logs = ref<
  Array<{ time: string; msg: string; type: "info" | "success" | "error" }>
>([]);
const statusMessage = ref<{ type: "success" | "error"; text: string } | null>(
  null
);

// 添加日志
const addLog = (msg: string, type: "info" | "success" | "error" = "info") => {
  const time = new Date().toLocaleTimeString();
  logs.value.unshift({ time, msg, type });
};

// 订阅操作
const handleSubscribe = async () => {
  try {
    loading.value = true;
    statusMessage.value = null;
    addLog(`正在订阅专辑: ${testAlbumId}...`, "info");

    const res = await xmlyService.subscribe(testAlbumId);

    // 检查返回结果
    if (res.ret === 200 || res.code === 0) {
      statusMessage.value = { type: "success", text: "订阅成功" };
      addLog(`订阅成功: ${JSON.stringify(res)}`, "success");
    } else {
      statusMessage.value = {
        type: "error",
        text: res.msg || "订阅操作返回异常",
      };
      addLog(`订阅返回非成功状态: ${JSON.stringify(res)}`, "error");
    }
  } catch (error: any) {
    console.error(error);
    statusMessage.value = { type: "error", text: error.message || "订阅失败" };
    addLog(`订阅失败: ${error.message}`, "error");
  } finally {
    loading.value = false;
  }
};

// 取消订阅操作
const handleUnsubscribe = async () => {
  try {
    loading.value = true;
    statusMessage.value = null;
    addLog(`正在取消订阅专辑: ${testAlbumId}...`, "info");

    const res = await xmlyService.unsubscribe(testAlbumId);

    if (res.ret === 200 || res.code === 0) {
      statusMessage.value = { type: "success", text: "取消订阅成功" };
      addLog(`取消订阅成功: ${JSON.stringify(res)}`, "success");
    } else {
      statusMessage.value = {
        type: "error",
        text: res.msg || "取消订阅操作返回异常",
      };
      addLog(`取消订阅返回非成功状态: ${JSON.stringify(res)}`, "error");
    }
  } catch (error: any) {
    console.error(error);
    statusMessage.value = {
      type: "error",
      text: error.message || "取消订阅失败",
    };
    addLog(`取消订阅失败: ${error.message}`, "error");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 简单的列表过渡动画 */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
