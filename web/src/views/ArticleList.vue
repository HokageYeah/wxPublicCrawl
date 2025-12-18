<template>
  <div class="max-w-4xl mx-auto py-8">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold">{{ nickname || '公众号文章' }}</h1>
        <p class="text-gray-500 text-sm mt-1">ID: {{ fakeid }}</p>
      </div>
      <button @click="router.back()" class="btn-secondary">返回搜索</button>
    </div>

    <!-- Controls -->
    <div class="card p-6 mb-8">
      <div class="flex flex-col md:flex-row gap-4 items-end">
        <div class="flex-1 w-full">
          <label class="block text-sm font-medium text-gray-700 mb-1">下载保存路径</label>
          <input 
            v-model="downloadPath" 
            type="text" 
            class="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="例如: /Users/username/Downloads/WxArticles"
          />
        </div>
        <div class="flex gap-2">
            <button @click="fetchArticles(0)" :disabled="loading" class="btn-primary">
                <span v-if="loading" class="i-carbon-renew animate-spin mr-2"></span>
                刷新列表
            </button>
        </div>
      </div>
      <p class="text-xs text-gray-500 mt-2">提示：请确保路径存在且有写入权限。留空将使用默认路径。</p>
    </div>

    <!-- List -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">标题</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">发布时间</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">摘要</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="article in articles" :key="article.aid" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 line-clamp-2" :title="article.title">{{ article.title }}</div>
                <a :href="article.link" target="_blank" class="text-xs text-blue-500 hover:text-blue-700 mt-1 inline-block">在浏览器打开</a>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(article.update_time) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                <div class="line-clamp-2 max-w-xs" :title="article.digest">{{ article.digest }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button 
                  @click="downloadArticle(article)" 
                  :disabled="article.downloading"
                  class="text-primary hover:text-primary-dark font-bold disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ article.downloading ? '下载中...' : '下载' }}
                </button>
                <span v-if="article.downloaded" class="ml-2 text-green-600">
                    <span class="i-carbon-checkmark"></span>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Empty State -->
      <div v-if="articles.length === 0 && !loading" class="text-center py-12 text-gray-500">
        暂无文章数据
      </div>
      
      <!-- Loading State -->
      <div v-if="loading && articles.length === 0" class="text-center py-12 text-gray-500">
        加载中...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

interface Article {
  aid: string;
  title: string;
  link: string;
  update_time: number;
  digest: string;
  downloading?: boolean;
  downloaded?: boolean;
}

const route = useRoute();
const router = useRouter();

const fakeid = route.query.fakeid as string;
const nickname = route.query.nickname as string;

// 默认下载路径建议（仅为占位符，如果为空，后端将处理实际默认值）
const downloadPath = ref(''); 
const articles = ref<Article[]>([]);
const loading = ref(false);

const formatDate = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleString();
};

const fetchArticles = async (begin = 0) => {
  if (!fakeid) return;
  
  loading.value = true;
  try {
    const apiUrl = import.meta.env.DEV ? '/api/v1' : '/api/v1';
    
    // 使用现有 API: /get-wx-article-list
    /*
    class ArticleListRequest(BaseModel):
        query: str = ""
        begin: int = 0
        count: int = 5
        wx_public_id: str
    */
    const response = await axios.post(`${apiUrl}/wx/get-wx-article-list`, {
      query: "",
      begin: begin, // Start from 0
      count: 20, // Fetch 20
      wx_public_id: fakeid
    });
    
    // 基于后端服务逻辑的响应结构：
    // 返回 publish_page_obj，其中包含 'publish_list'
    if (response.data && response.data.publish_list) {
        // 将响应映射到 Article 接口
        // publish_list 中项目的结构？
        // 通常是：{ appmsg_info: { title, digest, ... }, appmsgid, ... }
        // 查看后端：publish_page_obj['publish_list'] = [json.loads(item["publish_info"]) for item in publish_page_obj['publish_list']]
        
        // publish_info 通常包含多篇文章 (appmsg_info, appmsgex...)
        // 让我们假设后端解析返回了一个对象列表，我们可以从中找到标题/链接。
        // 等等，publish_info 的典型结构是：
        // {
        //    "type": 9,
        //    "appmsgid": 2247483653,
        //    "itemidx": 1,
        //    "link": "...",
        //    "title": "...",
        //    "digest": "...",
        //    "update_time": 162...,
        //    "cover": "..."
        // }
        // 如果存在 'appmsgex' 列表，它可能是多图文消息。
        // 但我们先假设是扁平列表，或者我们提取第一个，或者只相信基本字段在顶层或在 appmsgex[0] 中。
        
        // 让我们通过映射我们可能得到的内容或仅获取存在的字段来进行调试。
        
        const list = response.data.publish_list.map((item: any) => {
            // 根据消息类型，字段有所不同。
            // 类型 9 是标准文章。
            const info = item.appmsgex ? item.appmsgex[0] : item;
            return {
                aid: info.aid || info.appmsgid + '_' + info.itemidx,
                title: info.title,
                link: info.link,
                update_time: info.update_time,
                digest: info.digest,
                downloading: false,
                downloaded: false
            };
        });
        articles.value = list;
    }
  } catch (error) {
    console.error('Fetch articles failed:', error);
    alert('获取文章列表失败');
  } finally {
    loading.value = false;
  }
};

const downloadArticle = async (article: Article) => {
  if (article.downloading) return;
  
  article.downloading = true;
  try {
    const apiUrl = import.meta.env.DEV ? '/api/v1' : '/api/v1';
    
    /*
    class ArticleDetailRequest(BaseModel):
        article_link: str
        wx_public_id: str
        wx_public_name: str
        is_upload_to_aliyun: bool = False
        is_save_to_local: bool = True
        save_to_local_path: str = ""
        save_to_local_file_name: str = ""
    */
    
    await axios.post(`${apiUrl}/wx/get-wx-article-detail-by-link`, {
        article_link: article.link,
        wx_public_id: fakeid,
        wx_public_name: nickname,
        is_save_to_local: true,
        save_to_local_path: downloadPath.value, // 传递用户输入
        save_to_local_file_name: article.title + '.html' // 可选，后端会处理
    });
    
    article.downloaded = true;
    // alert('下载成功');
  } catch (error) {
    console.error('Download failed:', error);
    alert('下载失败');
  } finally {
    article.downloading = false;
  }
};

onMounted(() => {
    if (fakeid) {
        fetchArticles();
    }
});
</script>
