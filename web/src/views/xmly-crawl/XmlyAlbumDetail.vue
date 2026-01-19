<template>
  <div
    class="min-h-screen bg-[#0a0a0a] text-gray-200 font-sans selection:bg-orange-500/30"
  >
    <!-- Breadcrumb -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <nav class="flex text-sm font-medium text-gray-500 items-center">
        <router-link
          to="/xmly-crawl/search-album"
          class="hover:text-orange-500 transition-colors flex items-center gap-1"
        >
          <span class="i-carbon-home"></span>
          首页
        </router-link>
        <span class="mx-3 text-gray-700">/</span>
        <span
          v-if="albumData?.albumPageMainInfo?.categoryTitle"
          class="hover:text-gray-300 transition-colors cursor-pointer"
        >
          {{ albumData.albumPageMainInfo.categoryTitle }}
        </span>
        <span
          v-if="albumData?.albumPageMainInfo?.categoryTitle"
          class="mx-3 text-gray-700"
          >/</span
        >
        <span class="text-gray-200 truncate max-w-xs">{{
          albumData?.albumPageMainInfo?.albumTitle || "专辑详情"
        }}</span>
      </nav>
    </div>

    <!-- 下载路径设置 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:8 pb-4">
      <div class="bg-[#141414] rounded-2xl border border-white/5 p-4">
        <div
          class="flex flex-col sm:flex-row items-start sm:items-center gap-4"
        >
          <div class="flex items-center gap-2 text-sm">
            <span class="i-carbon-download text-orange-500 text-lg"></span>
            <span class="text-gray-300 font-medium">下载路径:</span>
          </div>
          <div class="flex-1 w-full sm:w-auto">
            <div class="relative">
              <input
                v-model="downloadPath"
                type="text"
                class="w-full bg-[#1f1f1f] border border-white/10 text-gray-200 text-sm rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 px-4 py-2.5 pr-24 transition-all placeholder-gray-500"
                placeholder="请选择或输入下载保存路径"
              />
              <button
                @click="selectDownloadFolder"
                :disabled="loadingDownloadPath"
                class="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-orange-500/10 text-orange-400 hover:bg-orange-500 hover:text-white border border-orange-500/20 rounded-md text-xs font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
              >
                <span
                  v-if="loadingDownloadPath"
                  class="i-carbon-circle-dash animate-spin"
                ></span>
                <span v-else>选择文件夹</span>
              </button>
            </div>
          </div>
        </div>
        <div
          v-if="!downloadPath"
          class="mt-3 flex items-start gap-2 text-xs text-amber-500 bg-amber-500/5 border border-amber-500/10 rounded-lg px-3 py-2"
        >
          <span class="i-carbon-warning-filled mt-0.5 flex-shrink-0"></span>
          <p>请先设置下载路径，否则无法使用下载功能。</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
      <!-- Loading State -->
      <div
        v-if="loading"
        class="flex flex-col justify-center items-center h-96"
      >
        <div
          class="w-16 h-16 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin mb-6"
        ></div>
        <p class="text-gray-500 animate-pulse tracking-wider text-sm">
          正在加载精彩内容...
        </p>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="flex flex-col justify-center items-center h-96 text-center"
      >
        <span class="i-carbon-warning-alt text-6xl text-red-500/50 mb-6"></span>
        <p class="text-gray-400 mb-6 max-w-md">{{ error }}</p>
        <button
          @click="fetchAlbumDetail"
          class="px-8 py-2.5 bg-orange-600 hover:bg-orange-500 text-white rounded-full transition-all shadow-lg shadow-orange-900/40 font-medium"
        >
          重试
        </button>
      </div>

      <div v-else-if="albumData" class="animate-fade-in">
        <!-- Top Section: Header Info -->
        <div
          class="bg-[#141414] rounded-3xl border border-white/5 p-6 md:p-8 shadow-2xl relative overflow-hidden backdrop-blur-sm"
        >
          <!-- Background Decoration -->
          <div
            class="absolute top-0 right-0 w-[500px] h-[500px] bg-orange-500/5 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/4 pointer-events-none"
          ></div>

          <div class="flex flex-col md:flex-row gap-8 md:gap-12 relative z-10">
            <!-- Left: Cover (Vinyl Style) -->
            <div
              class="flex-shrink-0 relative group perspective-1000 mx-auto md:mx-0"
            >
              <div
                class="w-64 h-64 md:w-72 md:h-72 relative transition-transform duration-500 group-hover:rotate-y-6 group-hover:scale-105 z-20"
              >
                <img
                  :src="albumData.albumPageMainInfo.cover"
                  :alt="albumData.albumPageMainInfo.albumTitle"
                  class="w-full h-full object-cover rounded-xl shadow-2xl border border-white/10"
                  referrerpolicy="no-referrer"
                />
                <!-- Shine Effect -->
                <div
                  class="absolute inset-0 bg-gradient-to-tr from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-xl pointer-events-none"
                ></div>
              </div>
              <!-- Vinyl Disc Behind -->
              <div
                class="absolute top-4 right-4 w-60 h-60 md:w-68 md:h-68 bg-[#111] rounded-full flex items-center justify-center z-10 shadow-2xl transition-all duration-700 ease-out group-hover:translate-x-16 group-hover:rotate-12 border border-white/5"
              >
                <div
                  class="w-full h-full absolute inset-0 rounded-full opacity-20 bg-[repeating-radial-gradient(#000_0,#000_2px,#222_3px)]"
                ></div>
                <div
                  class="w-24 h-24 bg-cover bg-center rounded-full border-4 border-[#222]"
                  :style="{
                    backgroundImage: `url(${albumData.albumPageMainInfo.cover})`,
                  }"
                ></div>
              </div>
            </div>

            <!-- Right: Details -->
            <div
              class="flex-1 flex flex-col justify-center text-center md:text-left pt-4"
            >
              <div class="mb-4">
                <div
                  class="flex items-center justify-center md:justify-start gap-3 mb-3"
                >
                  <span
                    v-if="albumData.albumPageMainInfo.isFinished === 2"
                    class="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded text-sm font-bold tracking-wider uppercase"
                    >完结</span
                  >
                  <span
                    v-else
                    class="px-2 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded text-[10px] font-bold tracking-wider uppercase"
                    >连载中</span
                  >
                  <span
                    v-if="albumData.albumPageMainInfo.vipType > 0"
                    class="px-2 py-0.5 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded text-[10px] font-bold tracking-wider uppercase"
                    >VIP</span
                  >
                </div>
                <h1
                  class="text-3xl md:text-4xl font-bold text-white mb-3 leading-tight tracking-tight"
                >
                  {{ albumData.albumPageMainInfo.albumTitle }}
                </h1>
                <p
                  class="text-gray-400 text-sm flex items-center justify-center md:justify-start gap-4"
                >
                  <span class="flex items-center gap-1.5" title="主播">
                    <span class="i-carbon-user text-orange-500"></span>
                    <span
                      class="hover:text-white transition-colors cursor-pointer border-b border-transparent hover:border-gray-500"
                      >{{ albumData.albumPageMainInfo.anchorName }}</span
                    >
                  </span>
                  <span class="w-1 h-1 bg-gray-600 rounded-full"></span>
                  <span class="flex items-center gap-1.5" title="播放量">
                    <span class="i-carbon-headphones text-orange-500"></span>
                    <span>{{
                      formatPlayCount(albumData.albumPageMainInfo.playCount)
                    }}</span>
                  </span>
                  <span class="w-1 h-1 bg-gray-600 rounded-full"></span>
                  <span class="text-gray-500"
                    >更新于
                    {{
                      albumData.albumPageMainInfo.updateDate.split(" ")[0]
                    }}</span
                  >
                </p>
              </div>

              <!-- Action Bar -->
              <div
                class="flex flex-wrap items-center justify-center md:justify-start gap-4 mt-6"
              >
                <button
                  class="group relative px-8 py-3 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-500 hover:to-orange-400 text-white rounded-full font-bold shadow-lg shadow-orange-900/30 hover:shadow-orange-700/50 transition-all hover:-translate-y-0.5"
                >
                  <div class="flex items-center gap-2">
                    <span
                      class="i-carbon-play-filled text-xl group-hover:scale-110 transition-transform"
                    ></span>
                    <span>立即播放</span>
                  </div>
                </button>

                <button
                  @click="handleSubscribe"
                  :disabled="submitting"
                  class="px-6 py-3 bg-[#1f1f1f] border border-white/10 hover:border-orange-500/30 text-gray-300 hover:text-white rounded-full font-medium transition-all hover:bg-[#2a2a2a] disabled:opacity-50 flex items-center gap-2"
                  :class="{
                    'text-orange-500 border-orange-500/20 bg-orange-500/5':
                      albumData.albumPageMainInfo.isSubscribe,
                  }"
                >
                  <span
                    v-if="submitting"
                    class="i-carbon-circle-dash animate-spin"
                  ></span>
                  <span
                    v-else
                    :class="
                      albumData.albumPageMainInfo.isSubscribe
                        ? 'i-carbon-star-filled'
                        : 'i-carbon-star'
                    "
                    class="text-lg"
                  ></span>
                  {{
                    albumData.albumPageMainInfo.isSubscribe ? "已订阅" : "订阅"
                  }}
                </button>

                <div class="flex gap-2">
                  <button
                    class="w-11 h-11 flex items-center justify-center rounded-full bg-[#1f1f1f] border border-white/10 text-gray-400 hover:text-white hover:bg-[#2a2a2a] hover:border-gray-600 transition-all"
                    title="下载"
                  >
                    <span class="i-carbon-download text-lg"></span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Content Section -->
        <div class="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Left Column: Details & Gallery -->
          <div class="lg:col-span-2 space-y-8">
            <!-- Highlights / Intro Module -->
            <div
              class="bg-[#141414] rounded-2xl border border-white/5 overflow-hidden"
            >
              <div class="p-4 border-b border-white/5">
                <h3
                  class="font-bold text-white text-lg flex items-center gap-2"
                >
                  <span class="w-1 h-5 bg-orange-500 rounded-full"></span>
                  精彩详情
                </h3>
              </div>

              <!-- Content Container -->
              <div class="relative">
                <div
                  class="px-5 py-6 transition-all duration-500 ease-in-out"
                  :class="{
                    'max-h-[600px] overflow-hidden': !isGalleryExpanded,
                  }"
                >
                  <!-- Rich Text Content (Text + Images) -->
                  <!-- Enforcing white text for the content -->
                  <div
                    class="rich-intro-content text-white leading-relaxed space-y-4"
                    v-html="
                      albumData?.albumPageMainInfo?.richIntro ||
                      albumData?.albumPageMainInfo?.shortIntro
                    "
                  ></div>
                </div>

                <!-- Gradient Overlay (when collapsed) -->
                <div
                  v-if="!isGalleryExpanded"
                  class="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-[#141414] via-[#141414]/90 to-transparent pointer-events-none z-10"
                ></div>
              </div>

              <!-- Toggle Button -->
              <div
                class="p-4 bg-[#141414] flex justify-center sticky bottom-0 z-20 pt-2 pb-6"
              >
                <button
                  @click="isGalleryExpanded = !isGalleryExpanded"
                  class="group relative overflow-hidden px-10 py-3 rounded-full font-medium text-sm transition-all duration-300 shadow-xl"
                >
                  <!-- Content -->
                  <div
                    class="relative flex items-center gap-2 text-white group-hover:scale-105 transition-transform"
                  >
                    <span>{{ isGalleryExpanded ? "收起" : "展示全部" }}</span>
                    <span
                      class="i-carbon-chevron-down text-lg transition-transform duration-300"
                      :class="{ 'rotate-180': isGalleryExpanded }"
                    ></span>
                  </div>
                </button>
              </div>
            </div>

            <!-- Tracks List Module -->
            <div
              class="bg-[#141414] rounded-2xl border border-white/5 overflow-hidden mt-8"
            >
              <div class="p-4 border-b border-white/5">
                <div class="flex items-center justify-between">
                  <h3
                    class="font-bold text-white text-lg flex items-center gap-2"
                  >
                    <span class="w-1 h-5 bg-orange-500 rounded-full"></span>
                    曲目列表
                  </h3>
                  <div class="flex items-center gap-2">
                    <span class="text-gray-500 text-sm">
                      共 {{ tracksTotalCount }} 首曲目
                    </span>

                    <!-- 批量操作按钮 -->
                    <button
                      @click="toggleAllTracks"
                      class="px-3 py-1.5 bg-[#1f1f1f] text-gray-400 hover:text-orange-400 hover:bg-[#252525] border border-white/5 rounded-lg text-sm transition-all flex items-center gap-1.5"
                      title="全选/取消全选"
                    >
                      <span
                        :class="
                          selectedTracks.size === tracksList.length
                            ? 'i-carbon-checkbox-checked-filled'
                            : 'i-carbon-checkbox'
                        "
                      ></span>
                      <span>{{
                        selectedTracks.size === tracksList.length
                          ? "取消"
                          : "全选"
                      }}</span>
                    </button>

                    <button
                      @click="downloadSelectedTracks"
                      :disabled="selectedTracks.size === 0"
                      class="px-3 py-1.5 bg-orange-500/10 text-orange-400 hover:bg-orange-500 hover:text-white border border-orange-500/20 rounded-lg text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
                      title="下载选中"
                    >
                      <span class="i-carbon-download"></span>
                      下载选中 ({{ selectedTracks.size }})
                    </button>

                    <button
                      @click="downloadAllTracks"
                      class="px-3 py-1.5 bg-[#1f1f1f] text-gray-400 hover:text-orange-400 hover:bg-[#252525] border border-white/5 rounded-lg text-sm transition-all flex items-center gap-1.5"
                      title="下载全部"
                    >
                      <span class="i-carbon-download"></span>
                      下载全部
                    </button>
                  </div>
                </div>
              </div>

              <!-- Tracks Loading State -->
              <div
                v-if="tracksLoading"
                class="flex justify-center items-center py-16"
              >
                <div
                  class="w-12 h-12 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin"
                ></div>
              </div>

              <!-- Tracks List -->
              <div v-else class="divide-y divide-white/5">
                <div
                  v-for="(track, index) in tracksList"
                  :key="track.trackId"
                  class="group hover:bg-[#1a1a1a] transition-colors cursor-pointer"
                  @click="playTrack(track)"
                >
                  <div class="flex items-center gap-4 px-5 py-4">
                    <!-- Checkbox for Batch Selection -->
                    <div
                      class="flex-shrink-0"
                      @click.stop="toggleTrackSelection(track.trackId)"
                    >
                      <div
                        class="w-6 h-6 flex items-center justify-center rounded border-2 cursor-pointer transition-all"
                        :class="
                          selectedTracks.has(track.trackId)
                            ? 'bg-orange-500 border-orange-500 text-white'
                            : 'bg-[#1f1f1f] border-white/10 text-gray-400 hover:border-gray-600'
                        "
                      >
                        <span
                          :class="
                            selectedTracks.has(track.trackId)
                              ? 'i-carbon-checkbox-checked-filled'
                              : 'i-carbon-checkbox'
                          "
                          class="text-lg"
                        ></span>
                      </div>
                    </div>

                    <!-- Play Number -->
                    <div
                      class="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-[#1f1f1f] text-gray-500 group-hover:bg-orange-500 group-hover:text-white transition-all text-sm font-medium"
                    >
                      {{ track.index }}
                    </div>

                    <!-- Track Info -->
                    <div class="flex-1 min-w-0">
                      <h4
                        class="text-gray-200 font-medium truncate group-hover:text-orange-400 transition-colors"
                        :title="track.title"
                      >
                        {{ track.title }}
                      </h4>
                      <div class="flex items-center gap-3 mt-1">
                        <span
                          class="text-gray-500 text-sm flex items-center gap-1"
                        >
                          <span class="i-carbon-time"></span>
                          {{ formatDuration(track.duration) }}
                        </span>
                        <span
                          class="text-gray-600 text-sm flex items-center gap-1"
                        >
                          <span class="i-carbon-headphones"></span>
                          {{ formatPlayCount(track.playCount) }}
                        </span>
                        <span
                          v-if="track.isPaid"
                          class="text-orange-500 text-xs px-2 py-0.5 bg-orange-500/10 border border-orange-500/20 rounded"
                          >VIP</span
                        >
                      </div>
                    </div>

                    <!-- Action Buttons -->
                    <div class="flex items-center gap-2">
                      <button
                        class="w-9 h-9 flex items-center justify-center rounded-full bg-[#1f1f1f] border border-white/5 text-gray-400 hover:text-orange-500 hover:border-orange-500/30 transition-all opacity-0 group-hover:opacity-100"
                        title="播放"
                        @click.stop="playTrack(track)"
                      >
                        <span class="i-carbon-play-filled"></span>
                      </button>
                      <button
                        class="w-9 h-9 flex items-center justify-center rounded-full bg-[#1f1f1f] border border-white/5 text-gray-400 hover:text-orange-500 hover:border-orange-500/30 transition-all opacity-0 group-hover:opacity-100"
                        title="下载"
                        @click.stop="downloadTrack(track)"
                      >
                        <span class="i-carbon-download"></span>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Empty State -->
                <div
                  v-if="tracksList.length === 0 && !tracksLoading"
                  class="flex flex-col items-center justify-center py-16 text-center"
                >
                  <span
                    class="i-carbon-music text-5xl text-gray-600 mb-4"
                  ></span>
                  <p class="text-gray-500">暂无曲目数据</p>
                </div>
              </div>

              <!-- Pagination -->
              <div
                v-if="totalPages > 1"
                class="p-4 border-t border-white/5 flex items-center justify-center gap-2"
              >
                <button
                  @click="prevPage"
                  :disabled="currentPage <= 1"
                  class="px-4 py-2 rounded-lg bg-[#1f1f1f] border border-white/10 text-gray-400 hover:text-white hover:border-gray-600 hover:bg-[#2a2a2a] disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center gap-1"
                >
                  <span class="i-carbon-chevron-left"></span>
                  上一页
                </button>

                <div class="flex items-center gap-2">
                  <button
                    v-for="page in displayedPages"
                    :key="page"
                    @click="goToPage(page)"
                    class="min-w-[40px] h-10 rounded-lg transition-all flex items-center justify-center"
                    :class="
                      currentPage === page
                        ? 'bg-orange-500 text-white font-medium'
                        : 'bg-[#1f1f1f] text-gray-400 hover:text-white hover:bg-[#2a2a2a] border border-white/10'
                    "
                  >
                    {{ page === -1 ? "..." : page }}
                  </button>
                </div>

                <button
                  @click="nextPage"
                  :disabled="currentPage >= totalPages"
                  class="px-4 py-2 rounded-lg bg-[#1f1f1f] border border-white/10 text-gray-400 hover:text-white hover:border-gray-600 hover:bg-[#2a2a2a] disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center gap-1"
                >
                  下一页
                  <span class="i-carbon-chevron-right"></span>
                </button>
              </div>
            </div>
          </div>

          <!-- Sidebar: Recommended / Tags (Placeholder) -->
          <div class="space-y-6">
            <!-- Tags -->
            <div
              class="bg-[#141414] rounded-2xl border border-white/5 p-6"
              v-if="albumData.albumPageMainInfo.tags?.length"
            >
              <h3 class="font-bold text-white text-base mb-4">关联标签</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="tag in albumData.albumPageMainInfo.tags"
                  :key="tag"
                  class="px-3 py-1.5 bg-[#1f1f1f] text-gray-400 hover:text-orange-400 hover:bg-[#252525] hover:border-orange-500/30 border border-white/5 rounded-lg text-sm transition-all cursor-pointer"
                >
                  # {{ tag }}
                </span>
              </div>
            </div>

            <!-- Anchor Info removed as requested -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { xmlyService } from "@/services/xmlyService";
