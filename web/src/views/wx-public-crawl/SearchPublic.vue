<template>
  <div class="max-w-4xl mx-auto py-8">
    <h1 class="text-2xl font-bold mb-8 text-center">搜索公众号</h1>
    
    <!-- AI助手卡片 -->
    <div class="card p-6 mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200">
      <div class="flex items-center mb-4">
        <span class="i-carbon-watson-health-ai-results text-2xl text-blue-600 mr-2"></span>
        <h2 class="text-lg font-bold text-gray-800">AI智能助手</h2>
        <span class="ml-auto text-xs text-gray-500">支持天气查询、计算器等</span>
      </div>
      
      <!-- AI对话区域 -->
      <div v-if="aiMessages.length > 0" class="mb-4 max-h-60 overflow-y-auto space-y-3 p-4 bg-white rounded-lg border border-gray-200">
        <div v-for="(msg, index) in aiMessages" :key="index" 
             :class="[
               'flex gap-3',
               msg.role === 'user' ? 'justify-end' : 'justify-start'
             ]">
          <div :class="[
            'max-w-[80%] rounded-lg px-4 py-2.5',
            msg.role === 'user' 
              ? 'bg-blue-600 text-white ml-auto' 
              : 'bg-gray-100 text-gray-800'
          ]">
            <div class="flex items-start gap-2">
              <span v-if="msg.role === 'assistant'" class="i-carbon-bot text-lg flex-shrink-0 mt-0.5"></span>
              <div class="flex-1">
                <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ msg.content }}</p>
                <div v-if="msg.toolCalls && msg.toolCalls > 0" class="text-xs opacity-75 mt-1">
                  🔧 调用了 {{ msg.toolCalls }} 个工具
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- AI思考中动画 -->
        <div v-if="aiThinking" class="flex gap-3 justify-start">
          <div class="bg-gray-100 rounded-lg px-4 py-2.5">
            <div class="flex items-center gap-2">
              <span class="i-carbon-bot text-lg"></span>
              <span class="i-carbon-circle-dash animate-spin text-blue-600"></span>
              <span class="text-sm text-gray-600">AI正在思考...</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- AI输入框 -->
      <div class="flex gap-3">
        <input 
          v-model="aiQuery" 
          @keyup.enter="handleAIQuery"
          type="text" 
          placeholder="试试问我：查询北京的天气、计算10+20、什么是Python..." 
          class="flex-1 px-4 py-2.5 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          :disabled="aiThinking"
        />
        <button 
          @click="handleAIQuery" 
          :disabled="aiThinking || !aiQuery.trim()"
          class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <span v-if="aiThinking" class="i-carbon-circle-dash animate-spin"></span>
          <span v-else class="i-carbon-send-alt"></span>
          {{ aiThinking ? '思考中' : '发送' }}
        </button>
        <button 
          v-if="aiMessages.length > 0"
          @click="clearAIHistory"
          class="px-4 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors"
          title="清空对话"
        >
          <span class="i-carbon-clean"></span>
        </button>
      </div>
      
      <!-- 快捷示例 -->
      <div v-if="aiMessages.length === 0" class="mt-3 flex flex-wrap gap-2">
        <button 
          v-for="example in aiExamples" 
          :key="example"
          @click="aiQuery = example; handleAIQuery()"
          class="text-xs px-3 py-1 bg-white border border-blue-200 hover:border-blue-400 text-blue-600 hover:text-blue-700 rounded-full transition-colors"
        >
          {{ example }}
        </button>
      </div>
    </div>
    
    <div class="card p-8 mb-8">
      <!-- 标签区域 -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">热门标签</label>
        <div class="flex flex-wrap gap-2">
          <div 
            v-for="tag in tags" 
            :key="tag.id"
            class="group relative inline-flex items-center px-3 py-1 rounded-full text-sm cursor-pointer transition-colors border"
            :class="query === tag.name 
              ? 'bg-primary text-white border-primary border-opacity-100' 
              : 'bg-gray-100 text-gray-700 border-transparent hover:bg-gray-200'"
            @click="toggleTag(tag.name)"
          >
            {{ tag.name }}
            
            <!-- 删除按钮 (hover 显示) -->
            <button 
              class="ml-2 opacity-0 group-hover:opacity-100 transition-opacity text-xs rounded-full bg-black bg-opacity-20 w-4 h-4 flex items-center justify-center hover:bg-opacity-40"
              @click="handleDeleteTag(tag.id, $event)"
              title="删除标签"
            >
              ×
            </button>
          </div>
          
          <!-- 添加标签按钮 -->
          <div v-if="!isAddingTag" 
            class="inline-flex items-center px-3 py-1 rounded-full text-sm border border-dashed border-gray-300 text-gray-500 hover:border-primary hover:text-primary cursor-pointer transition-colors"
            @click="isAddingTag = true"
          >
            + 添加
          </div>
          
          <!-- 添加标签输入框 -->
          <div v-else class="inline-flex items-center">
            <input 
              v-model="newTagName"
              type="text"
              class="px-3 py-1 rounded-full text-sm border border-primary focus:outline-none w-24"
              placeholder="输入标签"
              @keyup.enter="handleAddTag"
              @blur="handleAddTag"
              ref="newTagInput"
              autoFocus
            />
          </div>
        </div>
      </div>

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
        class="group card hover:shadow-2xl hover:scale-105 transition-all duration-300 cursor-pointer p-0 overflow-hidden flex flex-col border border-white hover:border-gray-300 hover:border-primary-200"
        @click="selectAccount(item)"
      >
        <div class="p-6 flex flex-col items-center flex-1">
          <img :src="item.round_head_img" class="w-20 h-20 rounded-full mb-4 object-cover transition-transform duration-300 group-hover:scale-110" alt="" referrerpolicy="no-referrer" />
          <h3 class="font-bold text-lg mb-2 text-center group-hover:text-primary transition-colors duration-300" v-html="item.nickname"></h3>
          <p class="text-sm text-gray-500 mb-2">{{ item.alias }}</p>
          <p class="text-xs text-gray-400 line-clamp-2 text-center self-stretch">{{ item.signature }}</p>
        </div>
        <div class="bg-gray-50 px-6 py-3 border-t text-center text-sm text-primary font-medium group-hover:bg-primary-100 group-hover:text-primary-700 transition-all duration-300">
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// 使用 axios 直接调用或导入预配置的实例
// import axios from 'axios';
import request from '@/utils/request';
import { useWechatLoginStore } from '@/stores/wechatLoginStore';

