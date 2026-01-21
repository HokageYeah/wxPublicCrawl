<template>
  <div class="h-screen flex flex-col bg-gray-100 font-sans text-gray-900">
    <!-- 顶部区域：标题头和控制 -->
    <div class="flex-none bg-white border-b border-gray-200 shadow-sm z-20">
        <div class="max-w-7xl mx-auto px-6 py-4">
            <!-- 标题头 -->
            <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-4">
                    <button @click="router.back()" class="p-2 rounded-full hover:bg-gray-100 text-gray-600 transition-colors" title="返回">
                        <span class="i-carbon-arrow-left text-xl block"></span>
                    </button>
                    <div>
                        <h1 class="text-xl font-bold text-gray-900 leading-tight">{{ nickname || '公众号文章' }}</h1>
                        <div class="flex items-center text-xs text-gray-500 mt-1 gap-3">
                            <span class="bg-gray-100 px-2 py-0.5 rounded text-gray-600">ID: {{ fakeid }}</span>
                            <span>共 {{ totalCount }} 篇文章</span>
                        </div>
                    </div>
                </div>
                <div class="flex flex-col items-end gap-2">
                    <div class="flex gap-2">
                        <button @click="fetchArticles(1)" :disabled="loading" class="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm disabled:opacity-70 disabled:cursor-not-allowed">
                            <span v-if="loading" class="i-carbon-renew animate-spin mr-2 text-lg"></span>
                            <span v-else class="i-carbon-renew mr-2 text-lg"></span>
                            刷新列表
                        </button>
                        <button @click="analyzeEducation" :disabled="analyzing || articles.length === 0" class="flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm disabled:opacity-70 disabled:cursor-not-allowed">
                            <span v-if="analyzing" class="i-carbon-circle-dash animate-spin mr-2 text-lg"></span>
                            <span v-else class="i-carbon-idea mr-2 text-lg"></span>
                            AI帮分析
                        </button>
                        <button @click="exportArticles" :disabled="exporting || !downloadPath" class="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm disabled:opacity-70 disabled:cursor-not-allowed">
                            <span v-if="exporting" class="i-carbon-circle-dash animate-spin mr-2 text-lg"></span>
                            <span v-else class="i-carbon-download mr-2 text-lg"></span>
                            文章导出
                        </button>
                    </div>
                    <p class="text-xs text-gray-500 flex items-center">
                        <span class="i-carbon-information mr-1"></span>
                        AI帮助分析哪些文章是跟教育类有关的
                    </p>
                    <p v-if="!downloadPath" class="text-xs text-amber-600 flex items-center">
                        <span class="i-carbon-warning-filled mr-1"></span>
                        请先设置下载地址才能使用文章导出功能
                    </p>
                </div>
            </div>

            <!-- 控制区（紧凑版） -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div class="flex flex-col md:flex-row gap-6 md:items-center justify-between">
                    <!-- 配置开关 -->
                    <div class="flex gap-6">
                        <label class="flex items-center space-x-2.5 cursor-pointer group select-none">
                            <input type="checkbox" v-model="isSaveToLocal" class="form-checkbox h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 transition duration-150 ease-in-out">
                            <span class="text-sm font-medium text-gray-700 group-hover:text-gray-900">保存到本地</span>
                        </label>
                        <label class="flex items-center space-x-2.5 cursor-pointer group select-none">
                            <input type="checkbox" v-model="isUploadToAliyun" class="form-checkbox h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 transition duration-150 ease-in-out">
                            <span class="text-sm font-medium text-gray-700 group-hover:text-gray-900">上传到阿里云</span>
                        </label>
                    </div>

                    <!-- 路径选择 -->
                    <div v-if="isSaveToLocal" class="flex-1 max-w-2xl flex flex-col md:flex-row gap-3 md:items-center">
                         <div class="flex-1 relative">
                            <input 
                                v-model="downloadPath" 
                                type="text" 
                                class="w-full pl-3 pr-10 py-2 bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block transition-shadow placeholder-gray-400"
                                placeholder="请选择或输入保存文件夹路径"
                            />
                            <div v-if="!downloadPath" class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                                <span class="i-carbon-warning-filled text-amber-500 text-lg"></span>
                            </div>
                         </div>
                         <button @click="selectDownloadFolder" class="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-lg transition-colors whitespace-nowrap shadow-sm">
                            选择文件夹
                         </button>
                    </div>
                </div>
                 <p v-if="isSaveToLocal && !downloadPath" class="text-xs text-amber-600 mt-2 flex items-center">
                    <span class="i-carbon-information mr-1"></span>
                    请设置下载路径，否则无法开始下载。
                 </p>
            </div>
        </div>
    </div>

    <!-- 中间区域：可滚动列表 -->
    <div class="flex-1 overflow-hidden relative">
        <div class="absolute inset-0 overflow-auto custom-scrollbar bg-gray-100 px-6 py-6 max-w-7xl mx-auto w-full">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden min-h-[400px]">
                <table class="min-w-full divide-y divide-gray-100">
                  <thead class="bg-gray-50">
                    <tr>
                      <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-1/3">文章标题</th>
                      <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider w-48">发布时间</th>
                      <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">摘要</th>
                      <th scope="col" class="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider w-32">操作</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-100">
                    <tr v-for="article in articles" :key="article.aid" 
                        class="transition-colors group hover:bg-blue-50/50"
                    >
                      <td class="px-6 py-4">
                        <div class="text-sm font-medium text-gray-900 line-clamp-2 group-hover:text-blue-700 transition-colors" :title="article.title">
                            <!-- AI分析标签（仅文本） -->
                            <span v-if="article.is_education" class="font-bold mr-1 align-middle select-none ai-text-shimmer">
                                教育 | AI严选
                            </span>
                            <span class="align-middle">{{ article.title }}</span>
                        </div>
                         <div class="flex items-center gap-3 mt-1.5">
                              <a :href="article.link" target="_blank" class="text-xs text-gray-400 hover:text-blue-600 flex items-center transition-colors">
                                  <span class="i-carbon-link mr-1"></span> 原文链接
                              </a>
                              <div v-if="article.uploadedUrl" class="text-xs text-gray-400 flex items-center">
                                <span class="i-carbon-cloud-upload mr-1 text-green-500"></span>
                                <a :href="article.uploadedUrl" target="_blank" class="text-green-600 hover:text-green-700 hover:underline">阿里云链接</a>
                              </div>
                         </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                        {{ formatDate(article.update_time).split(' ')[0] }}
                        <span class="text-gray-400 text-xs ml-1">{{ formatDate(article.update_time).split(' ')[1] }}</span>
                      </td>
                      <td class="px-6 py-4 text-sm text-gray-500">
                        <div class="line-clamp-2 max-w-lg text-xs text-gray-400" :title="article.digest">{{ article.digest }}</div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div class="flex justify-end">
                            <button 
                              v-if="isSaveToLocal || isUploadToAliyun"
                              @click="downloadArticle(article)" 
                              :disabled="article.downloading || (isSaveToLocal && !downloadPath)"
                              class="relative overflow-hidden group/btn px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ease-out shadow-sm"
                              :class="[
                                  article.downloaded 
                                    ? 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200' 
                                    : 'bg-white text-gray-700 hover:text-blue-600 hover:border-blue-300 border border-gray-200 hover:shadow'
                              ]"
                            >
                              <div class="flex items-center gap-1.5">
                                  <!-- Loading Icon -->
                                  <span v-if="article.downloading" class="i-carbon-circle-dash animate-spin text-blue-600"></span>
                                  
                                  <!-- Status Icon -->
                                  <span v-else-if="article.downloaded" class="i-carbon-checkmark text-green-600"></span>
                                  <span v-else class="i-carbon-download group-hover/btn:text-blue-600"></span>
                                  
                                  <!-- Text -->
                                  <span>
                                      {{ article.downloading ? '处理中' : (article.downloaded ? '已完成' : '下载') }}
                                  </span>
                              </div>
                            </button>
                         </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
                
                <!-- 空状态 -->
                <div v-if="articles.length === 0 && !loading" class="flex flex-col items-center justify-center py-20 text-gray-400">
                    <span class="i-carbon-document-blank text-4xl mb-3 text-gray-300"></span>
                    <p class="text-sm">暂无文章数据</p>
                </div>
                
                <!-- 加载状态 -->
                <div v-if="loading && articles.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-500">
                    <span class="i-carbon-renew animate-spin text-3xl mb-3 text-blue-500"></span>
                    <p class="text-sm">正在加载文章列表...</p>
                </div>
            </div>
            
            <div class="h-6"></div> <!-- Bottom Spacer -->
        </div>
    </div>

    <!-- 底部区域：分页 -->
    <div class="flex-none bg-white border-t border-gray-200 px-6 py-4 z-20">
        <div class="max-w-7xl mx-auto">
            <div v-if="totalCount > 0" class="flex items-center justify-between">
              <!-- 移动端分页 -->
              <div class="flex flex-1 justify-between sm:hidden">
                <button 
                    @click="handlePageChange(currentPage - 1)" 
                    :disabled="currentPage === 1"
                    class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  上一页
                </button>
                <button 
                    @click="handlePageChange(currentPage + 1)" 
                    :disabled="currentPage === totalPages"
                    class="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  下一页
                </button>
              </div>

              <!-- 桌面端分页 -->
              <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                <div>
                  <p class="text-sm text-gray-500">
                    第 <span class="font-medium text-gray-900">{{ (currentPage - 1) * pageSize + 1 }}</span> - <span class="font-medium text-gray-900">{{ Math.min(currentPage * pageSize, totalCount) }}</span> 条，
                    共 <span class="font-medium text-gray-900">{{ totalCount }}</span> 条
                  </p>
                </div>
                <div>
                  <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                    <button 
                        @click="handlePageChange(currentPage - 1)"
                        :disabled="currentPage === 1"
                        class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 transition-colors"
                    >
                      <span class="sr-only">上一页</span>
                      <span class="i-carbon-chevron-left h-5 w-5"></span>
                    </button>
                    
                    <template v-for="page in totalPages" :key="page">
                         <button 
                            v-if="Math.abs(page - currentPage) <= 2 || page === 1 || page === totalPages"
                            @click="handlePageChange(page)"
                            :class="[
                                page === currentPage 
                                    ? 'z-10 bg-blue-600 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600' 
                                    : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:outline-offset-0',
                                'relative inline-flex items-center px-4 py-2 text-sm font-semibold focus:z-20 transition-colors'
                            ]"
                        >
                            <span v-if="Math.abs(page - currentPage) === 2 && page !== 1 && page !== totalPages">...</span>
                            <span v-else>{{ page }}</span>
                        </button>
                    </template>
                    
                    <button 
                        @click="handlePageChange(currentPage + 1)"
                        :disabled="currentPage === totalPages"
                        class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 transition-colors"
                    >
                      <span class="sr-only">下一页</span>
                      <span class="i-carbon-chevron-right h-5 w-5"></span>
                    </button>
                  </nav>
                </div>
              </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// import axios from 'axios';
