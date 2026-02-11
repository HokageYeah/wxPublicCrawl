<template>
  <div class="min-h-screen bg-black dark:bg-gray-900">
    <div class="max-w-2xl mx-auto px-6 py-8">
      <h1 class="text-3xl font-bold mb-8 text-center text-white">
        喜马拉雅扫码登录
      </h1>

      <!-- Loading state -->
      <div
        v-if="xmlyStore.isLoading"
        class="card p-12 flex justify-center items-center bg-gray-900 border border-gray-700 rounded-xl"
      >
        <LoadingSpinner :label="loadingLabel" />
      </div>

      <!-- Error state -->
      <div
        v-else-if="xmlyStore.error"
        class="card p-8 bg-gray-900 border border-gray-700 rounded-xl"
      >
        <div class="flex items-center text-red-400 mb-4">
          <div class="i-carbon-warning-filled mr-2 text-2xl"></div>
          <span class="text-lg font-semibold text-white"
            >登录过程中出现错误</span
          >
        </div>
        <p class="mb-4 text-sm text-gray-400">{{ xmlyStore.error }}</p>
        <button
          @click="restart"
          class="btn-primary bg-orange-600 hover:bg-orange-700"
        >
          重试
        </button>
      </div>

      <!-- Login success state -->
      <div v-else-if="xmlyStore.isLoggedIn" class="col-span-1 md:col-span-1">
        <XlyUserInfoDisplay
          :user-info="xmlyStore.userInfo"
          @continue="onContinue"
          @logout="onLogout"
        />

        <div
          class="mt-4 card p-4 bg-gray-800 hover:bg-gray-750 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 rounded-xl border border-gray-700"
        >
          <details class="group">
            <summary
              class="cursor-pointer text-sm text-gray-300 font-medium flex items-center"
            >
              <span class="i-carbon-view mr-2"></span>
              <span>查看完整用户数据</span>
              <span
                class="ml-2 transition-transform duration-300 group-open:rotate-180"
              >
                <span class="i-carbon-chevron-down"></span>
              </span>
            </summary>
            <pre
              class="mt-3 text-xs overflow-auto bg-blue-900/30 p-3 rounded-md text-gray-300 border border-gray-600"
              >{{ JSON.stringify(xmlyStore.userInfo, null, 2) }}</pre
            >
          </details>
        </div>
      </div>

      <!-- QR code login state -->
      <template v-else>
        <div class="grid grid-cols-1 md:grid-cols-1 gap-8">
          <div class="col-span-1 md:col-span-1">
            <UniversalQRCodeDisplay
              v-if="
                xmlyStore.qrCodeImg &&
                xmlyStore.currentStep === XmlyLoginStep.QRCODE_GENERATED
              "
              :qr-code-img="xmlyStore.qrCodeImg"
              :status="xmlyStore.qrCodeStatus"
              :status-text="xmlyStore.qrCodeStateText"
              :error-message="xmlyStore.error"
              :polling-count="xmlyStore.pollingCount"
              @refresh="restart"
            />

            <div
              v-if="xmlyStore.qrCodeImg"
              class="card mt-8 p-6 bg-gray-900 border border-gray-700 rounded-xl"
            >
              <h3 class="text-lg font-semibold mb-4">登录步骤</h3>
              <ol class="space-y-3">
                <li
                  class="flex items-center"
                  :class="{
                    'text-orange-500':
                      xmlyStore.currentStep === XmlyLoginStep.INIT ||
                      completedSteps.includes(XmlyLoginStep.INIT),
                  }"
                >
                  <div
                    class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border"
                    :class="stepStyle(XmlyLoginStep.INIT)"
                  >
                    {{
                      completedSteps.includes(XmlyLoginStep.INIT) ? "✓" : "1"
                    }}
                  </div>
                  <span class="text-gray-300">初始化登录流程</span>
                </li>
                <li
                  class="flex items-center"
                  :class="{
                    'text-orange-500':
                      xmlyStore.currentStep ===
                        XmlyLoginStep.QRCODE_GENERATED ||
                      completedSteps.includes(XmlyLoginStep.QRCODE_GENERATED),
                  }"
                >
                  <div
                    class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border"
                    :class="stepStyle(XmlyLoginStep.QRCODE_GENERATED)"
                  >
                    {{
                      completedSteps.includes(XmlyLoginStep.QRCODE_GENERATED)
                        ? "✓"
                        : "2"
                    }}
                  </div>
                  <span class="text-gray-300">生成二维码</span>
                </li>
                <li
                  class="flex items-center"
                  :class="{
                    'text-orange-500':
                      xmlyStore.currentStep === XmlyLoginStep.QRCODE_SCANNED ||
                      completedSteps.includes(XmlyLoginStep.QRCODE_SCANNED),
                  }"
                >
                  <div
                    class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border"
                    :class="stepStyle(XmlyLoginStep.QRCODE_SCANNED)"
                  >
                    {{
                      completedSteps.includes(XmlyLoginStep.QRCODE_SCANNED)
                        ? "✓"
                        : "3"
                    }}
                  </div>
                  <span class="text-gray-300">扫描二维码</span>
                </li>
                <li
                  class="flex items-center"
                  :class="{
                    'text-orange-500':
                      xmlyStore.currentStep === XmlyLoginStep.LOGIN_SUCCESS ||
                      completedSteps.includes(XmlyLoginStep.LOGIN_SUCCESS),
                  }"
                >
                  <div
                    class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border"
                    :class="stepStyle(XmlyLoginStep.LOGIN_SUCCESS)"
                  >
                    {{
                      completedSteps.includes(XmlyLoginStep.LOGIN_SUCCESS)
                        ? "✓"
                        : "4"
                    }}
                  </div>
                  <span class="text-gray-300">登录成功</span>
                </li>
              </ol>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useXmlyLoginStore } from "@/stores/xmlyLoginStore";
