import json
import os
import time
import random
import datetime
import logging

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from .providers import PROVIDERS
from .errors import translate_error

RATE_LIMIT_HEADERS = [
    'x-ratelimit-limit-requests', 'x-ratelimit-remaining-requests',
    'x-ratelimit-limit-tokens', 'x-ratelimit-remaining-tokens',
    'x-request-id', 'ratelimit-limit', 'ratelimit-remaining',
]

SENSITIVE_HEADER_KEYWORDS = ('key', 'token', 'auth')


def _mask_api_key(api_key):
    if len(api_key) > 12:
        return f"{api_key[:8]}...{api_key[-4:]}"
    return api_key


def _is_sensitive_header(key):
    return any(kw in key.lower() for kw in SENSITIVE_HEADER_KEYWORDS)


def _mask_header_value(key, value):
    if _is_sensitive_header(key):
        if len(value) > 12:
            return f"{value[:8]}...{value[-4:]}"
        return "***"
    return value


def _print_request_info(req, flush=False):
    print("\n" + "─" * 50, flush=flush)
    print("📤 发送给服务器的请求:", flush=flush)
    print("─" * 50, flush=flush)
    if not req:
        return
    print(f"   请求地址: {req['url']}", flush=flush)
    print(f"   请求头:", flush=flush)
    for k, v in req['headers'].items():
        print(f"      {k}: {_mask_header_value(k, v)}", flush=flush)
    print(f"   请求体:", flush=flush)
    print(f"      {json.dumps(req['body'], ensure_ascii=False, indent=6)}", flush=flush)


def _print_response_info(result, show_raw=False, flush=False):
    print("\n" + "─" * 50, flush=flush)
    print("📥 服务器响应:", flush=flush)
    print("─" * 50, flush=flush)
    print(f"   状态码: {result['status_code']}", flush=flush)
    print(f"   延迟: {result['latency']:.2f}s", flush=flush)

    if result['success']:
        print(f"   状态: ✅ 成功", flush=flush)

        if show_raw and result.get('raw_response'):
            print(f"\n   响应内容:", flush=flush)
            try:
                resp_json = json.loads(result['raw_response'])
                print(f"   {json.dumps(resp_json, ensure_ascii=False, indent=3)}", flush=flush)
            except Exception:
                print(f"   {result['raw_response']}", flush=flush)

        meaning_parts = []
        if result['response_text']:
            meaning_parts.append(f"模型回复: {result['response_text']}")
        if result['usage']:
            usage = result['usage']
            meaning_parts.append(
                f"Token消耗: 输入{usage.get('prompt_tokens', 'N/A')} "
                f"+ 输出{usage.get('completion_tokens', 'N/A')} "
                f"= 总计{usage.get('total_tokens', 'N/A')}"
            )
        meaning_parts.append("API连接正常")
        print(f"   \033[92m返回含义: {' | '.join(meaning_parts)}\033[0m", flush=flush)
    else:
        print(f"   状态: ❌ 失败", flush=flush)
        if result['error']:
            print(f"\n   响应内容:", flush=flush)
            try:
                err_json = json.loads(result['error'])
                print(f"   {json.dumps(err_json, ensure_ascii=False, indent=3)}", flush=flush)
            except Exception:
                print(f"   {result['error'][:200]}", flush=flush)
            _, translation = translate_error(result['error'])
            if translation:
                print(f"   \033[91m💡 错误含义: {translation}\033[0m", flush=flush)

    print("─" * 50, flush=flush)

    if result.get('rate_limit'):
        print("\n⏱️ 速率限制信息:", flush=flush)
        for k, v in result['rate_limit'].items():
            print(f"   {k}: {v}", flush=flush)