import { useXmlyLoginStore } from "@/stores/xmlyLoginStore";
import request from "@/utils/request";
import Toast from "@/utils/toast";
import type { AlbumDetailData, TrackInfo } from "@/types/xmly";

const route = useRoute();
const xmlyStore = useXmlyLoginStore();
const loading = ref(false);
const submitting = ref(false);
const error = ref("");
const albumData = ref<AlbumDetailData | null>(null);
const isGalleryExpanded = ref(false);

// 下载路径相关
const downloadPath = ref("");
const loadingDownloadPath = ref(false);

// 曲目列表相关
const tracksList = ref<TrackInfo[]>([]);
const tracksLoading = ref(false);
const currentPage = ref(1);
const pageSize = ref(30);
const tracksTotalCount = ref(0);

// 下载状态管理（每个曲目的下载状态）
const trackDownloadStatus = ref<
  Record<
    number,
    { downloading: boolean; downloaded: boolean; progress: number }
  >
>({});
const downloadStatusPolling = ref(false);
const downloadStatusInterval = ref<number | null>(null);

const totalPages = computed(() =>
  Math.ceil(tracksTotalCount.value / pageSize.value),
);

// 显示的页码（智能分页）
const displayedPages = computed(() => {
  const pages: number[] = [];
  const total = totalPages.value;
  const current = currentPage.value;

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i);
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i);
      }
      pages.push(-1);
      pages.push(total);
    } else if (current >= total - 3) {
      pages.push(1);
      pages.push(-1);
      for (let i = total - 4; i <= total; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);
      pages.push(-1);
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i);
      }
      pages.push(-1);
      pages.push(total);
    }
  }

  return pages;
});

