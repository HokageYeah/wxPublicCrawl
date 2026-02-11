<template>
  <div
    class="h-screen w-full bg-[#0a0a0a] text-gray-200 font-sans flex items-center justify-center overflow-hidden py-8"
  >
    <!-- 固定宽高的主容器 -->
    <div
      class="max-w-7xl w-full h-full max-h-[calc(100vh-4rem)] flex flex-col bg-[#0a0a0a] relative"
    >
      <!-- 顶部筛选区域 (仿官方样式) -->
      <div
        class="bg-[#141414] border-b border-gray-800 px-8 py-6 flex-none z-10"
      >
        <!-- 排序 Tabs -->
        <div class="flex items-center mb-5">
          <span class="text-gray-500 text-sm mr-6 select-none">排序</span>
          <div class="flex items-center gap-8">
            <button
              v-for="tab in sortTabs"
              :key="tab.value"
              @click="handleSortChange(tab.value)"
              class="text-sm transition-all duration-200 relative py-1"
              :class="[
                subType === tab.value
                  ? 'text-orange-500 font-bold'
                  : 'text-gray-300 hover:text-orange-400'
              ]"
            >
              {{ tab.label }}
              <!-- Active Indicator -->
              <span
                v-if="subType === tab.value"
                class="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 bg-orange-500 rounded-full"
              ></span>
            </button>
          </div>
        </div>

        <!-- 分类 Tabs -->
        <div class="flex items-start">
          <span class="text-gray-500 text-sm mr-6 mt-1 select-none flex-shrink-0">分类</span>
          <div class="flex flex-wrap gap-x-8 gap-y-3">
            <!-- '全部' 选项 -->
            <!-- <button
              @click="handleCategoryChange('all')"
              class="text-sm transition-all duration-200 relative py-1"
              :class="[
                category === 'all'
                  ? 'text-orange-500 font-bold'
                  : 'text-gray-300 hover:text-orange-400'
              ]"
            >
              全部
              <span class="text-xs ml-0.5 opacity-60">{{ totalCount }}</span>
            </button> -->

            <!-- 动态分类列表 -->
            <button
              v-for="cat in categories"
              :key="cat.code"
              @click="handleCategoryChange(cat.code)"
              class="text-sm transition-all duration-200 relative py-1"
              :class="[
                category === cat.code
                  ? 'text-orange-500 font-bold'
                  : 'text-gray-300 hover:text-orange-400'
              ]"
            >
              {{ cat.title }}
              <span class="text-xs ml-0.5 opacity-60">{{ cat.count }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 列表内容区域 -->
      <div class="flex-1 overflow-hidden relative bg-[#0a0a0a]">
        <div
          class="absolute inset-0 overflow-y-auto scroll-smooth custom-scrollbar px-8 pb-10"
        >
          <!-- Loading -->
          <div
            v-if="loading && (!albums.length || currentPage === 1)"
            class="h-60 flex flex-col items-center justify-center"
          >
            <div
              class="w-10 h-10 border-4 border-orange-500/30 border-t-orange-500 rounded-full animate-spin mb-4"
            ></div>
            <p class="text-gray-500 text-sm">加载订阅内容...</p>
          </div>

          <!-- Empty State -->
          <div
            v-else-if="albums.length === 0"
            class="h-60 flex flex-col items-center justify-center opacity-50"
          >
            <span class="i-carbon-favorite text-6xl text-gray-700 mb-4"></span>
            <p class="text-gray-500">暂无订阅专辑</p>
          </div>

          <!-- Album List (Official Style) -->
          <div v-else class="space-y-3">
            <div
              v-for="album in albums"
              :key="album.id"
              class="group relative flex gap-8 py-6 rounded-xl border px-4 transition-all duration-200"
              :class="[
                'bg-[#141414]',
                hoveredAlbumId === album.id
                  ? 'border-orange-500 shadow-lg shadow-orange-500/20'
                  : 'border-gray-800/50 hover:border-orange-500/50 hover:shadow-[0_4px_16px_-4px_rgba(249,115,22,0.15)]'
              ]"
              @mouseenter="hoveredAlbumId = album.id"
              @mouseleave="hoveredAlbumId = null"
            >
              <!-- 封面图 (左侧) - 加大尺寸 -->
              <div class="relative flex-shrink-0 cursor-pointer" @click="goToAlbumDetail(album.id)">
                <div class="w-40 h-40 rounded-xl overflow-hidden bg-gray-800 border border-gray-700/50 shadow-md transition-all duration-200" :class="[
                  'group-hover:shadow-orange-900/10',
                  hoveredAlbumId === album.id ? 'border-orange-500' : ''
                ]">
                  <img
                    :src="getCoverUrl(album.coverPath)"
                    :alt="album.title"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
                    loading="lazy"
                    referrerpolicy="no-referrer"
                  />
                </div>
              </div>

              <!-- 内容信息 (右侧) - 增加间距 -->
              <div class="flex-1 min-w-0 flex flex-col justify-between py-1 relative">
                <!-- Row 1: 标题 + 标签 + 设置按钮 -->
                <div class="flex items-start justify-between gap-4 relative">
                  <div class="flex items-center gap-2 flex-wrap cursor-pointer" @click="goToAlbumDetail(album.id)">
                    <!-- VIP 标识 -->
                    <span 
                      v-if="isVip(album)" 
                      class="flex-shrink-0 px-1.5 py-0.5 bg-[#cba477] text-[#4a2d0c] text-[10px] font-extrabold rounded-sm leading-none shadow-sm"
                    >VIP</span>
                    
                    <h3 class="text-xl font-bold text-gray-100 hover:text-orange-500 transition-colors line-clamp-1 tracking-tight" :title="album.title">
                      {{ album.title }}
                    </h3>
                    
                    <!-- 状态标签: 完本/付费 -->
                    <span 
                      v-if="album.isFinished" 
                      class="px-2 py-0.5 text-xs font-medium text-emerald-400 border border-emerald-500/30 rounded bg-emerald-500/10 whitespace-nowrap"
                    >完本</span>
                    <span 
                      v-if="album.isPaid" 
                      class="px-2 py-0.5 text-xs font-medium text-amber-400 border border-amber-500/30 rounded bg-amber-500/10 whitespace-nowrap"
                    >付费</span>
                  </div>

                  <!-- 设置/操作按钮 (Hover显示) -->
                  <div 
                    class="opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center gap-2 relative z-20"
                  >
                    <button
                      class="p-1.5 text-gray-400 hover:text-white rounded-full hover:bg-gray-700 transition-colors"
                      title="取消订阅"
                      @click.stop="confirmUnsubscribe(album)"
                    >
                       <span class="i-carbon-trash-can text-lg">取消订阅</span>
                    </button>
                    <!-- 更多操作预留 -->
                    <button
                      class="p-1.5 text-gray-400 hover:text-white rounded-full hover:bg-gray-700 transition-colors"
                    >
                       <span class="i-carbon-settings text-lg"></span>
                    </button>
                  </div>
                </div>

                <!-- Row 2: 简介 外边句 -->
                <p 
                  class="text-sm text-gray-500 line-clamp-1 cursor-pointer hover:text-gray-400 transition-colors w-3/4 mt-2"
                  :title="album.description || album.subTitle"
                  @click="goToAlbumDetail(album.id)"
                >
                  {{ formatDescription(album) }}
                </p>

                <!-- Row 3: 主播信息 -->
                <div class="flex items-center gap-3 text-xs text-gray-500 mt-1">
                  <div class="flex items-center gap-2 cursor-pointer hover:text-gray-300 transition-colors">
                    <img
                      :src="getAnchorCover(album.anchor.anchorCoverPath)"
                      class="w-5 h-5 rounded-full object-cover border border-gray-700"
                      referrerpolicy="no-referrer"
                    />
                    <span class="max-w-[150px] truncate" :title="album.anchor.anchorNickName">
                      {{ album.anchor.anchorNickName }}
                    </span>
                  </div>
                  <span class="w-[1px] h-3 bg-gray-700"></span>
                  <span class="text-gray-500">{{ album.categoryTitle }}</span>
                </div>

                <!-- Row 4: 更新信息 (核心需求) -->
                <div class="flex items-center gap-3 text-xs text-gray-500 mt-auto pt-2">
                   <span class="font-mono text-gray-500">{{ formatDate(album.lastUptrackAt) }} 更新:</span>
                   <a 
                     :href="album.lastUptrackUrl" 
                     target="_blank" 
                     class="text-orange-500 hover:text-orange-400 hover:underline max-w-[300px] truncate"
                     :title="album.lastUptrackTitle"
                     @click.stop
                   >
                     {{ album.lastUptrackTitle || '暂无最新章节标题' }}
                   </a>
                   <span class="ml-4 text-gray-400">
                     已更新{{ album.trackCount }}集
                   </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页器 -->
          <div
            v-if="pagination && pagination.totalCount > pagination.pageSize"
            class="flex items-center justify-center gap-2 mt-8 py-4 border-t border-gray-800"
          >
            <button
              @click="changePage(currentPage - 1)"
              :disabled="currentPage <= 1 || loading"
              class="w-8 h-8 flex items-center justify-center rounded bg-[#1a1a1a] border border-gray-700 text-gray-400 hover:border-orange-500 hover:text-orange-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              <span class="i-carbon-chevron-left"></span>
            </button>

            <!-- 简单分页显示 -->
             <span class="text-sm text-gray-500 font-mono mx-2">
               {{ currentPage }} / {{ Math.ceil(pagination.totalCount / pagination.pageSize) }}
             </span>

            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage >= Math.ceil(pagination.totalCount / pagination.pageSize) || loading"
              class="w-8 h-8 flex items-center justify-center rounded bg-[#1a1a1a] border border-gray-700 text-gray-400 hover:border-orange-500 hover:text-orange-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              <span class="i-carbon-chevron-right"></span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onActivated, onDeactivated } from "vue";