import request from '@/utils/request';
import { useWechatLoginStore } from '@/stores/wechatLoginStore';
import { wechatService } from '@/services/wechatService';

// 文章数据接口
interface Article {
  aid: string;
  title: string;
  link: string;
  update_time: number;
  digest: string;
  downloading?: boolean;
  downloaded?: boolean;
  uploadedUrl?: string; // For Aliyun upload result
  is_education?: boolean; // AI分析结果
}

const route = useRoute();
const router = useRouter();
const wechatStore = useWechatLoginStore();

const fakeid = route.query.fakeid as string;
const nickname = route.query.nickname as string;

// 配置项
const downloadPath = ref(''); 
const isSaveToLocal = ref(true);
const isUploadToAliyun = ref(false);

const articles = ref<Article[]>([]);
const loading = ref(false);
const analyzing = ref(false);
const exporting = ref(false);

// 分页
const currentPage = ref(1);
const pageSize = 15;
const totalCount = ref(0);

// 获取ai返回的所有教育文章aid
const educationAids = ref<string[]>([]);
// 是否点击了AI分析教育相关文章
const isClickedAnalyzeEducation = ref(false);

const totalPages = computed(() => {
    return Math.ceil(totalCount.value / pageSize);
});

// 监听 downloadPath 变化并保存到数据库
watch(downloadPath, async (newPath) => {
    if (isSaveToLocal.value && wechatStore.userInfo) {
        // 优先使用 uin (唯一ID), 降级使用 nick_name
        const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
        if (userId && newPath) {
            try {
                // 调用 API 保存到数据库
                await request.post('/system/download-path', {
                    user_id: userId,
                    download_path: newPath
                });
                console.log('下载路径已保存到数据库:', newPath);
            } catch (error) {
                console.error('保存下载路径失败:', error);
            }
        }
    }
    // 路径变化时重新检查下载状态
    if (newPath && articles.value.length > 0) {
        checkDownloadStatus();
    }
});

