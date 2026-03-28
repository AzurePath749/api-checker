# -*- coding: utf-8 -*-
"""
代理节点检测工具
- 从订阅链接提取节点
- 测试每个节点是否能连通 Gemini API
- 生成测试报告
"""

import sys
import io

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import base64
import urllib.parse
import requests
import socket
import time
import json
import concurrent.futures
import threading
import subprocess
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ==================== 配置 ====================
GEMINI_TEST_URL = "https://generativelanguage.googleapis.com/v1/models"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TEST_TIMEOUT = 15  # 秒
MAX_WORKERS = 3    # 并发数 (降低以避免端口冲突)
LOCAL_PROXY_PORT_START = 10080  # 本地代理端口起始值

# ==================== 数据类 ====================
@dataclass
class ProxyNode:
    """代理节点"""
    name: str
    protocol: str      # ss, hysteria2, vmess, vless, trojan
    server: str
    port: int
    password: str
    method: str = ""   # SS加密方法
    sni: str = ""
    insecure: bool = False
    raw: str = ""      # 原始链接

@dataclass
class TestResult:
    """测试结果"""
    node: ProxyNode
    success: bool
    latency: float     # 毫秒
    error: str = ""
    status_code: int = 0
    response_preview: str = ""

# ==================== 节点解析 ====================
def fetch_subscription(url: str) -> str:
    """获取订阅内容"""
    print(f"📡 正在获取订阅内容...")
    if not url.startswith("https://"):
        raise Exception("仅允许 HTTPS 协议的订阅链接")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        # 尝试 base64 解码
        try:
            decoded = base64.b64decode(resp.text).decode('utf-8')
            return decoded
        except Exception:
            return resp.text
    except Exception as e:
        raise Exception(f"获取订阅失败: {e}")

def parse_ss_link(link: str) -> Optional[ProxyNode]:
    """解析 SS 链接
    格式1: ss://base64(method:password@server:port)#name
    格式2: ss://base64(method:password)@server:port#name
    """
    try:
        if not link.startswith("ss://"):
            return None

        # 分离名称
        name = ""
        if "#" in link:
            link_part, name_part = link.split("#", 1)
            name = urllib.parse.unquote(name_part)
        else:
            link_part = link

        # ss://后面的内容
        content = link_part[5:]  # 去掉 "ss://"

        # 添加 padding 如果需要
        def safe_b64decode(s):
            padding = 4 - len(s) % 4
            if padding != 4:
                s += '=' * padding
            return base64.b64decode(s).decode('utf-8')

        # 尝试整体 base64 解码 (格式1)
        try:
            decoded = safe_b64decode(content)
            # 格式: method:password@server:port
            if "@" in decoded:
                method_pass, server_port = decoded.rsplit("@", 1)
                method, password = method_pass.split(":", 1)
                server, port = server_port.rsplit(":", 1)
                port = int(port)

                return ProxyNode(
                    name=name or f"SS-{server}:{port}",
                    protocol="ss",
                    server=server,
                    port=port,
                    password=password,
                    method=method,
                    raw=link
                )
        except Exception:
            pass

        # 格式2: base64(method:password)@server:port
        if "@" in content:
            encoded_part, server_part = content.rsplit("@", 1)
            try:
                decoded = safe_b64decode(encoded_part)
                if ":" in decoded:
                    method, password = decoded.split(":", 1)
                else:
                    method = "chacha20-ietf-poly1305"
                    password = decoded

                # 解析 server:port
                if ":" in server_part:
                    server, port = server_part.rsplit(":", 1)
                    port = int(port)
                else:
                    return None

                return ProxyNode(
                    name=name or f"SS-{server}:{port}",
                    protocol="ss",
                    server=server,
                    port=port,
                    password=password,
                    method=method,
                    raw=link
                )
            except Exception as e:
                pass

        return None
    except Exception as e:
        print(f"  ⚠️ 解析SS节点失败: {e}")
        return None