import { useRouter } from "vue-router";
import { xmlyService } from "@/services/xmlyService";
import Toast from "@/utils/toast";
import type {
  SubscribedAlbumInfo,
  SubscribedAlbumsData,
  SubscribedAlbumCategory,
} from "@/types/xmly";
import dayjs from 'dayjs';
const router = useRouter();

// -- Config --
const sortTabs = [
  { label: "最近更新", value: 2 },
  { label: "最近订阅", value: 3 },
  { label: "最近常听", value: 1 },
];

// -- State --
const loading = ref(false);
const albums = ref<SubscribedAlbumInfo[]>([]);
const categories = ref<SubscribedAlbumCategory[]>([]);
const totalCount = ref(0); // For "All" category count
const hoverFilter = ref<string | null>(null);
const hoveredAlbumId = ref<number | null>(null);

// Filter States
const subType = ref(2); // 默认: 最近更新 (2)
const category = ref("all");
const currentPage = ref(1);
const pagination = ref<{
  pageSize: number;
  totalCount: number;
} | null>(null);

// -- Helpers --
const getCoverUrl = (path: string) => {
  if (!path) return "";
  // 140x140 for better quality
  return `https://imagev2.xmcdn.com/${path}!strip=1&quality=7&magick=webp&op_type=3&columns=180&rows=180`;
};