const formatPlayCount = (count: number) => {
  if (count > 100000000) return (count / 100000000).toFixed(1) + "亿";
  if (count > 10000) return (count / 10000).toFixed(1) + "万";
  return count.toString();
};

const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
};

// 下载路径相关函数
const selectDownloadFolder = async () => {
  try {
    loadingDownloadPath.value = true;
    const res = await request.get<{ path: string }>("/system/select-folder");
    if (res && res.path) {
      downloadPath.value = res.path;
      Toast.success("路径已选择");
    }
  } catch (error) {
    console.error("选择文件夹失败:", error);
    Toast.error("选择文件夹失败");
  } finally {
    loadingDownloadPath.value = false;
  }
};

const loadDownloadPath = async () => {
  try {
    loadingDownloadPath.value = true;
    // 从喜马拉雅登录状态中获取用户ID
    const userId =
      xmlyStore.userInfo?.uid || xmlyStore.userInfo?.nick_name || "";

    if (!userId) {
      console.warn("未获取到用户ID");
      return;
    }

    const res = await request.get<{ success: boolean; path?: string }>(
      "/system/download-path",
      {
        params: {
          user_id: userId,
          behavior_type: "XIMALAYA_DOWNLOAD_PATH",
        },
      },
    );
    if (res.success && res.path) {
      downloadPath.value = res.path;
      console.log("从数据库加载下载路径:", res.path);
    }
  } catch (error) {
    console.error("加载下载路径失败:", error);
  } finally {
    loadingDownloadPath.value = false;
  }
};

