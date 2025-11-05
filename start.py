#!/usr/bin/env python
"""
协议核心管理系统 - 一键启动脚本
包含环境检查、依赖安装、数据库初始化、服务启动等功能
支持原版和 Nuitka 加密版本
"""
import os
import sys
import subprocess
import platform
import importlib.util
import signal
import time
from pathlib import Path

# psutil作为可选依赖
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

# 全局标志，防止重复执行
_SCRIPT_EXECUTED = False

# 尝试导入配置，如果失败则使用默认配置
try:
    from config import SERVER_CONFIG, validate_config
except ImportError:
    # 加密版本中 config.py 可能被编译为 .so 文件
    try:
        import config
        SERVER_CONFIG = config.SERVER_CONFIG
        validate_config = config.validate_config
    except ImportError:
        # 使用默认配置
        SERVER_CONFIG = {
            'HOST': '0.0.0.0',
            'PORT': 8000,
            'SERVER_NAME': '协议核心管理系统',
            'VERSION': '1.0.0'
        }
        def validate_config():
            return []

def install_package(package_name, import_name=None):
    """自动安装Python包"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        print(f"⚠️ 缺少依赖包: {package_name}")
        print(f"📦 正在自动安装 {package_name}...")
        
        try:
            # 尝试使用pip安装
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
            print(f"✅ {package_name} 安装成功")
            
            # 重新尝试导入
            __import__(import_name)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {package_name} 安装失败: {e}")
            return False
        except ImportError:
            print(f"❌ {package_name} 安装后仍无法导入")
            return False
        except Exception as e:
            print(f"❌ 安装 {package_name} 时发生错误: {e}")
            return False

def check_and_install_dependencies():
    """检查并安装依赖"""
    print("🔍 检查系统依赖...")
    
    # 必需依赖列表
    required_packages = [
        ('django', 'django'),
        ('requests', 'requests'),
    ]
    
    # 可选依赖列表（用于增强功能）
    optional_packages = [
        ('psutil', 'psutil'),  # 用于进程管理
        ('pillow', 'PIL'),     # 用于图像处理
    ]
    
    # 检查必需依赖
    missing_required = []
    for package_name, import_name in required_packages:
        if not install_package(package_name, import_name):
            missing_required.append(package_name)
    
    if missing_required:
        print(f"❌ 缺少必需依赖: {', '.join(missing_required)}")
        print("请手动安装缺少的依赖包")
        return False
    
    # 检查可选依赖
    print("🔍 检查可选依赖...")
    global PSUTIL_AVAILABLE, psutil
    
    for package_name, import_name in optional_packages:
        if install_package(package_name, import_name):
            print(f"✅ {package_name} 可用")
            # 特殊处理psutil的重新导入
            if package_name == 'psutil':
                try:
                    import psutil
                    PSUTIL_AVAILABLE = True
                except ImportError:
                    PSUTIL_AVAILABLE = False
        else:
            print(f"⚠️ {package_name} 不可用，部分功能可能受限")
    
    print("✅ 依赖检查完成")
    return True

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        print(f"当前版本：{sys.version}")
        return False
    print(f"✅ Python版本检查通过：{sys.version}")
    return True

def check_django_version():
    """检查Django版本"""
    try:
        import django
        django_version = django.get_version()
        major, minor = map(int, django_version.split('.')[:2])
        
        if major < 4 or (major == 4 and minor < 2):
            print(f"❌ Django版本过低：{django_version}")
            print("需要Django 4.2+，正在尝试升级...")
            return install_requirements()
        else:
            print(f"✅ Django版本检查通过：{django_version}")
            return True
    except ImportError:
        print("❌ Django未安装，正在尝试安装...")
        return install_requirements()

def check_api_dependencies():
    """检查API相关依赖"""
    print("🔍 检查API相关依赖...")
    
    required_modules = {
        'rest_framework': 'djangorestframework',
        'drf_yasg': 'drf-yasg', 
        'django_filters': 'django-filter',
        'decouple': 'python-decouple',
        'jazzmin': 'django-jazzmin',
        'channels': 'channels',
        'daphne': 'daphne'
    }
    
    missing_modules = []
    
    for module_name, package_name in required_modules.items():
        try:
            __import__(module_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} 未安装")
            missing_modules.append(package_name)
    
    if missing_modules:
        print(f"🔧 发现 {len(missing_modules)} 个缺失的依赖包，正在安装...")
        return install_requirements()
    else:
        print("✅ 所有API依赖检查通过")
        return True

def check_websocket_support():
    """检查WebSocket支持"""
    try:
        import channels
        import daphne
        print("✅ WebSocket支持已启用")
        return True
    except ImportError:
        print("⚠️  WebSocket支持未安装")
        return False

def fix_dependency_conflicts():
    """修复依赖冲突"""
    print("🔧 检查并修复依赖冲突...")
    
    # 使用清华镜像源
    mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    try:
        # 先升级pip
        print("   升级pip...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip",
            "-i", mirror, "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 修复已知的依赖冲突
        conflict_fixes = [
            "async-timeout>=4.0.0,<5.0",  # 修复aiohttp兼容性
            "attrs>=22.1.0",  # 修复twisted依赖
            "setuptools>=65.0.0",  # 确保setuptools版本
        ]
        
        for fix in conflict_fixes:
            print(f"   修复: {fix}")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", fix,
                "-i", mirror, "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ 依赖冲突修复完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  依赖冲突修复失败: {e}")
        return False

def install_requirements():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    
    # 先修复依赖冲突
    fix_dependency_conflicts()
    
    # 使用清华镜像源
    mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    # 必需的包列表 - 修复依赖冲突
    packages = [
        "Django>=4.2.0",
        "djangorestframework>=3.14.0",
        "django-cors-headers>=4.0.0", 
        "Pillow>=10.0.0",
        "requests>=2.31.0",
        "qrcode>=7.4.0",
        "python-decouple>=3.8",
        "drf-yasg>=1.21.7",
        "django-filter>=23.2",
        "django-jazzmin>=2.6.0",
        # WebSocket相关依赖 - 修复版本兼容性
        "attrs>=22.1.0",  # 修复twisted依赖
        "async-timeout>=4.0.0,<5.0",  # 修复aiohttp兼容性
        "channels>=4.0.0",
        "channels-redis>=4.1.0",
        "daphne>=4.0.0",
        "twisted>=22.10.0"  # 确保twisted版本兼容
    ]
    

    try:
        print(f"🌐 使用镜像源: {mirror}")
        for package in packages:
            print(f"   安装 {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package, "-i", mirror, 
                "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
            ])
        
        print("✅ 依赖包安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败：{e}")
        print("💡 请手动执行:")
        print("   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Django djangorestframework")
        print("   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple channels daphne")
        return False

def install_websocket_only():
    """仅安装WebSocket相关依赖"""
    print("📡 正在安装WebSocket依赖...")
    
    # 使用清华镜像源
    mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
    
    # WebSocket相关包
    websocket_packages = [
        "attrs>=22.1.0",
        "async-timeout>=4.0.0,<5.0",
        "channels>=4.0.0",
        "daphne>=4.0.0",
        "twisted>=22.10.0"
    ]
    
    try:
        # 先修复依赖冲突
        fix_dependency_conflicts()
        
        print(f"🌐 使用镜像源: {mirror}")
        for package in websocket_packages:
            print(f"   安装 {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package, "-i", mirror, 
                "--trusted-host", "pypi.tuna.tsinghua.edu.cn",
                "--force-reinstall"  # 强制重新安装以解决冲突
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ WebSocket依赖安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ WebSocket依赖安装失败：{e}")
        print("💡 请手动执行:")
        print("   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple attrs async-timeout channels daphne")
        return False

def setup_database():
    """设置数据库"""
    print("🗄️ 正在设置数据库...")
    try:
        # 清理现有数据库
        if Path("protocol_core.db").exists():
            Path("protocol_core.db").unlink()
            print("   清理现有数据库")
        
        # 生成迁移文件（包含所有应用）
        apps = ["accounts", "connections", "wechat_login", "protocol_api", "read_check", "protocol_config", "updater", "auth_system", "auth_codes"]
        for app in apps:
            try:
                subprocess.check_call([sys.executable, "manage.py", "makemigrations", app], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
        
        # 执行迁移（确保所有应用的迁移都被执行）
        subprocess.check_call([sys.executable, "manage.py", "migrate", "--noinput"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ 数据库设置完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库设置失败：{e}")
        return False

def create_superuser():
    """创建默认管理员账户"""
    print("👤 创建默认管理员账户...")
    try:
        # 创建默认管理员
        create_admin_script = '''
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "protocol_core.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username="admin").exists():
    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin",
        user_type="admin"
    )
    print("✅ 默认管理员创建成功")
    print("   用户名: admin")
    print("   密码: admin")
else:
    print("ℹ️ 管理员账户已存在")
'''
        
        with open("temp_admin.py", "w", encoding="utf-8") as f:
            f.write(create_admin_script)
        
        subprocess.check_call([sys.executable, "temp_admin.py"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        Path("temp_admin.py").unlink()
        return True
        
    except Exception as e:
        print(f"❌ 管理员账户创建失败：{e}")
        if Path("temp_admin.py").exists():
            Path("temp_admin.py").unlink()
        return False

def collect_static():
    """收集静态文件"""
    print("📁 正在收集静态文件...")
    try:
        subprocess.check_call([sys.executable, "manage.py", "collectstatic", "--noinput"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ 静态文件收集完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 静态文件收集失败：{e}")
        return False

def start_asgi_server():
    """启动ASGI服务器（支持WebSocket）"""
    host = SERVER_CONFIG['HOST']
    port = SERVER_CONFIG['PORT']
    server_name = SERVER_CONFIG['SERVER_NAME']
    
    print("🚀 正在启动ASGI服务器（支持WebSocket）...")
    print("=" * 60)
    print(f"📡 {server_name} - WebSocket版本")
    print("=" * 60)
    print(f"🌐 访问地址：http://{host}:{port}")
    print(f"🔧 管理后台：http://{host}:{port}/admin")
    print(f"📡 WebSocket：ws://{host}:{port}/ws/chat/")
    print(f"🔥 RESTful API文档：http://{host}:{port}/api/swagger/")
    print(f"📚 ReDoc文档：http://{host}:{port}/api/redoc/")
    print(f"⚙️ 协议配置：http://{host}:{port}/dashboard/protocol-config/")
    print(f"👁️ 阅读过检：http://{host}:{port}/dashboard/read-check/")
    print("=" * 60)
    print("💡 提示：WebSocket实时通信已启用")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "-m", "daphne", "-p", str(port), "-b", host, "asgi:application"])
    except KeyboardInterrupt:
        print("\n👋 ASGI服务器已停止")
    except FileNotFoundError:
        print("❌ daphne未安装，请先安装: pip install daphne")
        return False
    return True

def is_encrypted_version():
    """检测是否为加密版本"""
    # 检查是否存在 .so 文件（Nuitka 编译后的文件）
    current_dir = Path('.')
    so_files = list(current_dir.glob('**/*.so'))
    
    # 检查是否有编译后的 Python 模块
    has_compiled_modules = len(so_files) > 0
    
    # 检查 manage.py 是否存在（原版会有，加密版可能没有或被编译）
    has_manage_py = Path('manage.py').exists()
    
    return has_compiled_modules and not has_manage_py

def start_encrypted_django_server():
    """启动加密版本的Django服务器"""
    host = SERVER_CONFIG['HOST']
    port = SERVER_CONFIG['PORT']
    server_name = SERVER_CONFIG['SERVER_NAME']
    
    print("🚀 启动协议核心管理系统...")
    print("=" * 50)
    print(f"{server_name}")
    print("=" * 50)
    print(f"🌐 访问地址：http://{host}:{port}")
    print(f"🔧 管理后台：http://{host}:{port}/admin")
    print(f"🔥 RESTful API文档：http://{host}:{port}/api/swagger/")
    print(f"📚 ReDoc文档：http://{host}:{port}/api/redoc/")
    print(f"⚙️ 协议配置：http://{host}:{port}/dashboard/protocol-config/")
    print(f"👁️ 阅读过检：http://{host}:{port}/dashboard/read-check/")
    print("=" * 50)
    print("🔒 源代码已加密保护")
    print("⚠️  WebSocket功能不可用")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        # 添加当前目录到 Python 路径
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # 设置环境变量
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'protocol_core.settings')
        
        # 导入 Django 并启动
        import django
        django.setup()
        
        # 直接使用 Django 的 runserver 命令，避免重复执行
        from django.core.management.commands.runserver import Command as RunServerCommand
        
        # 创建 runserver 命令实例
        command = RunServerCommand()
        
        # 执行 runserver 命令，使用正确的参数
        server_address = f"{host}:{port}"
        command.handle(
            addrport=server_address,
            verbosity=1,
            settings=None,
            pythonpath=None,
            traceback=False,
            no_color=False,
            force_color=False,
            skip_checks=False,
            use_ipv6=False,  # 添加缺失的参数
            use_threading=True,
            use_reloader=False,  # 禁用 reloader 防止重复执行
            use_static_handler=True,
            insecure_serving=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except ImportError as exc:
        print(f"❌ 导入错误: {exc}")
        print("💡 请确保已安装 Django 并且环境配置正确")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def start_django_server():
    """启动标准Django服务器"""
    host = SERVER_CONFIG['HOST']
    port = SERVER_CONFIG['PORT']
    server_name = SERVER_CONFIG['SERVER_NAME']
    
    print("🚀 正在启动标准HTTP服务器...")
    print("=" * 50)
    print(server_name)
    print("=" * 50)
    print(f"🌐 访问地址：http://{host}:{port}")
    print(f"🔧 管理后台：http://{host}:{port}/admin")
    print(f"🔥 RESTful API文档：http://{host}:{port}/api/swagger/")
    print(f"📚 ReDoc文档：http://{host}:{port}/api/redoc/")
    print(f"⚙️ 协议配置：http://{host}:{port}/dashboard/protocol-config/")
    print(f"👁️ 阅读过检：http://{host}:{port}/dashboard/read-check/")
    print("=" * 50)
    print("⚠️  WebSocket功能不可用")
    print("💡 提示：使用 'python manage.py generate_api_token username' 生成API Token")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        server_address = f"{host}:{port}"
        subprocess.check_call([sys.executable, "manage.py", "runserver", server_address])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")

def is_docker_environment():
    """检查是否在Docker容器中运行"""
    return os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER') == 'true'

def docker_main():
    """Docker容器中的主函数"""
    print("=" * 60)
    print("🐳 协议核心管理系统 - Docker容器版")
    print("=" * 60)
    print(f"📡 支持实时WebSocket通信")
    print(f"🌐 现代化Web管理界面")
    print(f"⚡ 高性能异步处理")
    print(f"🔐 集成API认证系统")
    print(f"🎯 版本: {SERVER_CONFIG['VERSION']}")
    print(f"🌐 启动端口: {SERVER_CONFIG['PORT']}")
    print("=" * 60)
    
    # 验证配置
    config_errors = validate_config()
    if config_errors:
        print("❌ 配置验证失败:")
        for error in config_errors:
            print(f"   - {error}")
        sys.exit(1)
    print("✅ 配置验证通过")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查是否在项目目录（加密版本可能没有 manage.py）
    if not is_encrypted_version() and not Path("manage.py").exists():
        print("❌ 错误：请在项目根目录运行此脚本")
        sys.exit(1)
    
    # Docker环境中总是执行初始化
    print("\n🔧 Docker环境初始化...")
    
    # 设置数据库
    if not setup_database():
        sys.exit(1)
    
    # 收集静态文件
    if not collect_static():
        sys.exit(1)
    
    # 创建默认管理员
    create_superuser()
    
    # 检查WebSocket支持
    websocket_support = check_websocket_support()
    
    print("\n🚀 启动服务器...")
    
    # Docker环境中优先使用ASGI服务器
    if websocket_support:
        print("📡 使用ASGI服务器（支持WebSocket）")
        start_asgi_server()
    else:
        print("🌐 使用标准HTTP服务器")
        start_django_server()

def handle_restart():
    """处理系统重启"""
    print("🔄 正在重启系统...")
    
    # 获取当前进程的PID
    current_pid = os.getpid()
    print(f"🔍 当前PID: {current_pid}")
    
    # 查找占用端口的进程
    port = SERVER_CONFIG.get('PORT', 8000)
    print(f"🔍 查找占用端口 {port} 的进程...")
    
    if PSUTIL_AVAILABLE:
        # 使用psutil查找占用端口的进程
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.laddr.port == port:
                            print(f"🔍 找到占用端口的进程: PID {proc.pid}")
                            if proc.pid != current_pid:
                                print(f"💪 终止进程 {proc.pid}")
                                proc.terminate()
                                # 等待进程终止
                                try:
                                    proc.wait(timeout=5)
                                except psutil.TimeoutExpired:
                                    print(f"⚠️ 强制终止进程 {proc.pid}")
                                    proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"⚠️ psutil查找进程失败: {e}")
    else:
        # 如果没有psutil，使用系统命令
        print("⚠️ psutil不可用，使用系统命令查找进程")
        try:
            if platform.system() == "Linux":
                # 使用lsof查找占用端口的进程
                result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip() and pid != str(current_pid):
                            print(f"💪 终止进程 {pid}")
                            try:
                                subprocess.run(['kill', pid.strip()], check=True)
                            except subprocess.CalledProcessError:
                                # 如果kill失败，尝试强制终止
                                subprocess.run(['kill', '-9', pid.strip()], check=False)
            elif platform.system() == "Windows":
                # Windows系统使用netstat和taskkill
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            if pid != str(current_pid):
                                print(f"💪 终止进程 {pid}")
                                subprocess.run(['taskkill', '/F', '/PID', pid], check=False)
        except Exception as e:
            print(f"⚠️ 使用系统命令终止进程失败: {e}")
    
    # 等待端口释放
    print("⏳ 等待端口释放...")
    time.sleep(3)
    
    # 重新启动
    print("🚀 重新启动系统...")
    python_executable = sys.executable
    script_path = os.path.abspath(__file__)
    
    # 使用新进程启动（不传递--restart参数避免递归）
    subprocess.Popen([python_executable, script_path], 
                    cwd=os.path.dirname(script_path),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL)
    
    print("✅ 重启命令已发送，当前进程即将退出")
    time.sleep(1)
    
    # 退出当前进程
    os._exit(0)

def main():
    """主函数"""
    global _SCRIPT_EXECUTED
    
    # 检查是否是重启模式
    if len(sys.argv) > 1 and sys.argv[1] == '--restart':
        handle_restart()
        return
    
    if _SCRIPT_EXECUTED:
        return
    _SCRIPT_EXECUTED = True
    
    # 检查并安装依赖
    if not check_and_install_dependencies():
        print("❌ 依赖检查失败，无法启动系统")
        return
    
    # 检查是否在Docker环境中
    #if is_docker_environment():
     #   docker_main()
    #    return
    
    print("=" * 60)
    # print("🚀 协议核心管理系统 - WebSocket增强版")
    print("=" * 60)
    # print(f"📡 支持实时WebSocket通信")
    # print(f"🌐 现代化Web管理界面")
    # print(f"⚡ 高性能异步处理")
    # print(f"🎯 版本: {SERVER_CONFIG['VERSION']}")
    print(f"🌐 启动端口: {SERVER_CONFIG['PORT']}")
    print("=" * 60)
    
    # 验证配置
    config_errors = validate_config()
    if config_errors:
        print("❌ 配置验证失败:")
        for error in config_errors:
            print(f"   - {error}")
        return
    print("✅ 配置验证通过")
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查Django版本
    if not check_django_version():
        return
    
    # 检查API相关依赖
    if not check_api_dependencies():
        return
    
    # 检查是否在项目目录（加密版本可能没有 manage.py）
    encrypted_version = is_encrypted_version()
    if not encrypted_version and not Path("manage.py").exists():
        print("❌ 错误：请在项目根目录运行此脚本")
        return
    
    # 检查是否需要初始化
    if not Path("protocol_core.db").exists():
        print("\n🔧 检测到首次运行，正在初始化...")
        
        # 设置数据库
        if not setup_database():
            return
        
        # 收集静态文件
        if not collect_static():
            return
        
        # 创建默认管理员
        create_superuser()
    
    else:
        print("\n✅ 数据库已存在，跳过初始化")
    
    # 根据版本类型启动相应的服务器
    if encrypted_version:
        # print("🔒 检测到加密版本，使用加密启动模式")
        start_encrypted_django_server()
    else:
        print("📝 检测到原版，使用标准启动模式")
        start_django_server()

if __name__ == "__main__":
    main()
