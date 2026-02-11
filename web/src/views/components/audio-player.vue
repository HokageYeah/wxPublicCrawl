<template>
  <div
    v-show="showPlayer"
    class="fixed bottom-0 left-0 right-0 bg-[#141414]/95 backdrop-blur-xl border-t border-white/5 shadow-2xl z-50 transition-all duration-300"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center gap-4 py-3">
        <!-- 音频信息 -->
        <div class="flex items-center gap-3 min-w-0 max-w-[30%]">
          <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-500/20 to-orange-600/10 flex items-center justify-center flex-shrink-0">
            <span v-if="currentTrack?.coverSmall" class="w-full h-full rounded-lg overflow-hidden">
              <img :src="currentTrack?.coverSmall" :alt="currentTrack?.title" class="w-full h-full object-cover" />
            </span>
            <span v-else class="i-carbon-music text-2xl text-orange-500"></span>
          </div>
          <div class="min-w-0">
            <h3 class="text-white font-medium truncate text-sm">{{ currentTrack?.title || "未播放" }}</h3>
            <p class="text-gray-500 text-xs truncate">{{ currentTrack?.albumTitle || "未知专辑" }}</p>
          </div>
        </div>

        <!-- 控制按钮 -->
        <div class="flex items-center gap-3 flex-shrink-0">
          <!-- 上一首 -->
          <button
            @click="handlePrevTrack"
            class="w-10 h-10 flex items-center justify-center rounded-full bg-[#1f1f1f] text-gray-400 hover:text-white hover:bg-[#2a2a2a] transition-all"
            title="上一首"
          >
            <span class="i-carbon-skip-back-filled text-lg"></span>
          </button>

          <!-- 停止 -->
          <button
            @click="stop"
            class="w-10 h-10 flex items-center justify-center rounded-full bg-[#1f1f1f] text-gray-400 hover:text-white hover:bg-[#2a2a2a] transition-all"
            title="停止"
          >
            <span class="i-carbon-stop-filled text-lg"></span>
          </button>

          <!-- 播放/暂停 -->
          <button
            @click="togglePlay"
            class="w-14 h-14 flex items-center justify-center rounded-full bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 text-white shadow-lg shadow-orange-900/30 transition-all hover:scale-105"
            :title="isPlaying ? '暂停' : '播放'"
          >
            <span v-if="isPlaying" class="i-carbon-pause-filled text-2xl"></span>
            <span v-else class="i-carbon-play-filled text-2xl ml-1"></span>
          </button>

          <!-- 下一首 -->
          <button
            @click="handleNextTrack"
            class="w-10 h-10 flex items-center justify-center rounded-full bg-[#1f1f1f] text-gray-400 hover:text-white hover:bg-[#2a2a2a] transition-all"
            title="下一首"
          >
            <span class="i-carbon-skip-forward-filled text-lg"></span>
          </button>

          <!-- 小的快退/快进按钮组 -->
          <div class="flex items-center gap-1.5 ml-2">
            <!-- 快退10秒（小按钮） -->
            <button
              @click="seek(-10)"
              class="flex flex-col items-center justify-center w-6 h-6 rounded-full bg-[#1f1f1f] text-gray-500 hover:text-orange-400 hover:bg-[#2a2a2a] transition-all duration-200 border border-white/5 hover:border-orange-500/30"
              title="快退10秒"
            >
              <span class="i-carbon-rewind text-xs leading-none mb-0.5"></span>
              <span class="text-[8px] font-medium leading-none">-10s</span>
            </button>
            <!-- 快进10秒（小按钮） -->
            <button
              @click="seek(10)"
              class="flex flex-col items-center justify-center w-6 h-6 rounded-full bg-[#1f1f1f] text-gray-500 hover:text-orange-400 hover:bg-[#2a2a2a] transition-all duration-200 border border-white/5 hover:border-orange-500/30"
              title="快进10秒"
            >
              <span class="i-carbon-forward text-xs leading-none mb-0.5"></span>
              <span class="text-[8px] font-medium leading-none">+10s</span>
            </button>
          </div>

          <!-- 音量控制 -->
          <div class="flex items-center gap-2 ml-2">
            <button
              @click="toggleMute"
              class="w-8 h-8 flex items-center justify-center rounded-full text-gray-400 hover:text-white transition-all"
              :title="isMuted ? '取消静音' : '静音'"
            >
              <span v-if="isMuted || volume === 0" class="i-carbon-volume-muted-filled text-lg"></span>
              <span v-else-if="volume < 0.5" class="i-carbon-volume-low-filled text-lg"></span>
              <span v-else class="i-carbon-volume-high-filled text-lg"></span>
            </button>
            <input
              v-model="volume"
              type="range"
              min="0"
              max="1"
              step="0.01"
              class="w-20 h-1 bg-[#2a2a2a] rounded-lg appearance-none cursor-pointer accent-orange-500"
              @input="handleVolumeChange"
            />
          </div>
        </div>

        <!-- 进度条 -->
        <div class="flex-1 min-w-0 flex items-center gap-3">
          <span class="text-xs text-gray-400 min-w-[40px] text-right">{{ formatTime(currentTime) }}</span>
          <div
            ref="progressBar"
            class="flex-1 h-1.5 bg-[#2a2a2a] rounded-full cursor-pointer group relative overflow-hidden"
            @click="handleProgressClick"
          >
            <!-- 缓冲进度 -->
            <div
              class="absolute top-0 left-0 h-full bg-gray-600/30 transition-all duration-300"
              :style="{ width: bufferedPercentage + '%' }"
            ></div>
            <!-- 播放进度 -->
            <div
              class="absolute top-0 left-0 h-full bg-gradient-to-r from-orange-600 to-orange-500 rounded-full transition-all duration-100 ease-linear"
              :style="{ width: progressPercentage + '%' }"
            ></div>
            <!-- 进度指示器（悬停时显示） -->
            <div
              class="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
              :style="{ left: `calc(${progressPercentage}% - 6px)` }"
            ></div>
          </div>
          <span class="text-xs text-gray-400 min-w-[40px]">{{ formatTime(duration) }}</span>
        </div>

        <!-- 质量选择 -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <select
            v-model="selectedQuality"
            @change="handleQualityChange"
            class="bg-[#1f1f1f] border border-white/10 text-gray-300 text-xs rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-orange-500 focus:border-orange-500 cursor-pointer"
          >
            <option value="high" v-if="currentTrack?.playUrls?.high">高品质</option>
            <option value="medium" v-if="currentTrack?.playUrls?.medium">中品质</option>
            <option value="low" v-if="currentTrack?.playUrls?.low">低品质</option>
          </select>
        </div>

        <!-- 关闭按钮 -->
        <button
          @click="close"
          class="w-8 h-8 flex items-center justify-center rounded-full text-gray-400 hover:text-white hover:bg-[#2a2a2a] transition-all flex-shrink-0"
          title="关闭播放器"
        >
          <span class="i-carbon-close text-lg"></span>
        </button>
      </div>
    </div>

    <!-- 隐藏的音频元素 -->
    <audio
      ref="audioElement"
      @timeupdate="handleTimeUpdate"
      @loadedmetadata="handleLoadedMetadata"
      @ended="handleEnded"
      @progress="handleProgress"
    ></audio>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onUnmounted } from "vue";