const saveDownloadPath = async (path: string) => {
  if (!path) return;
  try {
    // 从喜马拉雅登录状态中获取用户ID
    const userId =
      xmlyStore.userInfo?.uid || xmlyStore.userInfo?.nick_name || "";

    if (!userId) {
      console.warn("未获取到用户ID，无法保存下载路径");
      return;
    }

    await request.post("/system/download-path", {
      user_id: userId,
      download_path: path,
      behavior_type: "XIMALAYA_DOWNLOAD_PATH",
    });
    console.log("下载路径已保存:", path);
  } catch (error) {
    console.error("保存下载路径失败:", error);
  }
};

// 监听下载路径变化
watch(downloadPath, (newPath) => {
  if (newPath) {
    saveDownloadPath(newPath);
  }
});

// scrollGallery removed

const fetchAlbumDetail = async () => {
  const albumId = route.query.albumId as string;
  if (!albumId) {
    error.value = "缺少专辑参数";
    return;
  }

  loading.value = true;
  error.value = "";

  try {
    const res = await xmlyService.getAlbumDetail(albumId);
    let resData: any = res;
    if (typeof res === "string") {
      try {
        resData = JSON.parse(res);
      } catch (e) {
        console.error(e);
      }
    }

    if (resData && resData.data) {
      albumData.value = resData.data;
      // 获取专辑详情后，自动加载第一页曲目
      fetchTracksList();
    } else {
      error.value = "无法加载专辑数据";
    }
  } catch (err: any) {
    error.value = err.message || "网络请求失败";
  } finally {
    loading.value = false;
  }
};

