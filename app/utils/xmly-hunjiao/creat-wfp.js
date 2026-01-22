// 喜马拉雅 WFP 生成器
// 用于生成登录所需的 wfp 参数 (基于浏览器指纹)
//
// 使用方法：
// 1. Node.js 环境: node creat-wfp.js
// 2. Python 调用: 使用 execjs 调用

// ==================== 环境模拟 ====================
if (typeof window === "undefined") {
  // Node.js 环境下模拟浏览器
  window = global;
  window.document = {
    createElement: function (tag) {
      if (tag === "canvas") {
        return {
          getContext: function () {
            return {
              fillText: function () {},
              fillRect: function () {},
              fillStyle: "",
              textBaseline: "",
              font: "",
              globalCompositeOperation: "",
              beginPath: function () {},
              arc: function () {},
              closePath: function () {},
              fill: function () {},
              getImageData: function () {
                return { data: new Array(300 * 150 * 4).fill(0) };
              },
            };
          },
          toDataURL: function () {
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";
          },
          width: 300,
          height: 150,
        };
      }
      return {};
    },
    documentElement: {
      clientWidth: 1920,
      clientHeight: 1080,
      scrollLeft: 0,
      scrollTop: 0,
    },
    body: {
      scrollLeft: 0,
      scrollTop: 0,
      clientWidth: 1920,
      clientHeight: 1080,
      addBehavior: function () {},
    },
    getElementsByTagName: function () {
      return [];
    },
    getElementById: function () {
      return null;
    },
    getElementsByClassName: function () {
      return [];
    },
    querySelector: function () {
      return null;
    },
    querySelectorAll: function () {
      return [];
    },
  };

  window.navigator = {
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    platform: "Win32",
    language: "zh-CN",
    languages: ["zh-CN", "zh", "en"],
    cookieEnabled: true,
    doNotTrack: null,
    hardwareConcurrency: 8,
    maxTouchPoints: 0,
    plugins: [],
    appVersion: "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  };

  window.screen = {
    width: 1920,
    height: 1080,
    availWidth: 1920,
    availHeight: 1040,
    colorDepth: 24,
    pixelDepth: 24,
  };

  window.location = {
    hostname: "www.ximalaya.com",
    protocol: "https:",
    href: "https://www.ximalaya.com/",
  };

  window.localStorage = {
    getItem: function () {},
    setItem: function () {},
  };

  window.addEventListener = function () {};
}

// ==================== 核心功能 ====================

/**
 * WFP 生成器类
 */
class XimalayaWFPGenerator {
  constructor() {
    this.isInitialized = false;
    this.atsSystem = null;
    this.loadCoreCode();
  }

  /**
   * 加载核心混淆代码
   * 注意：必须先加载 dws.js (包含 a0_0x1957)，再加载 ats.js
   */
  loadCoreCode() {
    try {
      const fs = require("fs");
      const path = require("path");
      const dir = __dirname;

      console.log("正在加载核心代码...");

      // 1. 先加载 dws.js (包含字符串解码函数 a0_0x1957)
      const dwsPath = path.join(dir, "dws.js");
      if (fs.existsSync(dwsPath)) {
        const dwsCode = fs.readFileSync(dwsPath, "utf8");
        eval(dwsCode);
        console.log("✓ dws.js 加载成功");
      } else {
        throw new Error("dws.js 文件不存在");
      }

      // 2. 再加载 ats.js (依赖 a0_0x1957)
      const hxPath = path.join(dir, "ats.js");
      if (fs.existsSync(hxPath)) {
        const hxCode = fs.readFileSync(hxPath, "utf8");
        eval(hxCode);
        console.log("✓ ats.js 加载成功");
      } else {
        throw new Error("ats.js 文件不存在");
      }

      this.isInitialized = true;
      console.log("✓ 核心代码初始化完成");
    } catch (error) {
      console.error("✗ 核心代码加载失败:", error.message);
      this.isInitialized = false;
    }
  }

  /**
   * 生成 WFP
   * @returns {string} wfp 值
   */
  generate() {
    if (!this.isInitialized) {
      throw new Error("WFP 生成器未初始化");
    }

    try {
      // 检查 $ats 对象是否存在
      // 注意：$ats 可能在全局作用域或 window.$ats 中
      let $ats =
        typeof window.$ats !== "undefined"
          ? window.$ats
          : typeof global.$ats !== "undefined"
            ? global.$ats
            : null;

      if (!$ats) {
        throw new Error(
          "$ats 对象未找到，请确保 ats.js 和 dws.js 都已正确加载",
        );
      }

      // 初始化 ATS
      if (typeof $ats.init === "function") {
        $ats.init({
          channelId: "web",
          logUrl: "test",
        });
      }

      // 获取 OpenID (即 wfp)
      if (typeof $ats.getOpenId === "function") {
        const wfp = $ats.getOpenId();
        return wfp;
      } else {
        throw new Error("getOpenId 方法不存在");
      }
    } catch (error) {
      console.error("WFP 生成失败:", error.message);
      throw error;
    }
  }

  /**
   * 批量生成 WFP
   * @param {number} count 生成数量
   * @returns {Array<string>} wfp 数组
   */
  generateMultiple(count = 1) {
    const results = [];
    for (let i = 0; i < count; i++) {
      results.push(this.generate());
    }
    return results;
  }

  /**
   * 检查 WFP 生成器状态
   * @returns {boolean} 是否可用
   */
  isAvailable() {
    if (!this.isInitialized) return false;

    let $ats =
      typeof window.$ats !== "undefined"
        ? window.$ats
        : typeof global.$ats !== "undefined"
          ? global.$ats
          : null;
    return $ats && typeof $ats.getOpenId === "function";
  }
}

// ==================== 导出接口 ====================

// Node.js 模块导出
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    XimalayaWFPGenerator,
    createGenerator: function () {
      return new XimalayaWFPGenerator();
    },
    generateWFP: function () {
      const generator = new XimalayaWFPGenerator();
      return generator.generate();
    },
  };
}

