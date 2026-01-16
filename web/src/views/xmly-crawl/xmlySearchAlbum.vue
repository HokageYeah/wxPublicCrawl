<template>
  <div
    class="h-screen w-full bg-[#0a0a0a] text-gray-200 font-sans flex items-center justify-center overflow-hidden py-8"
  >
    <!-- 固定宽高的主容器 -->
    <div
      class="max-w-6xl w-full h-full max-h-[calc(100vh-4rem)] flex flex-col bg-[#0a0a0a]"
    >
      <!-- 搜索区域卡片 (参考 SearchPublic.vue 样式) -->
      <div
        class="card p-6 bg-[#141414] border border-gray-800 shadow-lg flex-none"
      >
        <div class="flex items-center gap-4 mb-4">
          <!-- Brand / Title -->
          <div class="flex items-center gap-2 select-none">
            <div
              class="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center shadow-lg shadow-orange-900/20"
            >
              <span
                class="i-carbon-microphone-filled text-white text-xl"
              ></span>
            </div>
            <h1 class="text-xl font-bold text-white tracking-tight">
              喜马拉雅搜索
            </h1>
          </div>
        </div>

        <!-- 搜索框 -->
        <div class="flex gap-3">
          <input
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            type="text"
            placeholder="搜索专辑、主播、有声书..."
            class="flex-1 px-4 py-3 bg-[#1a1a1a] border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all shadow-inner"
            :disabled="loading"
          />
          <button
            @click="handleSearch"
            :disabled="loading || !searchQuery.trim()"
            class="px-8 py-3 bg-orange-600 hover:bg-orange-500 text-white rounded-lg font-medium transition-all shadow-lg shadow-orange-900/20 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap min-w-[100px]"
          >
            <span
              v-if="loading"
              class="i-carbon-circle-dash animate-spin mr-2"
            ></span>
            <span v-else class="i-carbon-search mr-2"></span>
            搜索
          </button>
        </div>
      </div>

      <!-- 滚动结果区域 -->
      <div class="flex-1 overflow-hidden mt-6 relative">
        <div
          class="absolute inset-0 overflow-y-auto scroll-smooth custom-scrollbar px-4 py-2"
        >
          <!-- Loading State -->
          <div
            v-if="loading && !results.length"
            class="h-full flex flex-col items-center justify-center min-h-[400px]"
          >
            <div
              class="w-12 h-12 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin mb-4"
            ></div>
            <p class="text-gray-400 animate-pulse">正在搜索相关专辑...</p>
          </div>

          <!-- Empty State: Initial -->
          <div
            v-else-if="!hasSearched"
            class="h-full flex flex-col items-center justify-center min-h-[400px] text-center opacity-40"
          >
            <span class="i-carbon-music text-7xl text-gray-600 mb-6"></span>
            <h3 class="text-xl font-bold text-gray-300 mb-2">探索有声世界</h3>
            <p class="text-gray-500 max-w-sm">
              输入关键词，发现海量优质有声书与精选专辑
            </p>
          </div>

          <!-- Empty State: No Results -->
          <div
            v-else-if="results.length === 0"
            class="h-full flex flex-col items-center justify-center min-h-[400px] text-center opacity-60"
          >
            <span
              class="i-carbon-search-locate text-7xl text-gray-600 mb-6"
            ></span>
            <h3 class="text-xl font-bold text-gray-300 mb-2">未找到相关结果</h3>
            <p class="text-gray-500">换个关键词试试看吧</p>
          </div>

          <!-- Results Grid -->
          <div v-else class="pb-8">
            <div
              class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            >
              <div
                v-for="album in results"
                :key="album.albumId"
                class="group bg-[#141414] border border-white/5 rounded-xl overflow-hidden hover:border-orange-500/30 hover:shadow-2xl hover:shadow-orange-500/10 transition-all duration-300 flex flex-col h-full"
              >
                <!-- Cover Image -->
                <div class="aspect-square relative overflow-hidden bg-gray-900">
                  <img
                    :src="album.coverPath"
                    :alt="album.title"
                    class="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
                    loading="lazy"
                  />

                  <!-- Badges -->
                  <div
                    class="absolute top-2 right-2 flex flex-col gap-1.5 items-end z-10"
                  >
                    <span
                      v-if="album.isPaid"
                      class="px-2 py-0.5 bg-yellow-600/90 backdrop-blur-sm text-white text-[10px] font-bold rounded shadow-sm"
                      >付费</span
                    >
                    <span
                      v-if="album.isFinished === 2"
                      class="px-2 py-0.5 bg-green-600/90 backdrop-blur-sm text-white text-[10px] font-bold rounded shadow-sm"
                      >完结</span
                    >
                    <span
                      v-if="album.isVipFree"
                      class="px-2 py-0.5 bg-red-600/90 backdrop-blur-sm text-white text-[10px] font-bold rounded shadow-sm"
                      >VIP</span
                    >
                  </div>

                  <!-- Overlay Info -->
                  <div
                    class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/60 to-transparent p-3 pt-10"
                  >
                    <div
                      class="flex items-center text-xs text-gray-300 gap-3 font-mono"
                    >
                      <span class="flex items-center gap-1"
                        ><span
                          class="i-carbon-play-filled text-orange-500"
                        ></span
                        >{{ formatNumber(album.playCount) }}</span
                      >
                      <span class="flex items-center gap-1"
                        ><span class="i-carbon-playlist text-orange-500"></span
                        >{{ album.tracksCount }}集</span
                      >
                    </div>
                  </div>
                </div>

                <!-- Content -->
                <div class="p-4 flex flex-col flex-1">
                  <h3
                    class="text-base font-bold text-gray-100 mb-2 line-clamp-2 leading-snug group-hover:text-orange-400 transition-colors"
                    :title="album.title"
                    v-html="highlightKeyword(album.title)"
                  ></h3>

                  <p
                    class="text-xs text-gray-400 mb-4 line-clamp-2 leading-relaxed min-h-[2.5em]"
                  >
                    {{ album.intro || "暂无简介" }}
                  </p>

                  <!-- Anchor -->
                  <div
                    class="flex items-center gap-2 mb-4 mt-auto border-t border-white/5 pt-3"
                  >
                    <img
                      :src="album.anchorPic"
                      class="w-6 h-6 rounded-full object-cover bg-gray-800"
                    />
                    <span
                      class="text-xs text-gray-400 truncate flex-1 hover:text-gray-200"
                      >{{ album.nickname }}</span
                    >
                  </div>

                  <!-- Action Button -->
                  <button
                    @click="toggleSubscribe(album)"
                    :disabled="actionLoading === album.albumId"
                    :class="[
                      'w-full py-2 rounded text-xs font-medium transition-all duration-200 flex items-center justify-center gap-1.5',
                      isSubscribed(album.albumId)
                        ? 'bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20'
                        : 'bg-white text-black hover:bg-gray-200 shadow-sm',
                    ]"
                  >
                    <span
                      v-if="actionLoading === album.albumId"
                      class="i-carbon-circle-dash animate-spin text-sm"
                    ></span>
                    <template v-else>
                      <span
                        :class="
                          isSubscribed(album.albumId)
                            ? 'i-carbon-checkmark-filled'
                            : 'i-carbon-add-alt'
                        "
                      ></span>
                      <span>{{
                        isSubscribed(album.albumId) ? "已订阅" : "订阅监控"
                      }}</span>
                    </template>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页区域 -->
          <div
            v-if="hasSearched && pagination"
            class="mt-8 pt-6 border-t border-gray-800"
          >
            <div
              class="flex flex-col sm:flex-row items-center justify-between gap-4"
            >
              <div class="text-sm text-gray-500">
                共找到
                <span class="text-orange-500 font-bold mx-1">{{
                  pagination.total
                }}</span>
                条结果
              </div>

              <!-- Pagination Controls -->
              <div
                v-if="pagination.totalPage > 1"
                class="flex items-center gap-2"
              >
                <button
                  @click="changePage(pagination!.currentPage - 1)"
                  :disabled="pagination.currentPage <= 1 || loading"
                  class="w-9 h-9 flex items-center justify-center rounded-md bg-[#252525] border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 hover:bg-[#333] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <span class="i-carbon-chevron-left text-lg"></span>
                </button>

                <div
                  class="px-4 py-1.5 bg-[#1a1a1a] rounded-md border border-gray-800 text-sm flex items-center gap-1 text-gray-400 font-mono"
                >
                  <span class="text-orange-500 font-bold">{{
                    pagination.currentPage
                  }}</span>
                  <span class="text-gray-600">/</span>
                  <span>{{ pagination.totalPage }}</span>
                </div>

                <button
                  @click="changePage(pagination!.currentPage + 1)"
                  :disabled="
                    pagination.currentPage >= pagination.totalPage || loading
                  "
                  class="w-9 h-9 flex items-center justify-center rounded-md bg-[#252525] border border-gray-700 text-gray-400 hover:text-white hover:border-gray-500 hover:bg-[#333] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  <span class="i-carbon-chevron-right text-lg"></span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import Toast from "@/utils/toast";
