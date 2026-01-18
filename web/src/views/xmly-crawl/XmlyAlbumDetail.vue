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
import { ref, onMounted, computed, nextTick } from "vue";
import { useRoute } from "vue-router";
import { xmlyService } from "@/services/xmlyService";
import Toast from "@/utils/toast";
import type { AlbumDetailData } from "@/types/xmly";

const route = useRoute();
const loading = ref(false);
const submitting = ref(false);
const error = ref("");
const albumData = ref<AlbumDetailData | null>(null);
const isGalleryExpanded = ref(false);

const formatPlayCount = (count: number) => {
  if (count > 100000000) return (count / 100000000).toFixed(1) + "亿";
  if (count > 10000) return (count / 10000).toFixed(1) + "万";
  return count.toString();
};

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
    } else {
      error.value = "无法加载专辑数据";
    }
  } catch (err: any) {
    error.value = err.message || "网络请求失败";
  } finally {
    loading.value = false;
  }
};

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

onMounted(() => {
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