// 监听 isSaveToLocal 变化并保存到数据库
watch(isSaveToLocal, async (newValue) => {
    if (wechatStore.userInfo) {
        const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
        if (userId) {
            try {
                // 调用 API 保存到数据库（"1" 表示是，"2" 表示否）
                await request.post('/system/save-to-local', {
                    user_id: userId,
                    save_to_local: newValue ? "1" : "2"
                });
                console.log('保存到本地设置已保存到数据库:', newValue ? "1" : "2");
            } catch (error) {
                console.error('保存保存到本地设置失败:', error);
            }
        }
    }
});

// 监听 isUploadToAliyun 变化并保存到数据库
watch(isUploadToAliyun, async (newValue) => {
    if (wechatStore.userInfo) {
        const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
        if (userId) {
            try {
                // 调用 API 保存到数据库（"1" 表示是，"2" 表示否）
                await request.post('/system/upload-to-aliyun', {
                    user_id: userId,
                    upload_to_aliyun: newValue ? "1" : "2"
                });
                console.log('上传到阿里云设置已保存到数据库:', newValue ? "1" : "2");
            } catch (error) {
                console.error('保存上传到阿里云设置失败:', error);
            }
        }
    }
});

// 检查文章下载状态
const checkDownloadStatus = async () => {
    if (!downloadPath.value || !nickname || articles.value.length === 0) return;

    try {
        const articleList = articles.value.map(a => ({ aid: a.aid, title: a.title }));
        const downloadedAids = await request.post<{aid: string}[]>('/system/check-downloaded', {
            base_path: downloadPath.value,
            wx_public_name: nickname,
            articles: articleList
        });
        console.log('downloadedAids---', downloadedAids);
        console.log('articles---', articles.value);
        if (Array.isArray(downloadedAids)) {
            articles.value.forEach(article => {
                article.downloaded = false;
                if (downloadedAids.some(d => d === article.aid)) {
                    article.downloaded = true;
                }
            });
        }
    } catch (error) {
        console.error('Failed to check download status:', error);
    }
};
const checkEducationListStatus = async () => {
    if (!isClickedAnalyzeEducation.value) return;
    let educationCount = 0;
    articles.value.forEach(article => {
        if (educationAids.value.includes(article.aid)) {
            article.is_education = true;
            educationCount++;
        } else {
            article.is_education = false; 
        }
    });
}