const fetchTracksList = async (page: number = currentPage.value) => {
  if (!albumData.value) return;

  const albumId = albumData.value.albumId.toString();

  tracksLoading.value = true;
  try {
    const res = await xmlyService.getTracksList(albumId, page, pageSize.value);
    let resData: any = res;
    if (typeof res === "string") {
      try {
        resData = JSON.parse(res);
      } catch (e) {
        console.error(e);
      }
    }

    if (resData && resData.data) {
      tracksList.value = resData.data.tracks;
      tracksTotalCount.value = resData.data.trackTotalCount;
      currentPage.value = resData.data.pageNum;
    } else {
      Toast.error("加载曲目列表失败");
    }
  } catch (err: any) {
    Toast.error(err.message || "网络请求失败");
  } finally {
    tracksLoading.value = false;
  }
};

const playTrack = (track: TrackInfo) => {
  // 播放曲目的逻辑
  console.log("播放曲目:", track);
  Toast.info(`开始播放: ${track.title}`);
};

const prevPage = () => {
  if (currentPage.value > 1) {
    fetchTracksList(currentPage.value - 1);
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    fetchTracksList(currentPage.value + 1);
  }
};

const goToPage = (page: number) => {
  if (page === -1 || page === currentPage.value) return;
  fetchTracksList(page);
};