// ==================== 命令行测试 ====================

if (require.main === module) {
  console.log("╔════════════════════════════════════════╗");
  console.log("║     喜马拉雅 WFP 生成器 v1.0            ║");
  console.log("╚════════════════════════════════════════╝");
  console.log("");

  try {
    const generator = new XimalayaWFPGenerator();

    // 检查初始化状态
    if (!generator.isAvailable()) {
      console.error("✗ WFP 生成器初始化失败");
      console.error(" 请确保以下文件存在并可访问:");
      console.error("  - dws.js (包含混淆字符串数组)");
      console.error("  - ats.js (包含主逻辑)");
      process.exit(1);
    }

    console.log("✓ WFP 生成器初始化成功");
    console.log("");

    // 生成单个 WFP
    console.log("1. 生成单个 WFP:");
    const startTime = Date.now();
    const wfp = generator.generate();
    const endTime = Date.now();
    console.log(`  ✓ WFP: ${wfp}`);
    console.log(`  ✓ 长度: ${wfp ? wfp.length : 0}`);
    console.log(`  ✓ 耗时: ${endTime - startTime}ms`);
    console.log("");

    // 批量生成测试
    console.log("2. 批量生成测试 (5个):");
    const wfpList = generator.generateMultiple(5);
    wfpList.forEach((wfp, index) => {
      const isUnique = wfpList.indexOf(wfp) === index;
      console.log(
        `  [${index + 1}] ${wfp.substring(0, 32)}... ${isUnique ? "✓" : "✗ (重复)"}`,
      );
    });
    console.log("");

    // 唯一性检查
    const uniqueSet = new Set(wfpList);
    console.log(`3. 唯一性检查:`);
    console.log(`  总数: ${wfpList.length}`);
    console.log(`  唯一: ${uniqueSet.size}`);
    console.log(
      `  重复率: ${(((wfpList.length - uniqueSet.size) / wfpList.length) * 100).toFixed(2)}%`,
    );
    console.log("");

    if (uniqueSet.size === wfpList.length) {
      console.log("✓ 所有 WFP 都是唯一的！");
    } else {
      console.log("⚠ 存在重复的 WFP");
    }
  } catch (error) {
    console.error("");
    console.error("✗ 执行失败:", error.message);
    console.error("");
    console.error("故障排查:");
    console.error("  1. 确保 dws.js 文件存在于当前目录");
    console.error("  2. 确保 ats.js 文件存在于当前目录");
    console.error("  3. 确保 Node.js 版本 >= 12.x");
    console.error("  4. 检查文件权限是否正确");
    console.error("");
    console.error("详细错误信息:");
    console.error(error.stack);
    process.exit(1);
  }
}

// ==================== 浏览器环境支持 ====================

if (typeof window !== "undefined" && typeof window.$ats !== "undefined") {
  // 浏览器环境直接暴露到全局
  window.XimalayaWFPGenerator = XimalayaWFPGenerator;
}
