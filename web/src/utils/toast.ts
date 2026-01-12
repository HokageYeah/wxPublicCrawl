import { createVNode, render } from "vue";
import ToastComponent from "@/views/components/com-toast.vue";

// 创建容器
const container = document.createElement("div");
document.body.appendChild(container);

// 创建虚拟节点
const vm = createVNode(ToastComponent);
// 渲染
render(vm, container);

const Toast = {
  success: (message: string) => {
    vm.component?.exposed?.open(message, "success");
  },
  error: (message: string) => {
    vm.component?.exposed?.open(message, "error");
  },
  info: (message: string) => {
    vm.component?.exposed?.open(message, "success"); // 暂时复用 success 样式作为 info，或者后续扩展
  },
};

export default Toast;