// 下载相关功能
const downloadTrack = async (track: TrackInfo) => {
  // 检查下载路径
  if (!downloadPath.value) {
    Toast.error("请先设置下载路径");
    return;
  }

  try {
    Toast.info("正在获取下载信息...");

    // 获取专辑ID、专辑名称和用户ID
    const albumId = albumData.value?.albumId?.toString() || "";
    const albumName = albumData.value?.albumPageMainInfo?.albumTitle || "";
    const userId =
      xmlyStore.userInfo?.uid || xmlyStore.userInfo?.nick_name || "";

    // 使用批量下载接口，即使单个曲目也走批量逻辑
    const trackIds = [track.trackId.toString()];
    const res = await xmlyService.batchGetTracksDownloadInfo(
      trackIds,
      albumId,
      albumName,
      userId,
    );
    console.log("曲目下载信息:", res);

    // 检查返回数据格式
    let downloadData: any = res;
    if (typeof res === "string") {
      try {
        downloadData = JSON.parse(res);
      } catch (e) {
        console.error("解析下载信息失败:", e);
        Toast.error("解析下载信息失败");
        return;
      }
    }

    // 处理批量下载结果
    if (
      downloadData &&
      downloadData.success &&
      Array.isArray(downloadData.success) &&
      downloadData.success.length > 0
    ) {
      const successCount = downloadData.success_count || 0;
      const failedCount = downloadData.failed_count || 0;

      // 显示消息
      Toast.success(downloadData.message || "下载任务已启动");

      // 启动轮询下载状态
      if (downloadData.downloading) {
        const albumId = albumData.value?.albumId?.toString() || "";
        await startDownloadStatusPolling(albumId, 3000); // 每3秒轮询一次
      }

      // 不再触发浏览器下载，因为后台任务已经在下载
      // 只是为了兼容性保留原代码（但不会执行）
    } else {
      Toast.error("获取下载信息失败");
    }
  } catch (err: any) {
    console.error("下载曲目失败:", err);
    Toast.error(err.message || "下载失败");
  }
};

