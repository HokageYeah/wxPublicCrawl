<template>
  <div class="max-w-4xl mx-auto py-8">
    <h1 class="text-2xl font-bold mb-8 text-center">搜索公众号</h1>
    
    <div class="card p-8 mb-8">
      <div class="flex gap-4">
        <input 
          v-model="query" 
          @keyup.enter="handleSearch"
          type="text" 
          placeholder="请输入公众号名称" 
          class="flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button 
          @click="handleSearch" 
          :disabled="loading"
          class="btn-primary flex items-center"
        >
          <span v-if="loading" class="i-carbon-circle-dash animate-spin mr-2"></span>
          搜索
        </button>
      </div>
    </div>

    <!-- Results -->
    <div v-if="results.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="item in results" 
        :key="item.fakeid" 
        class="card hover:shadow-lg transition-all cursor-pointer p-0 overflow-hidden"
        @click="selectAccount(item)"
      >
        <div class="p-6 flex flex-col items-center">
          <img :src="item.round_head_img" class="w-20 h-20 rounded-full mb-4 object-cover" alt="" referrerpolicy="no-referrer" />
          <h3 class="font-bold text-lg mb-2 text-center" v-html="item.nickname"></h3>
          <p class="text-sm text-gray-500 mb-2">{{ item.alias }}</p>
          <p class="text-xs text-gray-400 line-clamp-2 text-center self-stretch">{{ item.signature }}</p>
        </div>
        <div class="bg-gray-50 px-6 py-3 border-t text-center text-sm text-primary font-medium hover:bg-gray-100 transition-colors">
          查看文章
        </div>
      </div>
    </div>
    
    <div v-else-if="hasSearched && !loading" class="text-center text-gray-500 py-12">
      未找到相关公众号
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// 使用 axios 直接调用或导入预配置的实例
// import axios from 'axios';
import request from '@/utils/request';

// 定义搜索结果接口
interface PublicAccount {
  fakeid: string;
  nickname: string;
  alias: string;
  round_head_img: string;
  signature: string;
}

const router = useRouter();
const query = ref('');
const loading = ref(false);
const hasSearched = ref(false);
const results = ref<PublicAccount[]>([]);

const handleSearch = async () => {
  if (!query.value.trim()) return;
  
  loading.value = true;
  hasSearched.value = true;
  results.value = [];
  
  try {
    // 确定 API 基础 URL
    // 如果在开发模式下运行 (npm run dev)，通常会设置代理或者我们需要完整的 URL
    // 如果在生产环境下运行（桌面应用），如果从同一源提供服务，相对路径 '/api/v1' 是可行的
    
    // 目前假设使用 Vite 代理或同一源
    // const baseURL = import.meta.env.DEV ? '/web-api/api/v1/wx/public' : '/api/v1/wx/public';
    // 实际上，在桌面应用中，main.py 提供静态文件服务，所以相对路径是正确的。
    // 在开发模式下，我们需要代理。
    
    // const response = await axios.get(`${baseURL}/wx/search-wx-public`, {
    const dataList = await request.get('/search-wx-public', {
      params: {
        query: query.value,
        begin: 0,
        count: 10
      }
    });
      console.log('dataList------', dataList);
    if (dataList && Array.isArray(dataList)) {
      results.value = dataList;
    }
  } catch (error) {
    console.error('Search failed:', error);
    alert('搜索失败，请检查是否已登录或网络连接');
  } finally {
    loading.value = false;
  }
};

const selectAccount = (account: PublicAccount) => {
  // 带参数跳转到文章列表
  // 通过 query 传递数据或使用 store。
  // Query 对于重载时的持久化更简单（如果支持），fakeid 敏感吗？不敏感。
  // 我们需要 fakeid 和 nickname（用于文件夹命名）
  
  // 注意：nickname 可能包含像 <em>...</em> 这样的搜索高亮 HTML 标签。
  // 我们应该去除它们。
  const rawNickname = account.nickname.replace(/<[^>]*>?/gm, '');
  
  router.push({
    name: 'articles',
    query: {
      fakeid: account.fakeid,
      nickname: rawNickname
    }
  });
};
</script>
