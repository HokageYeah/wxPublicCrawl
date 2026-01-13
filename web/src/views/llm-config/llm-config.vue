<template>
  <div class="min-h-screen bg-black text-white">
    <!-- 内容容器 -->
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-2">
          <div>
            <h1 class="text-3xl font-bold text-blue-400">LLM配置管理</h1>
            <p class="text-gray-400 mt-1">管理AI大模型配置，支持多模型切换</p>
          </div>
          <button
            @click="openCreateDialog"
            class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            <span class="i-carbon-add text-lg"></span>
            新建配置
          </button>
        </div>

        <!-- 激活配置卡片 -->
        <div
          v-if="activeConfig"
          class="mt-6 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span
                class="i-carbon-circle-check text-2xl text-green-400"
              ></span>
              <div>
                <div class="text-sm text-gray-400">当前激活配置</div>
                <div class="font-semibold text-lg">
                  {{ activeConfig.model_name }}
                </div>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <span
                class="px-3 py-1 text-xs font-medium bg-green-500/20 text-green-400 rounded-full"
              >
                {{ activeConfig.model_type }}
              </span>
              <span class="text-sm text-gray-400">{{
                activeConfig.description || "无描述"
              }}</span>
            </div>
          </div>
        </div>
        <div
          v-else
          class="mt-6 p-4 bg-yellow-900/20 border border-yellow-500/30 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <span class="i-carbon-warning text-2xl text-yellow-400"></span>
            <div>
              <div class="text-sm text-gray-400">暂无激活配置</div>
              <div class="font-medium text-yellow-400">
                请创建并激活一个配置以使用AI功能
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="mb-6 bg-gray-900/50 rounded-lg p-4 border border-gray-800">
        <div class="flex flex-wrap gap-4 items-center">
          <div class="flex-1 min-w-[200px]">
            <label class="block text-xs text-gray-400 mb-1">模型类型</label>
            <select
              v-model="filters.model_type"
              @change="fetchConfigs"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部类型</option>
              <option v-for="type in modelTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-xs text-gray-400 mb-1">状态</label>
            <select
              v-model="filters.is_active"
              @change="fetchConfigs"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option :value="null">全部状态</option>
              <option :value="true">已激活</option>
              <option :value="false">未激活</option>
            </select>
          </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-xs text-gray-400 mb-1">每页显示</label>
            <select
              v-model="filters.limit"
              @change="fetchConfigs"
              class="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option :value="10">10条</option>
              <option :value="20">20条</option>
              <option :value="50">50条</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 配置列表 -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <span
          class="i-carbon-circle-dash animate-spin text-5xl text-blue-500"
        ></span>
      </div>

      <div
        v-else-if="configs.length === 0"
        class="flex flex-col items-center justify-center py-20 border-2 border-dashed border-gray-800 rounded-lg"
      >
        <span class="i-carbon-ai-services text-6xl text-gray-600 mb-4"></span>
        <p class="text-gray-400 text-lg mb-2">暂无配置</p>
        <p class="text-gray-500 text-sm">点击"新建配置"按钮创建第一个LLM配置</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="config in configs"
          :key="config.id"
          class="group bg-gray-900 border rounded-xl overflow-hidden transition-all duration-300 hover:-translate-y-1"
          :class="[
            config.is_active
              ? 'border-green-500 shadow-lg shadow-green-500/20'
              : 'border-gray-800 hover:border-blue-500/50 hover:shadow-xl hover:shadow-blue-500/10',
          ]"
        >
          <!-- 卡片头部 -->
          <div class="relative p-5 bg-gray-800 border-b border-gray-700">
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="w-12 h-12 rounded-lg bg-blue-600 flex items-center justify-center"
                >
                  <span class="i-carbon-ai-services text-2xl"></span>
                </div>
                <div>
                  <h3
                    class="font-bold text-lg text-white group-hover:text-blue-400 transition-colors"
                  >
                    {{ config.model_name }}
                  </h3>
                  <span class="text-xs text-gray-400">{{
                    config.model_type
                  }}</span>
                </div>
              </div>
              <div
                v-if="config.is_active"
                class="px-2 py-1 bg-green-500/20 border border-green-500/30 rounded-full flex items-center gap-1"
              >
                <span
                  class="i-carbon-circle-check text-xs text-green-400"
                ></span>
                <span class="text-xs text-green-400">已激活</span>
              </div>
            </div>
          </div>

          <!-- 卡片内容 -->
          <div class="p-5 space-y-3">
            <div class="flex items-center gap-2 text-sm">
              <span class="i-carbon-api text-gray-400"></span>
              <span class="text-gray-300 font-medium">API Key:</span>
              <span class="text-gray-500 font-mono">{{
                maskedApiKey(config.ai_api_key)
              }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <span class="i-carbon-link text-gray-400"></span>
              <span class="text-gray-300 font-medium">Base URL:</span>
              <span class="text-gray-500 truncate">{{
                config.ai_base_url || "未设置"
              }}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
              <span class="i-carbon-temperature text-gray-400"></span>
              <span class="text-gray-300 font-medium">Temperature:</span>
              <span class="text-gray-500">{{ config.temperature }}</span>
              <span class="text-gray-300 font-medium ml-2">Max Tokens:</span>
              <span class="text-gray-500">{{ config.max_tokens }}</span>
            </div>
            <div v-if="config.description" class="text-sm text-gray-500 italic">
              {{ config.description }}
            </div>
          </div>

          <!-- 卡片操作 -->
          <div
            class="px-5 py-4 bg-gray-800/50 border-t border-gray-700 flex items-center justify-between"
          >
            <button
              v-if="!config.is_active"
              @click="activateConfig(config.id)"
              class="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              title="激活此配置"
            >
              <span class="i-carbon-power"></span>
              激活
            </button>
            <div class="flex items-center gap-2">
              <button
                @click="openEditDialog(config)"
                class="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                title="编辑配置"
              >
                <span class="i-carbon-edit"></span>
                编辑
              </button>
              <button
                @click="deleteConfig(config.id)"
                class="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                title="删除配置"
              >
                <span class="i-carbon-trash-can"></span>
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div
        v-if="total > filters.limit"
        class="mt-8 flex items-center justify-center gap-4"
      >
        <button
          @click="changePage(-1)"
          :disabled="currentPage === 1"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
        >
          <span class="i-carbon-chevron-left"></span>
          上一页
        </button>
        <span class="text-gray-400">
          第 {{ currentPage }} 页 / 共 {{ Math.ceil(total / filters.limit) }} 页
        </span>
        <button
          @click="changePage(1)"
          :disabled="currentPage >= Math.ceil(total / filters.limit)"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
        >
          下一页
          <span class="i-carbon-chevron-right"></span>
        </button>
      </div>

      <!-- 创建/编辑对话框 -->
      <div
        v-if="showDialog"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
        @click.self="closeDialog"
      >
        <div
          class="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl"
        >
          <!-- 对话框头部 -->
          <div
            class="px-6 py-4 border-b border-gray-700 flex items-center justify-between bg-gray-800"
          >
            <h2 class="text-xl font-bold text-white">
              {{ isEditMode ? "编辑配置" : "新建配置" }}
            </h2>
            <button
              @click="closeDialog"
              class="text-gray-400 hover:text-white transition-colors"
            >
              <span class="i-carbon-close text-2xl"></span>
            </button>
          </div>

          <!-- 对话框内容 -->
          <div class="p-6 overflow-y-auto max-h-[70vh]">
            <form @submit.prevent="saveConfig" class="space-y-4">
              <!-- 基本信息 -->
              <div class="grid grid-cols-2 gap-4">
                <div class="col-span-2">
                  <label class="block text-sm font-medium text-gray-300 mb-1"
                    >配置描述 <span class="text-red-400">*</span></label
                  >
                  <input
                    v-model="formData.description"
                    type="text"
                    placeholder="例如：GPT-4 生产环境配置"
                    class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-1"
                    >模型类型 <span class="text-red-400">*</span></label
                  >
                  <select
                    v-model="formData.model_type"
                    class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">请选择</option>
                    <option
                      v-for="type in modelTypes"
                      :key="type"
                      :value="type"
                    >
                      {{ type }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-1"
                    >模型名称 <span class="text-red-400">*</span></label
                  >
                  <input
                    v-model="formData.model_name"
                    type="text"
                    placeholder="例如：gpt-4-turbo"
                    class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>

              <!-- API 配置 -->
              <div class="space-y-4">
                <h3
                  class="text-base font-semibold text-gray-300 flex items-center gap-2"
                >
                  <span class="i-carbon-api text-blue-400"></span>
                  API 配置
                </h3>

                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-1"
                    >API Key <span class="text-red-400">*</span></label
                  >
                  <div class="relative">
                    <input
                      v-model="formData.ai_api_key"
                      :type="showApiKey ? 'text' : 'password'"
                      placeholder="sk-..."
                      class="w-full px-4 py-2.5 pr-10 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                    <button
                      type="button"
                      @click="showApiKey = !showApiKey"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                    >
                      <span
                        :class="
                          showApiKey ? 'i-carbon-view-off' : 'i-carbon-view'
                        "
                      ></span>
                    </button>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-1"
                    >Base URL</label
                  >
                  <input
                    v-model="formData.ai_base_url"
                    type="url"
                    placeholder="https://api.openai.com/v1"
                    class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-1"
                    >API Endpoint</label
                  >
                  <input
                    v-model="formData.api_endpoint"
                    type="text"
                    placeholder="/chat/completions"
                    class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <!-- 模型参数 -->
              <div class="space-y-4">
                <h3
                  class="text-base font-semibold text-gray-300 flex items-center gap-2"
                >
                  <span class="i-carbon-settings text-blue-400"></span>
                  模型参数
                </h3>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-300 mb-1"
                      >Temperature ({{ formData.temperature }})</label
                    >
                    <input
                      v-model.number="formData.temperature"
                      type="range"
                      min="0"
                      max="200"
                      step="10"
                      class="w-full"
                    />
                    <div
                      class="flex justify-between text-xs text-gray-500 mt-1"
                    >
                      <span>0 (确定性)</span>
                      <span>200 (随机性)</span>
                    </div>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-300 mb-1"
                      >Top P ({{ formData.top_p }})</label
                    >
                    <input
                      v-model.number="formData.top_p"
                      type="range"
                      min="0"
                      max="100"
                      step="1"
                      class="w-full"
                    />
                    <div
                      class="flex justify-between text-xs text-gray-500 mt-1"
                    >
                      <span>0</span>
                      <span>100</span>
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-300 mb-1"
                      >Max Tokens</label
                    >
                    <input
                      v-model.number="formData.max_tokens"
                      type="number"
                      placeholder="2000"
                      class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-300 mb-1"
                      >Max History</label
                    >
                    <input
                      v-model.number="formData.max_history"
                      type="number"
                      placeholder="10"
                      class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              <!-- 高级选项 -->
              <div class="space-y-4">
                <h3
                  class="text-base font-semibold text-gray-300 flex items-center gap-2"
                >
                  <span class="i-carbon-settings-adjust text-blue-400"></span>
                  高级选项
                </h3>

                <div class="flex flex-wrap gap-6">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      v-model="formData.enable_history"
                      type="checkbox"
                      class="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-600 focus:ring-blue-500"
                    />
                    <span class="text-sm text-gray-300">启用历史对话</span>
                  </label>

                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      v-model="formData.enable_stream"
                      type="checkbox"
                      class="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-600 focus:ring-blue-500"
                    />
                    <span class="text-sm text-gray-300">启用流式输出</span>
                  </label>

                  <label class="flex items-center gap-2 cursor-pointer">
                    <input
                      v-model="formData.is_active"
                      type="checkbox"
                      class="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-600 focus:ring-blue-500"
                    />
                    <span class="text-sm text-gray-300">激活此配置</span>
                  </label>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-1"
                    >系统提示词</label
                  >
                  <textarea
                    v-model="formData.system_prompt"
                    rows="4"
                    placeholder="You are a helpful assistant..."
                    class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  ></textarea>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-1"
                    >自定义参数 (JSON)</label
                  >
                  <textarea
                    v-model="formData.custom_parameters"
                    rows="3"
                    placeholder='{"key": "value"}'
                    class="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm"
                  ></textarea>
                </div>
              </div>
            </form>
          </div>

          <!-- 对话框底部 -->
          <div
            class="px-6 py-4 border-t border-gray-700 flex items-center justify-end gap-3 bg-gray-800/50"
          >
            <button
              @click="closeDialog"
              class="px-6 py-2.5 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors"
            >
              取消
            </button>
            <button
              @click="saveConfig"
              :disabled="saving"
              class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <span
                v-if="saving"
                class="i-carbon-circle-dash animate-spin"
              ></span>
              {{ saving ? "保存中..." : "保存" }}
            </button>
          </div>
        </div>
      </div>

      <!-- Toast 提示 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import request from "@/utils/request";
import Toast from "@/utils/toast";

// 类型定义
interface LLMConfig {
  id: number;
  user_id?: number | null;
  is_active: boolean;
  model_type: string;
  model_name: string;
  ai_api_key: string;
  ai_base_url?: string;
  api_endpoint?: string;
  temperature: number;
  max_tokens: number;
  top_p: number;
  enable_history: boolean;
  max_history: number;
  enable_stream: boolean;
  system_prompt?: string;
  custom_parameters?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

// 状态
const loading = ref(false);
const configs = ref<LLMConfig[]>([]);
const activeConfig = ref<LLMConfig | null>(null);
const modelTypes = ref<string[]>([]);
const total = ref(0);
const currentPage = ref(1);

// 筛选条件
const filters = ref({
  model_type: "",
  is_active: null as boolean | null,
  limit: 10,
  skip: 0,
});

// 对话框
const showDialog = ref(false);
const isEditMode = ref(false);
const showApiKey = ref(false);
const saving = ref(false);

// 表单数据
const formData = ref<Partial<LLMConfig>>({
  description: "",
  model_type: "",
  model_name: "",
  ai_api_key: "",
  ai_base_url: "",
  api_endpoint: "",
  temperature: 70,
  max_tokens: 2000,
  top_p: 100,
  enable_history: true,
  max_history: 10,
  enable_stream: false,
  system_prompt: "",
  custom_parameters: "",
  is_active: false,
  user_id: null,
});

// 显示 Toast (Adapter for global Toast)
const showToast = (message: string, type: "success" | "error" = "success") => {
  if (type === "error") {
    Toast.error(message);
  } else {
    Toast.success(message);
  }
};

// 脱敏 API Key
const maskedApiKey = (key: string) => {
  if (!key) return "";
  if (key.length <= 8) return "****";
  return key.substring(0, 4) + "****" + key.substring(key.length - 4);
};

// 获取模型类型
const fetchModelTypes = async () => {
  try {
    const result = await request.post<{ model_types: string[] }>(
      "/llm-config/llm-config-model-types"
    );
    modelTypes.value = result.model_types || [];
  } catch (error: any) {
    console.error("获取模型类型失败:", error);
    // 检查是否是表不存在的错误
    const errorMessage = error.message || "";
    if (
      errorMessage.includes("no such table") ||
      errorMessage.includes("llm_configuration")
    ) {
      // 表不存在，静默处理
      console.log("数据库表不存在，将在配置列表获取时自动创建");
    }
  }
};

// 获取配置列表
const fetchConfigs = async () => {
  loading.value = true;
  try {
    const result = await request.post<{ total: number; items: LLMConfig[] }>(
      "/llm-config/llm-config-list",
      {
        user_id: null,
        model_type: filters.value.model_type || undefined,
        is_active: filters.value.is_active,
        skip: filters.value.skip,
        limit: filters.value.limit,
      }
    );
    configs.value = result.items || [];

    // 如果筛选条件是全部，则将激活的卡片排在前面
    if (filters.value.is_active === null) {
      configs.value.sort((a, b) => {
        if (a.is_active === b.is_active) return 0;
        return a.is_active ? -1 : 1;
      });
    }

    total.value = result.total || 0;
  } catch (error: any) {
    console.error("获取配置列表失败:", error);
    // 检查是否是表不存在的错误
    const errorMessage = error.message || "";
    if (
      errorMessage.includes("no such table") ||
      errorMessage.includes("llm_configuration")
    ) {
      showToast("数据库表不存在，已自动创建，请重试", "success");
      // 延迟1秒后重新获取
      setTimeout(() => {
        fetchConfigs();
      }, 1000);
    } else {
      showToast(error.message || "获取配置列表失败", "error");
    }
  } finally {
    loading.value = false;
  }
};

// 获取激活配置
const fetchActiveConfig = async () => {
  try {
    const result = await request.post<LLMConfig>(
      "/llm-config/llm-config-active",
      { user_id: null }
    );
    activeConfig.value = result;
  } catch (error: any) {
    // 检查是否是表不存在的错误
    const errorMessage = error.message || "";
    if (
      errorMessage.includes("no such table") ||
      errorMessage.includes("llm_configuration")
    ) {
      // 表不存在，静默处理，等待fetchConfigs重试
      activeConfig.value = null;
    } else {
      // 如果没有激活配置，不算错误
      activeConfig.value = null;
    }
  }
};

// 切换页码
const changePage = (delta: number) => {
  const newPage = currentPage.value + delta;
  const maxPage = Math.ceil(total.value / filters.value.limit);

  if (newPage >= 1 && newPage <= maxPage) {
    currentPage.value = newPage;
    filters.value.skip = (newPage - 1) * filters.value.limit;
    fetchConfigs();
  }
};

// 打开创建对话框
const openCreateDialog = () => {
  isEditMode.value = false;
  formData.value = {
    description: "",
    model_type: "",
    model_name: "",
    ai_api_key: "",
    ai_base_url: "",
    api_endpoint: "",
    temperature: 70,
    max_tokens: 2000,
    top_p: 100,
    enable_history: true,
    max_history: 10,
    enable_stream: false,
    system_prompt: "",
    custom_parameters: "",
    is_active: false,
    user_id: null,
  };
  showApiKey.value = false;
  showDialog.value = true;
};

// 打开编辑对话框
const openEditDialog = async (config: LLMConfig) => {
  try {
    // 获取完整配置信息
    const result = await request.post<LLMConfig>("/llm-config/llm-config-get", {
      config_id: config.id,
      user_id: null,
    });

    isEditMode.value = true;
    formData.value = { ...result, config_id: config.id };
    showApiKey.value = false;
    showDialog.value = true;
  } catch (error) {
    console.error("获取配置详情失败:", error);
    showToast("获取配置详情失败", "error");
  }
};

// 保存配置
const saveConfig = async () => {
  saving.value = true;
  try {
    // 验证必填字段
    if (
      !formData.value.description ||
      !formData.value.model_type ||
      !formData.value.model_name ||
      !formData.value.ai_api_key
    ) {
      showToast("请填写所有必填字段", "error");
      saving.value = false;
      return;
    }

    // 解析自定义参数
    let customParameters = formData.value.custom_parameters;
    if (customParameters) {
      try {
        JSON.parse(customParameters);
      } catch (e) {
        showToast("自定义参数必须是有效的 JSON 格式", "error");
        saving.value = false;
        return;
      }
    }

    if (isEditMode.value) {
      // 更新配置
      await request.post("/llm-config/llm-config-update", {
        config_id: formData.value.config_id,
        user_id: null,
        ...formData.value,
      });
      if (formData.value.is_active) {
        showToast("配置已激活，AI助手服务正在重新初始化...");
      } else {
        showToast("配置更新成功");
      }
    } else {
      // 创建配置
      await request.post("/llm-config/llm-config-create", {
        ...formData.value,
      });
      if (formData.value.is_active) {
        showToast("配置已创建并激活，AI助手服务正在重新初始化...");
      } else {
        showToast("配置创建成功");
      }
    }

    closeDialog();
    await fetchConfigs();
    await fetchActiveConfig();
  } catch (error: any) {
    console.error("保存配置失败:", error);
    const errorMessage =
      error.response?.data?.detail || error.message || "保存失败";
    showToast(errorMessage, "error");
  } finally {
    saving.value = false;
  }
};

// 关闭对话框
const closeDialog = () => {
  showDialog.value = false;
  formData.value = {};
};

// 激活配置
const activateConfig = async (configId: number) => {
  if (
    !confirm(
      "确定要激活此配置吗？这将取消当前激活的配置，并重新初始化AI助手服务。"
    )
  )
    return;

  loading.value = true;
  try {
    await request.post("/llm-config/llm-config-switch", {
      config_id: configId,
      user_id: null,
    });
    showToast("配置已激活，AI助手服务正在重新初始化...");
    await fetchConfigs();
    await fetchActiveConfig();
  } catch (error: any) {
    console.error("激活配置失败:", error);
    const errorMessage =
      error.response?.data?.detail || error.message || "激活失败";
    showToast(errorMessage, "error");
  } finally {
    loading.value = false;
  }
};

// 删除配置
const deleteConfig = async (configId: number) => {
  if (!confirm("确定要删除此配置吗？此操作不可恢复。")) return;

  loading.value = true;
  try {
    await request.post("/llm-config/llm-config-delete", {
      config_id: configId,
      user_id: null,
    });
    showToast("配置删除成功");
    await fetchConfigs();
    await fetchActiveConfig();
  } catch (error: any) {
    console.error("删除配置失败:", error);
    const errorMessage =
      error.response?.data?.detail || error.message || "删除失败";
    showToast(errorMessage, "error");
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchModelTypes();
  fetchConfigs();
  fetchActiveConfig();
});
</script>

<style scoped>
/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1f2937;
}

::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

/* 输入框 range 样式 */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  height: 8px;
  background: #374151;
  border-radius: 4px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}

input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  transition: transform 0.2s;
}

input[type="range"]::-moz-range-thumb:hover {
  transform: scale(1.1);
}
</style>