// 下载当前页所有曲目
const downloadAllTracks = async () => {
  // 检查下载路径
  if (!downloadPath.value) {
    Toast.error("请先设置下载路径");
    return;
  }

  if (tracksList.value.length === 0) {
    Toast.warning("当前页没有可下载的曲目");
    return;
  }

  try {
    Toast.info(`正在获取 ${tracksList.value.length} 个曲目的下载信息...`);

    // 获取专辑ID、专辑名称和用户ID
    const albumId = albumData.value?.albumId?.toString() || "";
    const albumName = albumData.value?.albumPageMainInfo?.albumTitle || "";
    const userId =
      xmlyStore.userInfo?.uid || xmlyStore.userInfo?.nick_name || "";

    const trackIds = tracksList.value.map((track) => track.trackId.toString());
    const res = await xmlyService.batchGetTracksDownloadInfo(
      trackIds,
      albumId,
      albumName,
      userId,
    );
    console.log("批量下载信息:", res);

    // 检查返回数据格式
    let downloadData: any = res;
    if (typeof res === "string") {
      try {
        downloadData = JSON.parse(res);
      } catch (e) {
        console.error("解析批量下载信息失败:", e);
        Toast.error("解析下载信息失败");
        return;
      }
    }

    // 检查下载结果
    if (downloadData) {
      const successCount = downloadData.success_count || 0;
      const failedCount = downloadData.failed_count || 0;
      const total = downloadData.total || trackIds.length;

      if (successCount > 0) {
        Toast.success(`成功获取 ${successCount}/${total} 个曲目的下载信息`);

        // 遍历成功的下载项
        if (downloadData.success && Array.isArray(downloadData.success)) {
          downloadData.success.forEach((item: any, index: number) => {
            setTimeout(() => {
              const trackInfo = item.data;
              let downloadUrl = "";

              if (trackInfo && trackInfo.src) {
                downloadUrl = trackInfo.src;
              } else if (trackInfo && trackInfo.url) {
                downloadUrl = trackInfo.url;
              } else if (trackInfo && trackInfo.path) {
                downloadUrl = trackInfo.path;
              }

              if (downloadUrl) {
                const link = document.createElement("a");
                link.href = downloadUrl;
                // 从曲目列表中查找标题
                const track = tracksList.value.find(
                  (t) => t.trackId.toString() === item.trackId.toString(),
                );
                const title = track ? track.title : `曲目_${item.trackId}`;
                link.download = `${title}.m4a`;
                link.target = "_blank";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }
            }, index * 500); // 每隔500ms触发一个下载，避免同时下载太多
          });
        }
      }

      if (failedCount > 0) {
        setTimeout(
          () => {
            Toast.error(`${failedCount} 个曲目下载信息获取失败`);
          },
          successCount * 500 + 1000,
        );
      }
    } else {
      Toast.error("批量获取下载信息失败");
    }
  } catch (err: any) {
    console.error("批量下载失败:", err);
    Toast.error(err.message || "批量下载失败");
  }
};

// 选择要下载的曲目
const selectedTracks = ref<Set<number>>(new Set());

const toggleTrackSelection = (trackId: number) => {
  if (selectedTracks.value.has(trackId)) {
    selectedTracks.value.delete(trackId);
  } else {
    selectedTracks.value.add(trackId);
  }
};

const toggleAllTracks = () => {
  if (selectedTracks.value.size === tracksList.value.length) {
    // 全部取消选择
    selectedTracks.value.clear();
  } else {
    // 全部选中
    tracksList.value.forEach((track) =>
      selectedTracks.value.add(track.trackId),
    );
  }
};

// 下载选中的曲目
const downloadSelectedTracks = async () => {
  // 检查下载路径
  if (!downloadPath.value) {
    Toast.error("请先设置下载路径");
    return;
  }

  if (selectedTracks.value.size === 0) {
    Toast.warning("请先选择要下载的曲目");
    return;
  }

  // 获取专辑ID、专辑名称和用户ID
  const albumId = albumData.value?.albumId?.toString() || "";
  const albumName = albumData.value?.albumPageMainInfo?.albumTitle || "";
  const userId = xmlyStore.userInfo?.uid || xmlyStore.userInfo?.nick_name || "";

  const trackIds = Array.from(selectedTracks.value).map((id) => id.toString());

  try {
    Toast.info(`正在获取 ${trackIds.length} 个选中曲目的下载信息...`);

    const res = await xmlyService.batchGetTracksDownloadInfo(
      trackIds,
      albumId,
      albumName,
      userId,
    );
    console.log("选中曲目下载信息:", res);

    let downloadData: any = res;
    if (typeof res === "string") {
      try {
        downloadData = JSON.parse(res);
      } catch (e) {
        console.error("解析下载信息失败:", e);
        Toast.error("解析下载信息失败");
        return;
      }
    }

    if (
      downloadData &&
      downloadData.success &&
      Array.isArray(downloadData.success)
    ) {
      const successCount = downloadData.success_count || 0;
      Toast.success(`开始下载 ${successCount} 个选中曲目`);

      downloadData.success.forEach((item: any, index: number) => {
        setTimeout(() => {
          const trackInfo = item.data;
          let downloadUrl = "";

          if (trackInfo && trackInfo.src) {
            downloadUrl = trackInfo.src;
          } else if (trackInfo && trackInfo.url) {
            downloadUrl = trackInfo.url;
          } else if (trackInfo && trackInfo.path) {
            downloadUrl = trackInfo.path;
          }

          if (downloadUrl) {
            const link = document.createElement("a");
            link.href = downloadUrl;
            const track = tracksList.value.find(
              (t) => t.trackId.toString() === item.trackId.toString(),
            );
            const title = track ? track.title : `曲目_${item.trackId}`;
            link.download = `${title}.m4a`;
            link.target = "_blank";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }
        }, index * 500);
      });

      // 清除选择
      selectedTracks.value.clear();
    } else {
      Toast.error("获取下载信息失败");
    }
  } catch (err: any) {
    console.error("下载选中曲目失败:", err);
    Toast.error(err.message || "下载失败");
  }
};