import { XmlyLoginStep } from "@/types/xmly";
import UniversalQRCodeDisplay from "@/components/UniversalQRCodeDisplay.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import XlyUserInfoDisplay from "@/components/XmlyUserInfoDisplay.vue";

const xmlyStore = useXmlyLoginStore();

const loadingLabel = computed(() => {
  switch (xmlyStore.currentStep) {
    case XmlyLoginStep.INIT:
      return "正在生成二维码...";
    default:
      return "加载中...";
  }
});

const getStepOrder = (step: XmlyLoginStep): number => {
  const orderMap: Record<XmlyLoginStep, number> = {
    [XmlyLoginStep.INIT]: 0,
    [XmlyLoginStep.QRCODE_GENERATED]: 1,
    [XmlyLoginStep.QRCODE_SCANNED]: 2,
    [XmlyLoginStep.LOGIN_SUCCESS]: 3,
    [XmlyLoginStep.ERROR]: -1,
  };
  return orderMap[step];
};

const isStepCompleted = (step: XmlyLoginStep): boolean => {
  return getStepOrder(xmlyStore.currentStep) > getStepOrder(step);
};

const completedSteps = computed(() => {
  const steps: XmlyLoginStep[] = [];

  if (
    xmlyStore.currentStep === XmlyLoginStep.QRCODE_GENERATED ||
    isStepCompleted(XmlyLoginStep.QRCODE_GENERATED)
  ) {
    steps.push(XmlyLoginStep.INIT);
  }

  if (
    xmlyStore.currentStep === XmlyLoginStep.QRCODE_SCANNED ||
    isStepCompleted(XmlyLoginStep.QRCODE_SCANNED)
  ) {
    steps.push(XmlyLoginStep.QRCODE_GENERATED);
  }

  if (
    xmlyStore.currentStep === XmlyLoginStep.LOGIN_SUCCESS ||
    isStepCompleted(XmlyLoginStep.LOGIN_SUCCESS)
  ) {
    steps.push(XmlyLoginStep.QRCODE_SCANNED);
  }

  return steps;
});

const stepStyle = (step: XmlyLoginStep) => {
  if (completedSteps.value.includes(step)) {
    return "bg-orange-500 text-white border-orange-500";
  }

  if (xmlyStore.currentStep === step) {
    return "border-orange-500 text-orange-500";
  }

  return "border-gray-600 text-gray-400";
};

const restart = async () => {
  await xmlyStore.reset();
  await xmlyStore.startLoginFlow();
};

const router = useRouter();

const onContinue = () => {
  console.log("Login complete, redirecting to search...");
  router.push({ name: "xmly-crawl-search-album" });
};

const onLogout = async () => {
  await xmlyStore.logout();
  console.log("用户已退出登录");
  // 退出登录后自动重新开始登录流程
  await xmlyStore.startLoginFlow();
};

onMounted(async () => {
  await xmlyStore.initialize();

  if (!xmlyStore.isLoggedIn) {
    console.log("XmlyLogin组件已挂载，启动登录流程");
    xmlyStore.startLoginFlow();
  } else {
    console.log("用户已登录，无需启动登录流程");
  }
});

onUnmounted(() => {
  console.log("XmlyLogin组件已卸载，清理资源");
  xmlyStore.cleanup();
});
</script>