def parse_hysteria2_link(link: str) -> Optional[ProxyNode]:
    """解析 Hysteria2 链接
    格式: hysteria2://password@server:port?sni=xxx&insecure=1#name
    """
    try:
        if not link.startswith("hysteria2://") and not link.startswith("hy2://"):
            return None

        # 分离名称
        name = ""
        if "#" in link:
            link_part, name_part = link.split("#", 1)
            name = urllib.parse.unquote(name_part)
        else:
            link_part = link

        # hysteria2://password@server:port?params
        if link_part.startswith("hysteria2://"):
            content = link_part[13:]
        else:
            content = link_part[6:]

        # 解析参数
        params = {}
        if "?" in content:
            main_part, query = content.split("?", 1)
            for param in query.split("&"):
                if "=" in param:
                    k, v = param.split("=", 1)
                    params[k] = v
        else:
            main_part = content

        # 解析 password@server:port
        if "@" not in main_part:
            return None

        password, server_part = main_part.split("@", 1)

        if ":" in server_part:
            server, port = server_part.rsplit(":", 1)
            port = int(port)
        else:
            return None

        return ProxyNode(
            name=name or f"HY2-{server}:{port}",
            protocol="hysteria2",
            server=server,
            port=port,
            password=password,
            sni=params.get("sni", server),
            insecure=params.get("insecure", "0") == "1",
            raw=link
        )
    except Exception as e:
        print(f"  ⚠️ 解析Hysteria2节点失败: {e}")
        return None

def parse_vmess_link(link: str) -> Optional[ProxyNode]:
    """解析 VMess 链接"""
    try:
        if not link.startswith("vmess://"):
            return None

        content = link[8:]  # 去掉 "vmess://"
        decoded = base64.b64decode(content).decode('utf-8')
        config = json.loads(decoded)

        return ProxyNode(
            name=config.get("ps", "VMess"),
            protocol="vmess",
            server=config.get("add", ""),
            port=int(config.get("port", 443)),
            password=config.get("id", ""),
            method=config.get("scy", "auto"),
            sni=config.get("sni", config.get("host", "")),
            raw=link
        )
    except Exception:
        return None

def parse_vless_link(link: str) -> Optional[ProxyNode]:
    """解析 VLESS 链接
    格式: vless://uuid@server:port?encryption=none&security=tls&sni=xxx&type=tcp#name
    """
    try:
        if not link.startswith("vless://"):
            return None

        content = link[8:]

        name = ""
        if "#" in content:
            link_part, name_part = content.split("#", 1)
            name = urllib.parse.unquote(name_part)
        else:
            link_part = content

        params = {}
        if "?" in link_part:
            main_part, query = link_part.split("?", 1)
            for param in query.split("&"):
                if "=" in param:
                    k, v = param.split("=", 1)
                    params[k] = urllib.parse.unquote(v)
        else:
            main_part = link_part

        if "@" not in main_part:
            return None

        password, server_part = main_part.split("@", 1)

        if ":" in server_part:
            server, port = server_part.rsplit(":", 1)
            port = int(port)
        else:
            return None

        return ProxyNode(
            name=name or f"VLESS-{server}:{port}",
            protocol="vless",
            server=server,
            port=port,
            password=password,
            sni=params.get("sni", params.get("peer", server)),
            insecure=params.get("allowInsecure", "0") == "1",
            raw=link
        )
    except Exception:
        return None

def parse_trojan_link(link: str) -> Optional[ProxyNode]:
    """解析 Trojan 链接"""
    try:
        if not link.startswith("trojan://"):
            return None

        # trojan://password@server:port?sni=xxx#name
        content = link[9:]

        name = ""
        if "#" in content:
            link_part, name_part = content.split("#", 1)
            name = urllib.parse.unquote(name_part)
        else:
            link_part = content

        params = {}
        if "?" in link_part:
            main_part, query = link_part.split("?", 1)
            for param in query.split("&"):
                if "=" in param:
                    k, v = param.split("=", 1)
                    params[k] = v
        else:
            main_part = link_part

        password, server_part = main_part.split("@", 1)
        server, port = server_part.rsplit(":", 1)
        port = int(port)

        return ProxyNode(
            name=name or f"Trojan-{server}:{port}",
            protocol="trojan",
            server=server,
            port=port,
            password=password,
            sni=params.get("sni", server),
            raw=link
        )
    except Exception:
        return None

def parse_nodes(content: str) -> List[ProxyNode]:
    """解析所有节点"""
    nodes = []
    lines = content.strip().split("\n")

    print(f"📋 正在解析节点...")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        node = None
        if line.startswith("ss://"):
            node = parse_ss_link(line)
        elif line.startswith("hysteria2://") or line.startswith("hy2://"):
            node = parse_hysteria2_link(line)
        elif line.startswith("vmess://"):
            node = parse_vmess_link(line)
        elif line.startswith("vless://"):
            node = parse_vless_link(line)
        elif line.startswith("trojan://"):
            node = parse_trojan_link(line)

        if node:
            nodes.append(node)

    return nodes