// 查询专辑下载状态
const checkAlbumDownloadStatus = async () => {
  const albumId = albumData.value?.albumId?.toString() || "";
  const albumName = albumData.value?.albumPageMainInfo?.albumTitle || "";
  const userId = xmlyStore.userInfo?.uid || xmlyStore.userInfo?.nick_name || "";
  debugger;
  if (!albumId || !userId) {
    console.warn("无法获取专辑ID或用户ID");
    return;
  }

  try {
    const status = await xmlyService.getAlbumDownloadStatus(userId, albumId);
    console.log("专辑下载状态:", status);

    if (status.success && status.data) {
      const albumInfo = status.data;
      const downloads = albumInfo.downloads || {};

      // 更新每个曲目的下载状态
      Object.entries(downloads).forEach(
        ([trackId, trackStatus]: [string, any]) => {
          const statusValue = trackStatus.status;
          const isDownloaded = statusValue === "success";
          const isLoading = statusValue === "pending";

          if (trackDownloadStatus.value[trackId]) {
            trackDownloadStatus.value[trackId] = {
              ...trackDownloadStatus.value[trackId],
              downloaded: isDownloaded,
              loading: isLoading,
              progress: isDownloaded ? 100 : isLoading ? 50 : 0,
            };
          }
        },
      );
    }
  } catch (error) {
    console.error("查询专辑下载状态失败:", error);
  }
};

// 开始轮询下载状态
const startDownloadStatusPolling = async (
  albumId: string,
  intervalMs: number = 2000,
) => {
  if (downloadStatusInterval.value) {
    // 清除之前的轮询
    clearInterval(downloadStatusInterval.value);
  }

  downloadStatusPolling.value = true;

  // 立即查询一次
  await checkAlbumDownloadStatus();

  // 启动轮询
  downloadStatusInterval.value = window.setInterval(async () => {
    await checkAlbumDownloadStatus();

    // 检查是否所有都下载完成或失败
    const allTracks = tracksList.value;
    const allDownloaded = allTracks.every((track) => {
      const status = trackDownloadStatus.value[track.trackId];
      return (
        status &&
        (status.downloaded || (!status.loading && status.progress > 0))
      );
    });

    if (allDownloaded && allTracks.length > 0) {
      // 全部完成，停止轮询
      stopDownloadStatusPolling();
      Toast.success("所有曲目下载完成");
    }
  }, intervalMs);
};

// 停止轮询下载状态
const stopDownloadStatusPolling = () => {
  if (downloadStatusInterval.value) {
    clearInterval(downloadStatusInterval.value);
    downloadStatusInterval.value = null;
  }
  downloadStatusPolling.value = false;
  console.log("停止轮询下载状态");
};

// 下载状态轮询的清理
onUnmounted(() => {
  stopDownloadStatusPolling();
});

const handleSubscribe = async () => {
  if (!albumData.value || submitting.value) return;

  const albumId = albumData.value.albumId.toString();
  const isSubscribed = albumData.value.albumPageMainInfo.isSubscribe;

  submitting.value = true;
  try {
    const res = await (isSubscribed
      ? xmlyService.unsubscribe(albumId)
      : xmlyService.subscribe(albumId));
    if (
      res &&
      (res.ret === 200 ||
        res.code === 0 ||
        JSON.stringify(res).includes("成功"))
    ) {
      albumData.value.albumPageMainInfo.isSubscribe = !isSubscribed;
      Toast.success(isSubscribed ? "已取消订阅" : "订阅成功");
    } else {
      Toast.error("操作失败");
    }
  } catch (err: any) {
    Toast.error(err.message || "操作异常");
  } finally {
    submitting.value = false;
  }
};

onMounted(async () => {
  // 先加载下载路径
  await loadDownloadPath();
  // 然后加载专辑详情
  fetchAlbumDetail();
});
</script>

<style scoped>
/* Custom Scrollbar hide */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Rich Text Styles for Dark Mode */
:deep(.rich-intro-content) {
  line-height: 1.8;
  font-size: 1rem; /* Slightly larger for better readability */
  color: #ffffff; /* Enforce white text as requested */
}
:deep(.rich-intro-content img) {
  /* Hide images in the text flow if we want them ONLY in gallery, 
      BUT usually rich intro has context. Let's keep them but make them responsive */
  max-width: 100%;
  height: auto;
  border-radius: 0.75rem;
  margin: 1.5rem 0;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
:deep(.rich-intro-content p) {
  margin-bottom: 1.25em;
}
:deep(.rich-intro-content strong) {
  color: #e5e7eb;
}

/* 3D Perspective */
.perspective-1000 {
  perspective: 1000px;
}
</style>