class APIChecker:
    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def show_main_menu(self):
        self.clear_screen()
        self.print_header("🤖 大模型 API 检测工具")

        print("\n📍 国内厂商:")
        domestic = {k: v for k, v in PROVIDERS.items() if int(k) <= 10}
        for key, provider in domestic.items():
            print(f"  [{key:>2}] {provider['name']}")

        print("\n🌍 国外厂商:")
        international = {k: v for k, v in PROVIDERS.items() if int(k) > 10}
        for key, provider in international.items():
            print(f"  [{key}] {provider['name']}")

        print(f"\n  ─────────────────────────────────────")
        print(f"  [0]  自定义配置 (自定义端点/模型)")
        print(f"  [Q]  退出")
        print()

    def get_api_key(self, provider_key):
        provider = PROVIDERS[provider_key]
        print(f"\n请输入 {provider['name']} 的 API Key:")
        print("  💡 支持批量输入，每行一个，最多20个")
        print("  💡 输入空行结束")
        print()

        api_keys = []
        for i in range(20):
            key = input(f"  API Key [{i+1}/20]: ").strip()
            if not key:
                break
            api_keys.append(key)

        return api_keys if api_keys else None

    def get_available_models(self, provider, api_key):
        if provider.get('models_source_url'):
            try:
                response = self.session.get(
                    provider['models_source_url'],
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=15
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    if 'data' in data:
                        models = [m['id'] for m in data['data']]
                    return models if models else None
            except Exception as e:
                logging.debug(f"获取模型列表失败 (models_source_url): {e}")
            if 'bigmodel' in provider['base_url']:
                return [
                    "glm-5", "glm-5-turbo", "glm-4.5", "glm-4.5-air",
                    "glm-4-plus", "glm-4", "glm-4-air", "glm-4-airx",
                    "glm-4-long", "glm-4-flash", "glm-4v", "glm-4v-plus"
                ]
            else:
                return [
                    "claude-opus-4-6-20250514",
                    "claude-sonnet-4-6-20250519",
                    "claude-3-5-sonnet-20241022",
                    "claude-3-5-haiku-20241022",
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ]

        if provider.get('is_gemini'):
            try:
                response = self.session.get(
                    f"{provider['base_url']}{provider['models_endpoint']}",
                    headers={"x-goog-api-key": api_key},
                    timeout=15
                )
                if response.status_code == 200:
                    data = response.json()
                    models = []
                    if 'models' in data:
                        for m in data['models']:
                            name = m.get('name', '').replace('models/', '')
                            if name and 'embed' not in name.lower():
                                models.append(name)
                    return models if models else None
                return None
            except Exception as e:
                logging.debug(f"获取 Gemini 模型列表失败: {e}")
                return None

        try:
            response = self.session.get(
                f"{provider['base_url']}{provider['models_endpoint']}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                models = []
                if 'data' in data:
                    models = [m['id'] for m in data['data']]
                elif isinstance(data, list):
                    models = [m['id'] if 'id' in m else m.get('name', str(m)) for m in data]
                if len(models) > 50:
                    print(f"   ℹ️ 模型列表已截断，共 {len(models)} 个，仅显示前50个")
                return models[:50]
            else:
                return None
        except Exception as e:
            logging.debug(f"获取模型列表失败: {e}")
            return None

    def test_single_request(self, provider, api_key, model=None):
        if model is None:
            model = provider['default_model']

        start_time = time.time()
        result = {
            "success": False,
            "latency": 0,
            "status_code": 0,
            "error": None,
            "rate_limit": {},
            "usage": None,
            "response_text": "",
            "raw_response": "",
            "request_info": {}
        }

        try:
            if provider.get('is_anthropic'):
                url = f"{provider['base_url']}{provider['chat_endpoint']}"
                headers = {
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                body = {
                    "model": model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "你好"}]
                }
            elif provider.get('is_gemini'):
                url = f"{provider['base_url']}/models/{model}:generateContent"
                headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
                body = {
                    "contents": [{"parts": [{"text": "你好"}]}],
                    "generationConfig": {"maxOutputTokens": 10}
                }
            elif provider.get('is_cohere'):
                url = f"{provider['base_url']}{provider['chat_endpoint']}"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                body = {
                    "model": model,
                    "messages": [{"role": "user", "content": "你好"}]
                }
            else:
                url = f"{provider['base_url']}{provider['chat_endpoint']}"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                body = {
                    "model": model,
                    "messages": [{"role": "user", "content": "你好"}],
                    "max_tokens": 5
                }

            result["request_info"] = {"url": url, "headers": headers, "body": body}
            response = self.session.post(url, headers=headers, json=body, timeout=30)

            result["latency"] = time.time() - start_time
            result["status_code"] = response.status_code

            rate_limit_info = {}
            for key in RATE_LIMIT_HEADERS:
                if key in response.headers:
                    rate_limit_info[key] = response.headers[key]
            result["rate_limit"] = rate_limit_info

            if response.status_code == 200:
                result["success"] = True
                data = response.json()
                result["raw_response"] = response.text

                if provider.get('is_gemini'):
                    candidates = data.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        if parts:
                            result["response_text"] = parts[0].get('text', '')[:50]
                    usage_meta = data.get('usageMetadata', {})
                    result["usage"] = {
                        "prompt_tokens": usage_meta.get('promptTokenCount', 0),
                        "completion_tokens": usage_meta.get('candidatesTokenCount', 0),
                        "total_tokens": usage_meta.get('totalTokenCount', 0)
                    }
                elif provider.get('is_anthropic'):
                    content = data.get('content', [])
                    if content:
                        result["response_text"] = content[0].get('text', '')[:50]
                    usage = data.get('usage', {})
                    result["usage"] = {
                        "prompt_tokens": usage.get('input_tokens', 0),
                        "completion_tokens": usage.get('output_tokens', 0),
                        "total_tokens": usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
                    }
                elif provider.get('is_cohere'):
                    message = data.get('message', {})
                    content = message.get('content', [])
                    if content:
                        result["response_text"] = content[0].get('text', '')[:50]
                    meta = data.get('meta', {})
                    tokens = meta.get('tokens', {})
                    result["usage"] = {
                        "prompt_tokens": tokens.get('input_tokens', 0),
                        "completion_tokens": tokens.get('output_tokens', 0),
                        "total_tokens": tokens.get('input_tokens', 0) + tokens.get('output_tokens', 0)
                    }
                else:
                    result["usage"] = data.get('usage', {})
                    result["response_text"] = data.get('choices', [{}])[0].get('message', {}).get('content', '')[:50]
            else:
                result["error"] = response.text[:200]

        except requests.exceptions.Timeout:
            result["latency"] = time.time() - start_time
            result["error"] = "请求超时 (>30s)"
        except Exception as e:
            result["latency"] = time.time() - start_time
            result["error"] = str(e)[:200]

        return result

    def run_stress_test(self, provider, api_key, model, runs=5, interval=1):
        print(f"\n🔥 开始压力测试 (次数: {runs}, 间隔: {interval}s)")
        print("-" * 50)

        success_count = 0
        total_latency = 0
        latencies = []

        for i in range(1, runs + 1):
            result = self.test_single_request(provider, api_key, model)
            latencies.append(result['latency'])

            if result['success']:
                success_count += 1
                total_latency += result['latency']
                print(f"  [{i}/{runs}] ✅ 成功 | 延迟: {result['latency']:.2f}s")
            else:
                error_display = result['error'][:30] if result['error'] else 'Unknown'
                print(f"  [{i}/{runs}] ❌ 失败 | 延迟: {result['latency']:.2f}s | {error_display}")

            if i < runs:
                time.sleep(interval)

        print("-" * 50)
        if success_count > 0:
            avg = total_latency / success_count
            min_lat = min(latencies)
            max_lat = max(latencies)
            print(f"📊 压测结果: 成功率 {success_count}/{runs} ({success_count/runs*100:.0f}%)")
            print(f"   平均延迟: {avg:.2f}s | 最小: {min_lat:.2f}s | 最大: {max_lat:.2f}s")
        else:
            print(f"📊 压测结果: 全部失败 (0/{runs})")

    def select_model_with_pagination(self, models, default_model):
        if not models:
            print(f"\n⚠️ 无法从API获取模型列表")
            print(f"   默认模型: {default_model}")
            print(f"\n   [回车] 使用默认模型")
            print(f"   [输入] 手动输入模型名称")

            choice = input("\n请选择: ").strip()
            if choice == "":
                return default_model
            return choice

        page_size = 10
        total_pages = (len(models) + page_size - 1) // page_size
        current_page = 0

        while True:
            print(f"\n📋 可用模型 (第 {current_page + 1}/{total_pages} 页, 共 {len(models)} 个):")
            print("─" * 55)

            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(models))

            for i in range(start_idx, end_idx):
                default_mark = " ⭐默认" if models[i] == default_model else ""
                print(f"  [{i + 1:>3}] {models[i]}{default_mark}")

            print("─" * 55)

            nav_hints = []
            if current_page > 0:
                nav_hints.append("[P] 上一页")
            if current_page < total_pages - 1:
                nav_hints.append("[N] 下一页")
            nav_hints.append("[数字] 选择模型")
            nav_hints.append("[名称] 直接输入模型名")
            nav_hints.append("[回车] 使用默认模型")

            print(" | ".join(nav_hints))

            choice = input("\n请选择: ").strip()

            if choice == "":
                return default_model
            elif choice.upper() == 'P' and current_page > 0:
                current_page -= 1
                continue
            elif choice.upper() == 'N' and current_page < total_pages - 1:
                current_page += 1
                continue
            elif choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(models):
                    return models[idx - 1]
                else:
                    print(f"❌ 请输入 1-{len(models)} 之间的数字")
            elif choice:
                if choice in models:
                    return choice
                matches = [m for m in models if choice.lower() in m.lower()]
                if len(matches) == 1:
                    print(f"✅ 匹配到: {matches[0]}")
                    return matches[0]
                elif len(matches) > 1:
                    print(f"找到多个匹配: {matches[:5]}")
                else:
                    confirm = input(f"模型 '{choice}' 不在列表中，仍要使用? (y/N): ").strip().lower()
                    if confirm == 'y':
                        return choice
                    print("请重新选择")

    def save_batch_results(self, provider, model, results):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_test_{provider['name']}_{timestamp}.txt"
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        success_keys = []
        failed_keys = []

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"批量API测试报告\n")
            f.write(f"{'='*60}\n")
            f.write(f"厂商: {provider['name']}\n")
            f.write(f"模型: {model}\n")
            f.write(f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")

            success_count = sum(1 for r in results if r['result']['success'])
            f.write(f"总计: {len(results)} 个\n")
            f.write(f"成功: {success_count} | 失败: {len(results) - success_count}\n")
            f.write(f"{'-'*60}\n\n")

            f.write("✅ 可用的 API Key:\n")
            f.write("-"*40 + "\n")
            for item in results:
                if item['result']['success']:
                    f.write(f"{_mask_api_key(item['api_key'])}\n")
                    success_keys.append(item['api_key'])
            if not success_keys:
                f.write("(无)\n")

            f.write(f"\n❌ 不可用的 API Key:\n")
            f.write("-"*40 + "\n")
            for item in results:
                if not item['result']['success']:
                    _, translation = translate_error(item['result'].get('error', ''))
                    f.write(f"{item['api_key']} | {translation or '失败'}\n")
                    failed_keys.append(item['api_key'])
            if not failed_keys:
                f.write("(无)\n")

        print(f"\n📄 报告已保存到: {filepath}")

        if success_keys:
            print(f"\n✅ 可用的 API Key ({len(success_keys)} 个):")
            for key in success_keys:
                print(f"   {_mask_api_key(key)}")

    def test_provider(self, provider_key):
        provider = PROVIDERS[provider_key]
        self.clear_screen()
        self.print_header(f"🔍 测试 {provider['name']}")

        api_keys = self.get_api_key(provider_key)
        if not api_keys:
            print("❌ API Key 不能为空!")
            input("\n按回车返回...")
            return

        is_batch = len(api_keys) > 1

        print(f"\n📡 正在连接 {provider['base_url']} ...")
        print("\n📋 正在获取可用模型列表...")
        models = self.get_available_models(provider, api_keys[0])

        if models:
            print(f"   ✅ 发现 {len(models)} 个可用模型")
        else:
            print("   ⚠️ 无法获取模型列表，将使用默认模型")

        selected_model = self.select_model_with_pagination(models, provider['default_model'])

        if is_batch:
            self.run_batch_test(provider, api_keys, selected_model)
        else:
            print(f"\n🎯 选中模型: {selected_model}")
            print("\n🧪 执行单次连接测试...")
            result = self.test_single_request(provider, api_keys[0], selected_model)
            self.display_single_result(result, provider, api_keys[0], selected_model)

        input("\n按回车返回主菜单...")

    def run_batch_test(self, provider, api_keys, selected_model):
        print("\n" + "=" * 60, flush=True)
        print(f"🎯 选中模型: {selected_model}", flush=True)
        print(f"🚀 批量测试模式 - 共 {len(api_keys)} 个 API Key", flush=True)
        print(f"   间隔: 3~5秒随机 | 预计耗时: ~{len(api_keys) * 5}秒", flush=True)
        print("=" * 60, flush=True)
        print("", flush=True)

        results = []
        success_count = 0

        for i, api_key in enumerate(api_keys, 1):
            key_display = _mask_api_key(api_key)
            print(f"\n[{i}/{len(api_keys)}] 测试: {key_display}", flush=True)

            result = self.test_single_request(provider, api_key, selected_model)
            results.append({
                'api_key': api_key,
                'result': result
            })

            if result['success']:
                success_count += 1
                print(f"   ✅ 成功 | 延迟: {result['latency']:.2f}s", flush=True)
                if result['response_text']:
                    print(f"   📝 回复: {result['response_text'][:50]}...", flush=True)
            else:
                error_msg = result.get('error', 'Unknown')
                _, translation = translate_error(error_msg)
                print(f"   ❌ 失败 | \033[91m{translation or error_msg[:80]}\033[0m", flush=True)

            if i < len(api_keys):
                wait_time = random.randint(3, 5)
                print(f"   ⏳ 等待 {wait_time}秒...", flush=True)
                time.sleep(wait_time)

            _print_request_info(result.get('request_info'), flush=True)
            _print_response_info(result, flush=True)

        print("\n" + "=" * 60)
        print("📊 批量测试结果汇总")
        print("=" * 60)
        print(f"\n总计: {len(api_keys)} 个 | ✅ 成功: {success_count} | ❌ 失败: {len(api_keys) - success_count}")
        print("─" * 60)

        sorted_results = sorted(results, key=lambda x: (not x['result']['success'], x['result']['latency']))

        for i, item in enumerate(sorted_results, 1):
            api_key = item['api_key']
            result = item['result']
            key_display = _mask_api_key(api_key)
            status = "✅" if result['success'] else "❌"

            if result['success']:
                print(f"  [{i:2d}] {status} {key_display} | 延迟: {result['latency']:.2f}s")
            else:
                _, translation = translate_error(result.get('error', ''))
                print(f"  [{i:2d}] {status} {key_display} | \033[91m{translation or '失败'}\033[0m")

        self.save_batch_results(provider, selected_model, results)
        print("\n✅ 测试完成！", flush=True)

    def display_single_result(self, result, provider, api_key, selected_model):
        _print_request_info(result.get('request_info'))
        _print_response_info(result, show_raw=True)

        if result['success']:
            print("\n是否进行压力测试?")
            print("  [1] 快速测试 (5次, 间隔1秒)")
            print("  [2] 标准测试 (10次, 间隔2秒)")
            print("  [3] 自定义测试")
            print("  [其他] 跳过")

            choice = input("\n请选择: ").strip()

            if choice == '1':
                self.run_stress_test(provider, api_key, selected_model, runs=5, interval=1)
            elif choice == '2':
                self.run_stress_test(provider, api_key, selected_model, runs=10, interval=2)
            elif choice == '3':
                try:
                    runs = int(input("测试次数 (默认5): ") or "5")
                    interval = float(input("间隔秒数 (默认1): ") or "1")
                    self.run_stress_test(provider, api_key, selected_model, runs=runs, interval=interval)
                except ValueError:
                    print("输入无效，跳过压力测试")

    def test_custom(self):
        self.clear_screen()
        self.print_header("⚙️ 自定义配置测试")

        print("\n请选择API格式:")
        print("  [1] OpenAI 兼容格式 (大多数厂商)")
        print("  [2] Anthropic 格式 (Claude/智谱Anthropic端点)")
        print("  [3] Gemini 格式")

        format_choice = input("\n请选择: ").strip()

        if format_choice == '2':
            api_format = 'anthropic'
        elif format_choice == '3':
            api_format = 'gemini'
        else:
            api_format = 'openai'

        print("\n请输入配置信息:")
        base_url = input("API地址 (如 https://api.example.com/v1): ").strip()
        if not base_url:
            print("❌ API地址不能为空!")
            input("\n按回车返回...")
            return

        api_key = input("API Key: ").strip()
        if not api_key:
            print("❌ API Key不能为空!")
            input("\n按回车返回...")
            return

        model = input("模型名称 (如 gpt-4o-mini): ").strip()
        if not model:
            print("❌ 模型名称不能为空!")
            input("\n按回车返回...")
            return

        custom_provider = {
            "name": "自定义",
            "base_url": base_url,
            "chat_endpoint": "/chat/completions" if api_format != 'anthropic' else "/v1/messages",
            "default_model": model
        }

        if api_format == 'anthropic':
            custom_provider["is_anthropic"] = True
        elif api_format == 'gemini':
            custom_provider["is_gemini"] = True
            custom_provider["chat_endpoint"] = f"/models/{model}:generateContent"

        print(f"\n🎯 配置信息:")
        print(f"   API地址: {base_url}")
        print(f"   模型: {model}")
        print(f"   格式: {api_format}")

        print("\n🧪 执行连接测试...")
        result = self.test_single_request(custom_provider, api_key, model)
        _print_request_info(result.get('request_info'))
        _print_response_info(result, show_raw=True)

        input("\n按回车返回主菜单...")

    def run(self):
        while True:
            self.show_main_menu()
            choice = input("请选择: ").strip().upper()

            if choice == 'Q':
                print("\n👋 再见!")
                break
            elif choice == '0':
                self.test_custom()
            elif choice in PROVIDERS:
                self.test_provider(choice)
            else:
                print("无效选择，请重试")
                time.sleep(1)

    def close(self):
        try:
            self.session.close()
        except Exception:
            pass