// 类型定义
interface PlayUrls {
  high: string;
  medium: string;
  low: string;
}

interface CurrentTrack {
  trackId: string;
  title: string;
  intro: string;
  coverSmall: string;
  albumTitle?: string;
  duration: number;
  playUrls: PlayUrls;
}

// Props
interface Props {
  show: boolean;
  track?: CurrentTrack;
  autoPlay?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
  track: undefined,
  autoPlay: true,
});

// Emits
const emit = defineEmits<{
  (e: "update:show", value: boolean): void;
  (e: "play"): void;
  (e: "pause"): void;
  (e: "ended"): void;
  (e: "error"): void;
  (e: "prev"): void;
  (e: "next"): void;
}>();

// 响应式数据
const audioElement = ref<HTMLAudioElement | null>(null);
const progressBar = ref<HTMLDivElement | null>(null);

const isPlaying = ref(false);
const isMuted = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(0.8);
const buffered = ref(0);
const selectedQuality = ref<"high" | "medium" | "low">("medium");
const currentTrack = ref<CurrentTrack | null>(null);

// 计算属性
const showPlayer = computed({
  get: () => props.show,
  set: (value) => emit("update:show", value),
});

const progressPercentage = computed(() => {
  if (duration.value === 0) return 0;
  return (currentTime.value / duration.value) * 100;
});

const bufferedPercentage = computed(() => {
  if (duration.value === 0) return 0;
  return (buffered.value / duration.value) * 100;
});

// 监听 track 变化
watch(
  () => props.track,
  (newTrack, oldTrack) => {
    if (newTrack && JSON.stringify(newTrack) !== JSON.stringify(oldTrack)) {
      // 先停止当前播放
      if (isPlaying.value) {
        stop();
      }
      // 更新当前曲目
      currentTrack.value = { ...newTrack };
      // 等待DOM更新后再加载音频
      nextTick(() => {
        loadTrack();
      });
    }
  },
  { immediate: false }
);