// 定义搜索结果接口
interface PublicAccount {
  fakeid: string;
  nickname: string;
  alias: string;
  round_head_img: string;
  signature: string;
}

interface SearchTag {
  id: number;
  name: string;
}

interface AIMessage {
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: number;
}

const router = useRouter();
const query = ref('');
const loading = ref(false);
const hasSearched = ref(false);
const results = ref<PublicAccount[]>([]);
const wechatStore = useWechatLoginStore();

// 标签相关状态
const tags = ref<SearchTag[]>([]);
const isAddingTag = ref(false);
const newTagName = ref('');

// AI助手相关状态
const aiQuery = ref('');
const aiThinking = ref(false);
const aiMessages = ref<AIMessage[]>([]);
const aiExamples = [
  '查询北京的天气',
  '计算 10+20',
  '什么是Python'
];

// 获取标签列表
const fetchTags = async () => {
  try {
    const res = await request.get<SearchTag[]>('/system/tags');
    tags.value = res || [];
    
    // 如果没有标签，尝试初始化
    if (tags.value.length === 0) {
      await initTags();
    }
  } catch (error) {
    console.error('获取标签失败:', error);
  }
};

// 初始化默认标签
const initTags = async () => {
  try {
    const res = await request.post<SearchTag[]>('/system/tags/init');
    if (res) {
      tags.value = res;
    }
  } catch (error) {
    console.error('初始化标签失败:', error);
  }
};

