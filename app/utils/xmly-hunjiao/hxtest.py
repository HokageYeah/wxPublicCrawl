import execjs
import requests
from http.cookies import SimpleCookie

class XimalayaWFP:
    def __init__(self):
        # 读取混淆的JS文件
        with open('hx.js', 'r', encoding='utf-8') as f:
            js_code = f.read()
        
        # 添加必要的浏览器环境模拟
        wrapper_code = """
        // 模拟浏览器环境
        var window = this;
        var document = {
            createElement: function(tag) {
                if (tag === 'canvas') {
                    return {
                        getContext: function() {
                            return {
                                fillText: function() {},
                                fillRect: function() {},
                                fillStyle: '',
                                textBaseline: '',
                                font: '',
                                globalCompositeOperation: '',
                                beginPath: function() {},
                                arc: function() {},
                                closePath: function() {},
                                fill: function() {},
                                getImageData: function() {
                                    return { data: [1,2,3,4] };
                                }
                            };
                        },
                        toDataURL: function() {
                            return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
                        },
                        width: 300,
                        height: 150
                    };
                }
                return {};
            },
            documentElement: {
                clientWidth: 1920,
                clientHeight: 1080,
                scrollLeft: 0,
                scrollTop: 0
            },
            body: {
                scrollLeft: 0,
                scrollTop: 0,
                clientWidth: 1920,
                clientHeight: 1080,
                addBehavior: function() {}
            },
            getElementsByTagName: function() { return []; },
            getElementById: function() { return null; },
            getElementsByClassName: function() { return []; },
            querySelector: function() { return null; },
            querySelectorAll: function() { return []; }
        };
        
        var navigator = {
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            platform: 'Win32',
            language: 'zh-CN',
            languages: ['zh-CN', 'zh', 'en'],
            cookieEnabled: true,
            doNotTrack: null,
            hardwareConcurrency: 8,
            maxTouchPoints: 0,
            plugins: [],
            appVersion: '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        };
        
        var screen = {
            width: 1920,
            height: 1080,
            availWidth: 1920,
            availHeight: 1040,
            colorDepth: 24,
            pixelDepth: 24
        };
        
        var location = {
            href: 'https://www.ximalaya.com/',
            hostname: 'www.ximalaya.com',
            protocol: 'https:'
        };
        
        """ + js_code + """
        
        // 导出获取WFP的函数
        function getWFP() {
            try {
                // 初始化ATS
                if (typeof $ats !== 'undefined' && $ats.init) {
                    $ats.init({
                        channelId: 'web',
                        logUrl: 'test'
                    });
                }
                
                // 获取OpenID
                if (typeof $ats !== 'undefined' && $ats.getOpenId) {
                    return $ats.getOpenId();
                }
                
                return null;
            } catch(e) {
                console.log('Error:', e);
                return null;
            }
        }
        """
        
        # 编译JS代码
        self.ctx = execjs.compile(wrapper_code)
    
    def get_wfp(self):
        """获取WFP参数"""
        try:
            result = self.ctx.call('getWFP')
            return result
        except Exception as e:
            print(f"执行JS错误: {e}")
            return None

# 使用示例
def login_ximalaya(username, password):
    # 1. 生成WFP
    wfp_generator = XimalayaWFP()
    wfp = wfp_generator.get_wfp()
    
    print(f"生成的WFP: {wfp}")
    
    # 2. 设置Cookie
    session = requests.Session()
    session.cookies.set('wfp', wfp, domain='.ximalaya.com')
    
    # 3. 执行登录请求
    login_url = "https://www.ximalaya.com/passport-api/user/login"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.ximalaya.com/'
    }
    
    data = {
        'username': username,
        'password': password,
        # 其他必要参数
    }
    
    response = session.post(login_url, headers=headers, json=data)
    return response.json()

# 测试
if __name__ == '__main__':
    wfp_gen = XimalayaWFP()
    wfp = wfp_gen.get_wfp()
    print(f"WFP值: {wfp}")