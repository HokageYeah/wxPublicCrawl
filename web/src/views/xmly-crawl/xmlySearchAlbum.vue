<template>
  <div class="min-h-screen bg-[#0a0a0a] text-gray-200 font-sans selection:bg-orange-500/30">
    <div class="max-w-4xl mx-auto px-6 py-12">
      <!-- Header -->
      <header class="mb-12 text-center relative">
        <div class="absolute inset-0 -z-10 bg-gradient-to-r from-orange-500/10 to-red-500/10 blur-3xl opacity-30 rounded-full transform scale-150"></div>
        <h1 class="text-4xl font-bold mb-4 text-white tracking-tight flex items-center justify-center gap-4">
          <span class="p-3 bg-white/5 rounded-2xl border border-white/10 shadow-2xl backdrop-blur-sm">
            <span class="i-carbon-microphone-filled text-orange-500 text-3xl block"></span>
          </span>
          喜马拉雅专辑订阅
        </h1>
        <p class="text-gray-500 text-lg">自动监控与下载管理系统</p>
      </header>

      <!-- Main Control Card -->
      <div class="bg-[#111] border border-gray-800 rounded-2xl p-1 shadow-2xl overflow-hidden mb-8 group hover:border-gray-700 transition-colors duration-300">
        <div class="bg-[#151515] rounded-xl p-8 relative overflow-hidden">
          <!-- Glass effect decoration -->
          <div class="absolute top-0 right-0 p-32 bg-orange-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

          <div class="grid md:grid-cols-2 gap-8 items-center relative z-10">
            <!-- Left Info -->
            <div>
              <label class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 block">
                Target Album ID
              </label>
              <div class="flex items-center gap-4 group/id">
                <span class="text-4xl font-mono font-bold text-white tracking-tight group-hover/id:text-orange-400 transition-colors">
                  {{ testAlbumId }}
                </span>
                <span v-if="loading" class="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-orange-400">
                  <span class="i-carbon-circle-dash animate-spin"></span>
                  Processing
                </span>
              </div>
            </div>

            <!-- Right Actions -->
            <div class="flex flex-col sm:flex-row gap-4 justify-end">
              <button
                @click="handleSubscribe"
                :disabled="loading"
                class="relative overflow-hidden group px-6 py-3 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 text-white font-medium shadow-lg hover:shadow-orange-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:-translate-y-0.5 active:translate-y-0"
              >
                <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                <div class="flex items-center gap-2 relative">
                  <span class="i-carbon-add-alt text-lg"></span>
                  <span>立即订阅</span>
                </div>
              </button>

              <button
                @click="handleUnsubscribe"
                :disabled="loading"
                class="px-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 hover:text-white font-medium transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2 hover:border-red-500/50 hover:text-red-400 group/del"
              >
                <span class="i-carbon-trash-can group-hover/del:scale-110 transition-transform"></span>
                取消订阅
              </button>
            </div>
          </div>

          <!-- Status Alert -->
          <transition
            enter-active-class="transition ease-out duration-200"
            enter-from-class="opacity-0 translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition ease-in duration-150"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 translate-y-2"
          >
            <div
              v-if="statusMessage"
              :class="[
                'mt-6 p-4 rounded-xl border flex items-center gap-3 backdrop-blur-md',
                statusMessage.type === 'success'
                  ? 'bg-green-500/10 border-green-500/20 text-green-400'
                  : 'bg-red-500/10 border-red-500/20 text-red-400',
              ]"
            >
              <div :class="[
                'p-1.5 rounded-full flex items-center justify-center',
                statusMessage.type === 'success' ? 'bg-green-500/20' : 'bg-red-500/20'
              ]">
                <span :class="statusMessage.type === 'success' ? 'i-carbon-checkmark' : 'i-carbon-warning'"></span>
              </div>
              <span class="font-medium text-sm">{{ statusMessage.text }}</span>
            </div>
          </transition>
        </div>
      </div>

      <!-- Terminal Log -->
      <div class="bg-[#0f0f0f] rounded-xl border border-gray-800 overflow-hidden shadow-2xl font-mono text-sm relative group">
        <!-- Terminal Header -->
        <div class="bg-[#1a1a1a] px-4 py-3 flex items-center justify-between border-b border-gray-800">
          <div class="flex items-center gap-2">
            <div class="flex gap-1.5">
              <div class="w-3 h-3 rounded-full bg-red-500/50"></div>
              <div class="w-3 h-3 rounded-full bg-yellow-500/50"></div>
              <div class="w-3 h-3 rounded-full bg-green-500/50"></div>
            </div>
            <span class="ml-3 text-gray-500 text-xs flex items-center gap-1">
              <span class="i-carbon-terminal"></span>
              Console Output
            </span>
          </div>
          <button
            @click="logs = []"
            class="text-xs text-gray-600 hover:text-gray-300 transition-colors flex items-center gap-1 hover:bg-white/5 px-2 py-1 rounded"
          >
            <span class="i-carbon-clean"></span> Clear
          </button>
        </div>

        <!-- Terminal Body -->
        <div class="p-4 h-80 overflow-y-auto bg-black/50 custom-scrollbar tracking-wide">
          <transition-group name="terminal">
            <div
              v-for="(log, index) in logs"
              :key="index"
              class="mb-1.5 last:mb-0 break-all flex items-start gap-3 hover:bg-white/5 p-1 rounded transition-colors group/log"
              :class="{
                'text-green-400': log.type === 'success',
                'text-red-400': log.type === 'error',
                'text-gray-400': log.type === 'info',
              }"
            >
              <span class="opacity-30 select-none w-20 text-xs mt-0.5 shrink-0 text-right font-light">{{ log.time }}</span>
              <span class="opacity-50 select-none mt-0.5">❯</span>
              <span class="group-hover/log:opacity-100 opacity-90 transition-opacity">{{ log.msg }}</span>
            </div>
          </transition-group>

          <div v-if="logs.length === 0" class="h-full flex flex-col items-center justify-center text-gray-800">
            <div class="i-carbon-terminal text-4xl mb-2 opacity-20"></div>
            <p class="text-xs uppercase tracking-widest opacity-30">Ready for connection</p>
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
  const now = new Date();
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
  logs.value.unshift({ time, msg, type });
};