import { xmlyService } from "@/services/xmlyService";
import type {
  SearchAlbumResult,
  SearchAlbumResponse,
  SearchAlbumPagination,
} from "@/types/xmly";

// -- State --
const searchQuery = ref("");
const loading = ref(false);
const actionLoading = ref<number | null>(null);
const hasSearched = ref(false);
const results = ref<SearchAlbumResult[]>([]);
const pagination = ref<SearchAlbumPagination | null>(null);
const subscribedIds = ref<Set<number>>(new Set());

// -- Toast Helper --
const showToast = (
  message: string,
  type: "success" | "error" | "info" = "success"
) => {
  if (type === "error") {
    Toast.error(message);
  } else if (type === "info") {
    Toast.info(message);
  } else {
    Toast.success(message);
  }
};

// -- Utility Functions --
const formatNumber = (num: number) => {
  if (num > 100000000) return (num / 100000000).toFixed(1) + "亿";
  if (num > 10000) return (num / 10000).toFixed(1) + "万";
  return num.toString();
};

const highlightKeyword = (text: string) => {
  if (!searchQuery.value) return text;
  try {
    const reg = new RegExp(searchQuery.value, "gi");
    return text.replace(
      reg,
      (match) =>
        `<span class="text-orange-500 font-medium bg-orange-500/10 rounded px-0.5">${match}</span>`
    );
  } catch (e) {
    return text;
  }
};