// 添加新标签
const handleAddTag = async () => {
  const name = newTagName.value.trim();
  if (!name) {
    isAddingTag.value = false;
    return;
  }
  
  // 检查是否重复
  if (tags.value.some(t => t.name === name)) {
    alert('标签已存在');
    return;
  }
  
  try {
    await request.post('/system/tags', { name });
    newTagName.value = '';
    isAddingTag.value = false;
    await fetchTags();
  } catch (error: any) {
    console.error('添加标签失败:', error);
    alert(error.response?.data?.message || '添加失败');
  }
};

// 删除标签
const handleDeleteTag = async (id: number, event: Event) => {
  event.stopPropagation(); // 防止触发选择
  if (!confirm('确定删除该标签吗？')) return;
  
  try {
    await request.delete(`/system/tags?tag_id=${id}`);
    // 如果当前搜索框内容等于该标签，清空搜索框
    const tag = tags.value.find(t => t.id === id);
    if (tag && query.value === tag.name) {
      query.value = '';
    }
    await fetchTags();
  } catch (error) {
    console.error('删除标签失败:', error);
  }
};

// 切换标签选择
const toggleTag = (tagName: string) => {
  if (query.value === tagName) {
    query.value = ''; // 取消选择
  } else {
    query.value = tagName; // 选中
  }
};

onMounted(() => {
  fetchTags();
  // 进入这个页面，如果用户没有登录，则再初始化登录信息
  // if (!wechatStore.isLoggedIn) {
  //   wechatStore.initialize();
  // }
});

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
    name: 'wx-public-crawl-articles',
    query: {
      fakeid: account.fakeid,
      nickname: rawNickname
    }
  });
};

// AI助手相关函数
const handleAIQuery = async () => {
  const userQuery = aiQuery.value.trim();
  if (!userQuery) return;
  
  // 添加用户消息
  aiMessages.value.push({
    role: 'user',
    content: userQuery
  });
  
  // 清空输入框
  aiQuery.value = '';
  aiThinking.value = true;
  
  try {
    // 调用AI接口
    const response = await request.post<{
      response: string;
      tool_calls_count: number;
      success: boolean;
      error?: string;
    }>('/ai/query', {
      query: userQuery,
      enable_tools: true,
      extra_body: {
        enable_thinking: false,
      }
    });
    
    if (response.success) {
      // 添加AI回复
      aiMessages.value.push({
        role: 'assistant',
        content: response.response,
        toolCalls: response.tool_calls_count
      });
    } else {
      // 显示错误
      aiMessages.value.push({
        role: 'assistant',
        content: `抱歉，出现错误：${response.error || '未知错误'}`
      });
    }
    
    // 自动滚动到底部
    setTimeout(() => {
      const chatContainer = document.querySelector('.max-h-60');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 100);
    
  } catch (error: any) {
    console.error('AI查询失败:', error);
    
    // 显示友好的错误消息
    let errorMessage = '抱歉，AI服务暂时不可用。';
    if (error.response?.status === 503) {
      errorMessage = 'AI服务未初始化，请先启动MCP服务。';
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    
    aiMessages.value.push({
      role: 'assistant',
      content: errorMessage
    });
  } finally {
    aiThinking.value = false;
  }
};

// 清空AI对话历史
const clearAIHistory = async () => {
  if (!confirm('确定要清空对话历史吗？')) return;
  
  try {
    // 调用后端清空历史
    await request.post('/ai/clear-history');
    
    // 清空前端显示
    aiMessages.value = [];
    aiQuery.value = '';
  } catch (error) {
    console.error('清空历史失败:', error);
    alert('清空失败，请重试');
  }
};
</script>
