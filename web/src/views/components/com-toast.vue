<template>
  <Transition name="toast">
    <div
      v-if="visible"
      :class="[
        'fixed top-[20%] left-1/2 -translate-x-1/2 px-6 py-4 rounded-lg shadow-2xl flex items-center gap-3 z-[9999]',
        type === 'success'
          ? 'bg-green-600 text-white'
          : 'bg-red-600 text-white',
      ]"
    >
      <span
        :class="
          type === 'success'
            ? 'i-carbon-checkmark-filled'
            : 'i-carbon-error-filled'
        "
      ></span>
      <span class="font-medium">{{ message }}</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from "vue";

const visible = ref(false);
const message = ref("");
const type = ref<"success" | "error">("success");
let timer: NodeJS.Timeout | null = null;

const open = (
  msg: string,
  toastType: "success" | "error" = "success",
  duration = 3000
) => {
  if (timer) clearTimeout(timer);

  message.value = msg;
  type.value = toastType;
  visible.value = true;

  timer = setTimeout(() => {
    visible.value = false;
  }, duration);
};

defineExpose({
  open,
});
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}
</style>