const isSubscribed = (id: number) => {
  return subscribedIds.value.has(id);
};

// -- Actions --
const handleSearch = async () => {
  if (!searchQuery.value.trim()) return;
  await performSearch(1);
};

const performSearch = async (page: number) => {
  if (loading.value) return;

  loading.value = true;
  hasSearched.value = true;
  if (page === 1) results.value = []; // Only clear on new search, ideally keep if strictly paging but simpler UX for now

  try {
    // Note: Assuming xmlyService.search might support page, otherwise assume API returns default page
    // The current service definition only takes 'kw'.
    // If backend ignores page, this will just re-search page 1.
    // UI will show pagination if backend returns 'pagination' object.
    const res = await xmlyService.search(searchQuery.value);

    let data: SearchAlbumResponse;
    if (typeof res === "string") {
      try {
        data = JSON.parse(res);
      } catch {
        throw new Error("API Response Parse Error");
      }
    } else {
      data = res;
    }

    if (data && data.docs) {
      results.value = data.docs;

      // Handle pagination
      if (data.pagination) {
        pagination.value = data.pagination;
      } else {
        // Fallback mock pagination if result exists but no pagination data
        pagination.value = {
          pageSize: 20,
          currentPage: page,
          total: data.docs.length,
          totalPage: 1,
        };
      }
    } else {
      if (page === 1) results.value = [];
      showToast("未找到相关内容", "info");
    }
  } catch (err: any) {
    console.error(err);
    showToast(err.message || "搜索请求失败", "error");
  } finally {
    loading.value = false;
  }
};

const changePage = async (page: number) => {
  // Currently the API service might not support page parameter explicitly in the frontend method signature
  // We will simulate the UI update or call search again.
  // Ideally, we should update xmlyService.search to accept (kw, page, pageSize)
  showToast("分页功能依赖后端接口更新，目前仅重载本页", "info");
  await performSearch(page);
};

const toggleSubscribe = async (album: SearchAlbumResult) => {
  if (actionLoading.value) return;
  const id = album.albumId;
  actionLoading.value = id;

  try {
    if (isSubscribed(id)) {
      const res = await xmlyService.unsubscribe(id.toString());
      // Check response strictly
      if (
        res &&
        (res.ret === 200 ||
          JSON.stringify(res).includes("成功") ||
          res.code === 0)
      ) {
        subscribedIds.value.delete(id);
        showToast("已取消订阅", "success");
      } else {
        showToast("取消失败，请重试", "error");
      }
    } else {
      const res = await xmlyService.subscribe(id.toString());
      if (
        res &&
        (res.ret === 200 ||
          JSON.stringify(res).includes("成功") ||
          res.code === 0)
      ) {
        subscribedIds.value.add(id);
        showToast("订阅成功", "success");
      } else {
        showToast("订阅失败，请重试", "error");
      }
    }
  } catch (err: any) {
    showToast(err.message || "操作异常", "error");
  } finally {
    actionLoading.value = null;
  }
};
</script>

<style scoped>
/* Custom Scrollbar for the main content area */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px; /* for horizontal if needed */
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