const getAnchorCover = (path: string) => {
  if (!path) return "";
  return `https://imagev2.xmcdn.com/${path}!strip=1&quality=7&magick=webp&op_type=3&columns=60&rows=60`;
};

const formatDate = (ts: number) => {
  if (!ts) return "--";
  return dayjs(ts).format("YYYY-MM-DD");
};

const formatDescription = (album: SubscribedAlbumInfo) => {
  // Use subtitle if description is empty, or combination
  // Official XM usually shows a specific intro line
  return album.description || album.subTitle || "暂无简介";
};

const isVip = (album: SubscribedAlbumInfo) => {
  // vipType check? or isV?
  // User asked to "Mark if VIP clearly"
  // Usually vipType > 0 means some VIP status.
  return album.vipType > 0;
};

// -- Actions --
const fetchSubscribedAlbums = async () => {
  if (loading.value) return;
  loading.value = true;

  try {
    const res = await xmlyService.getSubscribedAlbums(
      currentPage.value,
      30, // Official uses 30
      subType.value,
      category.value
    );

    let data: SubscribedAlbumsData;
    if (typeof res === "string") {
      try {
        data = JSON.parse(res).data;
      } catch {
        throw new Error("Response Parse Error");
      }
    } else {
      data = res.data;
    }

    albums.value = data.albumsInfo;
    categories.value = data.categoryArray;
    
    // Attempt to find 'all' category count or sum up
    // Usually 'All' count is totalCount from pagination
    if (data.categoryCode === 'all' || !data.categoryCode) {
        // If we are on 'all', update total
        totalCount.value = data.totalCount;
    } else {
        // If we switched category, we might rely on previous total or fetch separately (not supported by API usually)
        // For UI consistency, we might just keep previous or 0 if unknown. 
        // Or loop categories to find total? Categories usually is subset.
    }
    
    pagination.value = {
      pageSize: data.pageSize,
      totalCount: data.totalCount,
    };

    // If 'all' count is missing from categories array, we try to ensure it
    // Note: API returns specific categories. 'All' is implicit total.

  } catch (err: any) {
    console.error("Fetch Error:", err);
    Toast.error(err.message || "加载失败");
  } finally {
    loading.value = false;
  }
};

const handleSortChange = (val: number) => {
  if (subType.value === val) return;
  subType.value = val;
  currentPage.value = 1;
  fetchSubscribedAlbums();
};

const handleCategoryChange = (catCode: string) => {
  if (category.value === catCode) return;
  category.value = catCode;
  currentPage.value = 1;
  fetchSubscribedAlbums();
};

const changePage = (page: number) => {
  if (page < 1) return;
  currentPage.value = page;
  fetchSubscribedAlbums();
};

const goToAlbumDetail = (albumId: number) => {
  router.push({
    name: "xmly-crawl-album-detail",
    query: { albumId: albumId.toString() },
  });
};

const confirmUnsubscribe = async (album: SubscribedAlbumInfo) => {
  // Simple confirm
  // In a real app we might use a Modal. For now use window.confirm or just Toast action?
  // Let's just execute with a toast for now or optimistic update.
  if(!confirm(`确定取消订阅《${album.title}》吗？`)) return;

  try {
    const res = await xmlyService.unsubscribe(album.id.toString());
    if (res && (res.ret === 200 || res.code === 0 || JSON.stringify(res).includes('成功'))) {
      Toast.success("取消订阅成功");
      // Remove local
      albums.value = albums.value.filter(a => a.id !== album.id);
      if(pagination.value) pagination.value.totalCount--;
    } else {
       Toast.error("取消失败");
    }
  } catch (e: any) {
    Toast.error(e.message || "取消订阅出错");
  }
};

onMounted(() => {
  fetchSubscribedAlbums();
});
onActivated(() => {
  console.log("✓ XmlySubscribedAlbum activated");
});
onDeactivated(() => {
  console.log("✓ XmlySubscribedAlbum deactivated");
});
</script>

<style scoped>
/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px; /* for horizontal categories */
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
</style>