// 订阅操作
const handleSubscribe = async () => {
  try {
    loading.value = true;
    statusMessage.value = null;
    addLog(`Initiating subscription for album: ${testAlbumId}...`, "info");

    const res = await xmlyService.subscribe(testAlbumId);

    // 检查返回结果
    if (res.ret === 200 || res.code === 0) {
      statusMessage.value = { type: "success", text: "Subscription activated successfully" };
      addLog(`Success: ${JSON.stringify(res)}`, "success");
    } else {
      statusMessage.value = {
        type: "error",
        text: res.msg || "Operation returned abnormal status",
      };
      addLog(`Error: ${JSON.stringify(res)}`, "error");
    }
  } catch (error: any) {
    console.error(error);
    statusMessage.value = { type: "error", text: error.message || "Connection failed" };
    addLog(`Exception: ${error.message}`, "error");
  } finally {
    loading.value = false;
  }
};

// 取消订阅操作
const handleUnsubscribe = async () => {
  try {
    loading.value = true;
    statusMessage.value = null;
    addLog(`Requesting unsubscription for album: ${testAlbumId}...`, "info");

    const res = await xmlyService.unsubscribe(testAlbumId);

    if (res.ret === 200 || res.code === 0) {
      statusMessage.value = { type: "success", text: "Subscription cancelled successfully" };
      addLog(`Success: ${JSON.stringify(res)}`, "success");
    } else {
      statusMessage.value = {
        type: "error",
        text: res.msg || "Operation returned abnormal status",
      };
      addLog(`Error: ${JSON.stringify(res)}`, "error");
    }
  } catch (error: any) {
    console.error(error);
    statusMessage.value = {
      type: "error",
      text: error.message || "Cancellation failed",
    };
    addLog(`Exception: ${error.message}`, "error");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Scrollbar Styling */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.3);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Terminal Animations */
.terminal-enter-active,
.terminal-leave-active {
  transition: all 0.3s ease;
}
.terminal-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}
.terminal-leave-to {
  opacity: 0;
}
</style>