const formatDate = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleString();
};

const selectDownloadFolder = async () => {
    try {
        const res = await request.get<{path: string}>('/system/select-folder');
        if (res && res.path) {
            downloadPath.value = res.path;
        }
    } catch (error) {
        console.error('Failed to select folder:', error);
        alert(error);
    }
};

const fetchArticles = async (page = 1) => {
  if (!fakeid) return;
  
  loading.value = true;
  currentPage.value = page;
  
  const begin = (page - 1) * pageSize;
  
  try {
    const dataList = await request.post('/get-wx-article-list', {
      query: "",
      begin: begin, 
      count: pageSize, 
      wx_public_id: fakeid
    });
    
    // Response structure based on user feedback:
    // { "total_count": 9215, "publish_count": 10, "masssend_count": 9205, "publish_list": [], "featured_count": 0 }
    if (dataList) {
        if (dataList.total_count !== undefined) {
             totalCount.value = dataList.total_count;
        }
        
        if (dataList.publish_list) {
            const list = dataList.publish_list.map((item: any) => {
                const info = item.appmsgex ? item.appmsgex[0] : item;
                // Some items might be textual or different types, ensure safe access
                if (!info) return null;
                
                return {
                    aid: info.aid || (info.appmsgid + '_' + info.itemidx),
                    title: info.title || '无标题',
                    link: info.link,
                    update_time: info.update_time,
                    digest: info.digest,
                    downloading: false,
                    downloaded: false
                };
            }).filter((item: any) => item !== null);
            articles.value = list;
            // 获取列表后检查下载状态
            if (isSaveToLocal.value && downloadPath.value) {
                checkDownloadStatus();
            }
        } else {
            articles.value = [];
        }
        checkEducationListStatus();
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

  // 校验
  if (isSaveToLocal.value && !downloadPath.value) {
      alert('请先选择下载保存路径');
      return;
  }
  
  article.downloading = true;
  try {
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
    
    // Expecting response might contain upload url if is_upload_to_aliyun is true
    const res = await request.post('/get-wx-article-detail-by-link', {
        article_link: article.link,
        wx_public_id: fakeid,
        wx_public_name: nickname,
        is_save_to_local: isSaveToLocal.value,
        is_upload_to_aliyun: isUploadToAliyun.value,
        save_to_local_path: downloadPath.value
    });
    
    article.downloaded = true;
    
    if (isUploadToAliyun.value && res && res.uploaded_url) {
        article.uploadedUrl = res.uploaded_url;
        // alert(`上传成功: ${res.uploaded_url}`);
    }
    
  } catch (error) {
    console.error('Download/Upload failed:', error);
    alert('操作失败');
  } finally {
    article.downloading = false;
  }

};

const analyzeEducation = async () => {
    if (articles.value.length === 0) return;
    
    analyzing.value = true;
    try {
        const articleList = articles.value.map(a => ({ aid: a.aid, title: a.title }));
        // API response format: { code: 0, msg: "success", data: ["aid1", "aid2"] }
        // # AI分析教育相关文章
        // const res = await request.post<{code: number, msg: string, data: string[]}>('/analyze-education-content', {
        //     articles: articleList
        // });
      

        // # AI通过ID分析教育相关文章
        const res = await request.post<{code: number, msg: string, data: string[]}>('/analyze-education-content-by-id', {
            wx_public_id: fakeid
        });

        let educationCount = 0;
        if (res && res.data) {
            isClickedAnalyzeEducation.value = true;
            // const educationAids = res.data;
            educationAids.value = res.data;
            checkEducationListStatus();
            alert(`分析完成！\n 公众号 ${nickname} 共有 ${educationAids.value.length} 条教育相关文章。`);
        } else {
            alert('分析完成，未发现教育相关文章或返回数据异常。');
        }
    } catch (error) {
        console.error('AI Analysis failed:', error);
        alert('AI分析请求失败，请稍后重试。');
    } finally {
        analyzing.value = false;
    }
};

const exportArticles = async () => {
    if (!downloadPath.value) {
        alert('请先设置下载地址！');
        return;
    }
    
    exporting.value = true;
    try {
        console.log('========== 开始导出文章信息 ==========');
        console.log('公众号ID:', fakeid);
        console.log('公众号名称:', nickname);
        console.log('保存路径:', downloadPath.value);
        console.log('');
        
        // 调用 wechatService 循环获取所有文章
        const allArticles = await wechatService.getAllArticles(
            fakeid,
            (current: number, total: number, message: string) => {
                // 进度回调
                console.log(`[进度] ${message}`);
            }
        );
        
        console.log('');
        console.log('========== 文章导出结果 ==========');
        console.log(`共获取 ${allArticles.length} 篇文章`);
        console.log('');
        
        allArticles.forEach((article, index) => {
            console.log(`[${index + 1}] ${article.title}`);
            console.log(`    文章ID: ${article.aid}`);
            console.log(`    发布时间: ${article.publish_time || '未知'}`);
            console.log(`    链接: ${article.link}`);
            console.log('');
        });
        
        console.log('================================');
        console.log('开始导出到Excel...');
        
        // 调用后端接口导出到Excel
        const exportResult = await wechatService.exportArticlesToExcel(allArticles, downloadPath.value, nickname || '公众号文章');
        
        console.log('导出结果:', exportResult);
        
        if (exportResult && exportResult.code === 0 && exportResult.data) {
            console.log('Excel导出成功！');
            console.log(`文件路径: ${exportResult.data.file_path}`);
            console.log('================================');
            
            alert(`导出成功！\n\n共获取 ${allArticles.length} 篇文章\n已导出到Excel文件：${exportResult.data.file_path}`);
        } else {
            console.error('导出Excel失败:', exportResult);
            alert('导出Excel失败，请查看控制台详情。');
        }
    } catch (error) {
        console.error('导出失败:', error);
        alert('导出请求失败，请稍后重试。\n错误信息：' + (error as Error).message);
    } finally {
        exporting.value = false;
    }
};

const handlePageChange = (newPage: number) => {
    if (newPage > 0 && newPage <= totalPages.value) {
        fetchArticles(newPage);
    }
};

onMounted(async () => {
    // 从数据库恢复保存的路径和设置
    if (wechatStore.userInfo) {
        const userId = wechatStore.userInfo.uin || wechatStore.userInfo.nick_name;
        if (userId) {
            try {
                // 加载下载路径
                const pathRes = await request.get<{success: boolean, path?: string}>('/system/download-path', {
                    params: { user_id: userId }
                });
                if (pathRes.success && pathRes.path) {
                    downloadPath.value = pathRes.path;
                    console.log('从数据库加载下载路径:', pathRes.path);
                }

                // 加载是否保存到本地设置
                const saveRes = await request.get<{success: boolean, value?: string}>('/system/save-to-local', {
                    params: { user_id: userId }
                });
                if (saveRes.success && saveRes.value) {
                    isSaveToLocal.value = saveRes.value === "1";
                    console.log('从数据库加载保存到本地设置:', isSaveToLocal.value);
                }

                // 加载是否上传到阿里云设置
                const uploadRes = await request.get<{success: boolean, value?: string}>('/system/upload-to-aliyun', {
                    params: { user_id: userId }
                });
                if (uploadRes.success && uploadRes.value) {
                    isUploadToAliyun.value = uploadRes.value === "1";
                    console.log('从数据库加载上传到阿里云设置:', isUploadToAliyun.value);
                }
            } catch (error) {
                console.error('加载用户设置失败:', error);
            }
        }
    }

    if (fakeid) {
        fetchArticles(1);
    }
});
</script>



<style scoped>
/* AI文本闪光效果的动画 */
.ai-text-shimmer {
  /* 渐变色：深蓝 -> 亮青 -> 白色（闪光） -> 亮青 -> 深蓝 */
  background: linear-gradient(
    110deg, 
    #1e40af 0%,    /* deep-blue-800 */
    #3b82f6 30%,   /* blue-500 */
    #22d3ee 45%,   /* cyan-400 */
    #ffffff 50%,   /* 白色（闪光点） */
    #22d3ee 55%,   /* cyan-400 */
    #3b82f6 70%,   /* blue-500 */
    #1e40af 100%   /* deep-blue-800 */
  );
  background-size: 200% auto;
  background-position: -200% center;
  color: #2563eb;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 2.5s linear infinite;
  text-shadow: 0 0 10px rgba(59, 130, 246, 0.3); /* 柔和发光效果 */
  font-weight: 800; /* 加粗以提升可见度 */
}

@keyframes shimmer {
  to {
    background-position: 200% center;
  }
}
</style>