# ==================== 连通性测试 ====================
def test_tcp_connection(node: ProxyNode) -> Tuple[bool, float, str]:
    """测试 TCP 连通性"""
    start = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TEST_TIMEOUT)
            sock.connect((node.server, node.port))
            latency = (time.time() - start) * 1000
            return True, latency, ""
    except socket.timeout:
        return False, 0, "连接超时"
    except ConnectionRefusedError:
        return False, 0, "连接被拒绝"
    except Exception as e:
        return False, 0, str(e)

def get_local_port() -> int:
    """获取本地代理端口（由系统分配）"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', 0))
        return sock.getsockname()[1]

def test_ss_proxy_gemini(node: ProxyNode, local_port: int) -> Tuple[bool, str, str]:
    """通过 SS 代理测试 Gemini API

    使用 pproxy 启动本地代理，然后测试 Gemini API

    返回: (成功, 延迟, 消息)
    - 成功=True: 代理可用，能连接到 Gemini
    - 成功=False: 代理不可用或被封锁
    """
    try:
        # 构建 SS 代理 URL
        # 格式: ss://method:password@server:port
        ss_url = f"ss://{node.method}:{node.password}@{node.server}:{node.port}"

        # 启动 pproxy
        cmd = [
            sys.executable, "-m", "pproxy",
            "-l", f"http://:{local_port}",
            "-r", ss_url
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        for _ in range(10):
            if proc.poll() is not None:
                return False, "", "pproxy 启动失败"
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as check_sock:
                    check_sock.settimeout(0.2)
                    check_sock.connect(('127.0.0.1', local_port))
                break
            except (ConnectionRefusedError, socket.timeout, OSError):
                time.sleep(0.2)

        try:
            # 通过代理测试 Gemini API
            proxies = {
                "http": f"http://127.0.0.1:{local_port}",
                "https": f"http://127.0.0.1:{local_port}"
            }

            # 构建 URL（如果有 API Key）
            test_url = GEMINI_TEST_URL
            headers = {}
            if GEMINI_API_KEY:
                headers["x-goog-api-key"] = GEMINI_API_KEY

            start = time.time()
            resp = requests.get(
                test_url,
                headers=headers,
                proxies=proxies,
                timeout=TEST_TIMEOUT
            )
            latency = (time.time() - start) * 1000

            if resp.status_code == 200:
                return True, f"{latency:.0f}ms", "Gemini API 连接成功"
            elif resp.status_code == 403:
                # 403 表示代理可用，但 API 需要认证
                # 这意味着代理工作正常！
                return True, f"{latency:.0f}ms", "代理可用 (Gemini 需 API Key)"
            else:
                return False, "", f"Gemini 返回 {resp.status_code}"
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()

    except requests.exceptions.ProxyError as e:
        return False, "", f"代理错误: {str(e)[:50]}"
    except requests.exceptions.ConnectTimeout:
        return False, "", "连接超时"
    except Exception as e:
        return False, "", str(e)[:50]

def test_node(node: ProxyNode, test_gemini: bool = True) -> TestResult:
    """测试单个节点

    Args:
        node: 代理节点
        test_gemini: 是否测试 Gemini API (需要 pproxy)
    """
    # 首先测试 TCP 连通性
    tcp_ok, tcp_latency, tcp_error = test_tcp_connection(node)

    if not tcp_ok:
        return TestResult(
            node=node,
            success=False,
            latency=0,
            error=f"端口不可达: {tcp_error}"
        )

    # 如果是 SS 节点且启用 Gemini 测试
    if test_gemini and node.protocol == "ss":
        local_port = get_local_port()
        gemini_ok, gemini_latency, gemini_msg = test_ss_proxy_gemini(node, local_port)

        if gemini_ok:
            return TestResult(
                node=node,
                success=True,
                latency=float(gemini_latency.replace("ms", "")),
                error="",
                response_preview=f"Gemini API ✓ ({gemini_latency})"
            )
        else:
            return TestResult(
                node=node,
                success=False,
                latency=tcp_latency,
                error=f"TCP可达但 {gemini_msg}"
            )

    # 其他情况只返回 TCP 测试结果
    return TestResult(
        node=node,
        success=True,
        latency=tcp_latency,
        error="",
        response_preview="端口可达 ✓ (需代理客户端测试 Gemini)"
    )

# ==================== 报告生成 ====================
def print_results(results: List[TestResult]):
    """打印测试结果"""
    print("\n" + "="*70)
    print("📊 测试结果报告")
    print("="*70)

    success_count = sum(1 for r in results if r.success)
    fail_count = len(results) - success_count

    print(f"\n总计: {len(results)} 个节点 | ✅ 可用: {success_count} | ❌ 不可用: {fail_count}")
    print("-"*70)

    # 按延迟排序
    sorted_results = sorted(results, key=lambda r: (not r.success, r.latency))

    for i, result in enumerate(sorted_results, 1):
        status = "✅" if result.success else "❌"
        latency_str = f"{result.latency:.0f}ms" if result.latency > 0 else "N/A"

        print(f"\n[{i:2d}] {status} {result.node.name}")
        print(f"     协议: {result.node.protocol.upper()} | 服务器: {result.node.server}:{result.node.port}")
        print(f"     延迟: {latency_str}")

        if result.error:
            print(f"     错误: \033[91m{result.error}\033[0m")  # 红色
        elif result.response_preview:
            print(f"     信息: {result.response_preview}")

    print("\n" + "="*70)

def save_report(results: List[TestResult], filename: str = "proxy_report.txt"):
    """保存报告到文件"""
    filepath = os.path.join(os.path.dirname(__file__), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("代理节点测试报告\n")
        f.write("="*70 + "\n\n")

        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        f.write(f"总计: {len(results)} 个节点\n")
        f.write(f"可用: {success_count} | 不可用: {fail_count}\n")
        f.write("-"*70 + "\n\n")

        sorted_results = sorted(results, key=lambda r: (not r.success, r.latency))

        for i, result in enumerate(sorted_results, 1):
            status = "✅" if result.success else "❌"
            f.write(f"[{i:2d}] {status} {result.node.name}\n")
            f.write(f"     协议: {result.node.protocol.upper()}\n")
            f.write(f"     服务器: {result.node.server}:{result.node.port}\n")
            f.write(f"     延迟: {result.latency:.0f}ms\n")
            if result.error:
                f.write(f"     错误: {result.error}\n")
            f.write("\n")

    print(f"\n📄 报告已保存到: {filepath}")

# ==================== 主程序 ====================
def check_pproxy():
    """检查并安装 pproxy"""
    try:
        import pproxy
        return True
    except ImportError:
        print("\n⚠️  检测到缺少 pproxy 库")
        print("    pproxy 用于创建本地代理以测试 Gemini API")
        print()
        choice = input("    是否安装? (y/n): ").strip().lower()
        if choice == 'y':
            print("    正在安装 pproxy...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pproxy"], check=True)
            print("    ✅ 安装完成")
            return True
        else:
            print("    将跳过 Gemini API 测试")
            return False

def main(subscription_url: str = None, test_gemini: bool = True):
    """主程序"""
    print("\n" + "="*70)
    print("🔧 代理节点检测工具 - Gemini API 连通性测试")
    print("="*70)

    # 检查 pproxy
    if test_gemini:
        test_gemini = check_pproxy()

    # 获取订阅链接
    if not subscription_url:
        print("\n请输入订阅链接:")
        url = input(">>> ").strip()
        if not url:
            print("❌ 订阅链接不能为空")
            return
    else:
        url = subscription_url

    # 获取并解析节点
    try:
        content = fetch_subscription(url)
        nodes = parse_nodes(content)
        print(f"✅ 成功解析 {len(nodes)} 个节点")
    except Exception as e:
        print(f"❌ 错误: {e}")
        return

    if not nodes:
        print("❌ 没有找到有效节点")
        return

    # 显示节点列表
    print("\n📋 节点列表:")
    print("-"*50)
    for i, node in enumerate(nodes, 1):
        print(f"  [{i:2d}] {node.protocol.upper():8s} | {node.name}")

    # 开始测试
    test_mode = "Gemini API 测试" if test_gemini else "端口连通测试"
    print(f"\n🧪 开始测试 ({test_mode}, 并发: {MAX_WORKERS}, 超时: {TEST_TIMEOUT}s)...")
    print("-"*50)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_node = {executor.submit(test_node, node, test_gemini): node for node in nodes}

        for future in concurrent.futures.as_completed(future_to_node):
            result = future.result()
            results.append(result)

            status = "✅" if result.success else "❌"
            latency = f"{result.latency:.0f}ms" if result.latency > 0 else "N/A"
            print(f"  {status} {result.node.name} - {latency}")

    # 显示结果
    print_results(results)

    # 保存报告
    save_report(results)

    return results

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            main(sys.argv[1])
        else:
            main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出。")
        sys.exit(0)