// 加载音频
const loadTrack = async () => {
  if (!props.track || !audioElement.value) return;

  try {
    // 根据选择的音质获取URL
    let playUrl = "";
    if (selectedQuality.value === "high" && props.track.playUrls.high) {
      playUrl = props.track.playUrls.high;
    } else if (selectedQuality.value === "medium" && props.track.playUrls.medium) {
      playUrl = props.track.playUrls.medium;
    } else if (selectedQuality.value === "low" && props.track.playUrls.low) {
      playUrl = props.track.playUrls.low;
    } else {
      // 如果选择的音质不可用，尝试其他音质
      playUrl = props.track.playUrls.medium || props.track.playUrls.low || props.track.playUrls.high || "";
    }

    if (!playUrl) {
      console.error("没有可用的播放链接");
      emit("error");
      return;
    }

    // 重置播放状态
    currentTime.value = 0;
    duration.value = 0;
    buffered.value = 0;

    audioElement.value.src = playUrl;
    await audioElement.value.load();

    if (props.autoPlay) {
      await nextTick();
      play();
    }
  } catch (error) {
    console.error("加载音频失败:", error);
    emit("error");
  }
};

// 播放/暂停切换
const togglePlay = () => {
  if (isPlaying.value) {
    pause();
  } else {
    play();
  }
};

// 播放
const play = async () => {
  if (!audioElement.value) return;
  try {
    await audioElement.value.play();
    isPlaying.value = true;
    emit("play");
  } catch (error) {
    console.error("播放失败:", error);
    emit("error");
  }
};

// 暂停
const pause = () => {
  if (!audioElement.value) return;
  audioElement.value.pause();
  isPlaying.value = false;
  emit("pause");
};

// 停止
const stop = () => {
  if (!audioElement.value) return;
  pause();
  currentTime.value = 0;
  audioElement.value.currentTime = 0;
};

// 快进/快退
const seek = (seconds: number) => {
  if (!audioElement.value) return;
  const newTime = currentTime.value + seconds;
  audioElement.value.currentTime = Math.max(0, Math.min(newTime, duration.value));
};

// 上一首
const handlePrevTrack = () => {
  emit("prev");
};

// 下一首
const handleNextTrack = () => {
  emit("next");
};

// 切换静音
const toggleMute = () => {
  if (!audioElement.value) return;
  isMuted.value = !isMuted.value;
  audioElement.value.muted = isMuted.value;
};

// 音量变化
const handleVolumeChange = () => {
  if (!audioElement.value) return;
  audioElement.value.volume = volume.value;
  if (volume.value === 0) {
    isMuted.value = true;
    audioElement.value.muted = true;
  } else {
    isMuted.value = false;
    audioElement.value.muted = false;
  }
};

// 进度条点击
const handleProgressClick = (event: MouseEvent) => {
  if (!progressBar.value || !audioElement.value) return;
  const rect = progressBar.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const percentage = x / rect.width;
  audioElement.value.currentTime = percentage * duration.value;
};

// 时间更新
const handleTimeUpdate = () => {
  if (!audioElement.value) return;
  currentTime.value = audioElement.value.currentTime;
};

// 加载元数据
const handleLoadedMetadata = () => {
  if (!audioElement.value) return;
  duration.value = audioElement.value.duration;
};

// 缓冲进度
const handleProgress = () => {
  if (!audioElement.value) return;
  if (audioElement.value.buffered.length > 0) {
    buffered.value = audioElement.value.buffered.end(audioElement.value.buffered.length - 1);
  }
};

// 播放结束
const handleEnded = () => {
  isPlaying.value = false;
  currentTime.value = 0;
  emit("ended");
};

// 音质切换
const handleQualityChange = () => {
  if (isPlaying.value) {
    loadTrack();
  }
};

// 关闭播放器
const close = () => {
  stop();
  showPlayer.value = false;
  currentTrack.value = null;
};

// 格式化时间
const formatTime = (seconds: number): string => {
  if (isNaN(seconds) || seconds < 0) return "00:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
};

// 暴露方法
defineExpose({
  play,
  pause,
  stop,
  seek,
  togglePlay,
});

// 组件卸载时清理
onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause();
    audioElement.value.src = "";
  }
});
</script>

<style scoped>
/* 自定义滑块样式 */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
}

input[type="range"]::-webkit-slider-runnable-track {
  height: 4px;
  background: #2a2a2a;
  border-radius: 2px;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  background: #f97316;
  border-radius: 50%;
  cursor: pointer;
  margin-top: -4px;
  transition: transform 0.15s;
}

input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

input[type="range"]::-moz-range-track {
  height: 4px;
  background: #2a2a2a;
  border-radius: 2px;
}

input[type="range"]::-moz-range-thumb {
  width: 12px;
  height: 12px;
  background: #f97316;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  transition: transform 0.15s;
}

input[type="range"]::-moz-range-thumb:hover {
  transform: scale(1.2);
}

/* 下拉选择样式 */
select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

select:focus {
  outline: none;
}
</style>
