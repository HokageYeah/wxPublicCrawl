"""
测试打包后资源文件路径是否正确
用于诊断打包后提示词文件找不到的问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import os
from app.utils.src_path import get_resource_path


def test_resource_paths():
    """测试各种资源路径"""
    print("\n" + "="*70)
    print("🔍 资源路径诊断工具")
    print("="*70)
    
    # 检测运行模式
    # 不用 _MEIPASS 判断是否打包、onedir 模式可能没有 _MEIPASS、非 PyInstaller 理论上也可能存在
    # is_packaged = hasattr(sys, '_MEIPASS')
    is_packaged = getattr(sys, 'frozen', False)
    print(f"\n📦 运行模式: {'打包模式 (PyInstaller)' if is_packaged else '开发模式'}")
    
    if is_packaged:
        print(f"📂 临时资源目录: {sys._MEIPASS}")
    
    # 测试路径列表
    test_paths = [
        'app/ai/prompt',
        'app/ai/prompt/education_prompt.txt',
        'web/dist',
        '.env',
        '.env.desktop'
    ]
    
    print(f"\n{'='*70}")
    print("📋 资源路径检查:")
    print("="*70)
    
    results = []
    for relative_path in test_paths:
        print(f"\n🔍 检查: {relative_path}")
        print("-" * 70)
        
        try:
            full_path = get_resource_path(relative_path)
            exists = os.path.exists(full_path)
            
            result = {
                'relative': relative_path,
                'full': full_path,
                'exists': exists
            }
            
            if exists:
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    result['type'] = 'file'
                    result['size'] = size
                    print(f"   ✅ 文件存在")
                    print(f"   📏 大小: {size} 字节")
                elif os.path.isdir(full_path):
                    contents = os.listdir(full_path)
                    result['type'] = 'directory'
                    result['contents'] = contents
                    print(f"   ✅ 目录存在")
                    print(f"   📁 包含 {len(contents)} 个项目:")
                    for item in contents[:5]:  # 只显示前5个
                        print(f"      - {item}")
                    if len(contents) > 5:
                        print(f"      ... 还有 {len(contents) - 5} 个项目")
            else:
                result['type'] = 'not_found'
                print(f"   ❌ 不存在")
                
                # 检查父目录
                parent_dir = os.path.dirname(full_path)
                if os.path.exists(parent_dir):
                    print(f"   ℹ️  父目录存在: {parent_dir}")
                    try:
                        parent_contents = os.listdir(parent_dir)
                        print(f"   📁 父目录内容: {parent_contents[:5]}")
                    except:
                        pass
                else:
                    print(f"   ❌ 父目录也不存在: {parent_dir}")
            
            results.append(result)
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            results.append({
                'relative': relative_path,
                'error': str(e)
            })
    
    # 总结
    print(f"\n{'='*70}")
    print("📊 检查总结:")
    print("="*70)
    
    found = sum(1 for r in results if r.get('exists', False))
    total = len(results)
    
    print(f"\n找到资源: {found}/{total}")
    
    missing = [r['relative'] for r in results if not r.get('exists', False)]
    if missing:
        print(f"\n❌ 缺失的资源:")
        for path in missing:
            print(f"   - {path}")
    else:
        print(f"\n✅ 所有资源都存在！")
    
    return results


def test_prompt_manager():
    """测试提示词管理器"""
    print(f"\n{'='*70}")
    print("🧪 测试提示词管理器")
    print("="*70)
    
    try:
        from app.ai.utils.prompt_manager import PromptManager, get_prompt_manager
        
        print("\n1️⃣ 测试默认路径:")
        print("-" * 70)
        manager1 = PromptManager()
        print(f"   提示词目录: {manager1.prompt_dir}")
        print(f"   目录存在: {'✅ 是' if manager1.prompt_dir.exists() else '❌ 否'}")
        
        if manager1.prompt_dir.exists():
            files = list(manager1.prompt_dir.glob("*.txt"))
            print(f"   提示词文件数量: {len(files)}")
            for f in files:
                print(f"      - {f.name}")
        
        print("\n2️⃣ 测试加载education_prompt:")
        print("-" * 70)
        try:
            manager1.load_prompt("education_prompt", "education_prompt.txt")
            print("   ✅ 加载成功")
            
            # 尝试渲染
            test_data = '[{"id": "1", "title": "测试"}]'
            prompt = manager1.render_prompt("education_prompt", articles_json=test_data)
            print(f"   ✅ 渲染成功，长度: {len(prompt)} 字符")
            print(f"   预览: {prompt[:100]}...")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
        
        print("\n3️⃣ 测试单例模式:")
        print("-" * 70)
        manager2 = get_prompt_manager()
        print(f"   是否同一实例: {'✅ 是' if manager1 is not manager2 else '❌ 否'}")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "🚀 " * 20)
    print("打包后资源路径诊断")
    print("🚀 " * 20)
    
    # 测试1: 资源路径
    results = test_resource_paths()
    
    # 测试2: 提示词管理器
    test_prompt_manager()
    
    print("\n" + "="*70)
    print("✨ 诊断完成")
    print("="*70)
    
    # 给出建议
    prompt_exists = any(
        r.get('relative') == 'app/ai/prompt' and r.get('exists')
        for r in results
    )
    
    if not prompt_exists:
        print("\n⚠️  建议:")
        print("1. 确保 wx_crawler.spec 中包含:")
        print("   datas=[('app/ai/prompt', 'app/ai/prompt'), ...]")
        print("2. 重新打包: script/desktop/build_mac.sh")
        print("3. 检查打包后的目录结构")


if __name__ == "__main__":
    main()

