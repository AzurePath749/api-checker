# 大模型 API 检测工具 使用说明书

## 目录

- [功能概述](#功能概述)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
- [支持的厂商列表](#支持的厂商列表)
- [常见问题](#常见问题)

---

## 功能概述

本工具用于检测各大 AI 厂商的大模型 API 可用性，主要功能包括：

| 功能 | 说明 |
|------|------|
| **连通性测试** | 快速检测 API 是否可用 |
| **模型列表查询** | 自动获取账户可用的模型列表 |
| **性能测试** | 测量 API 响应延迟 |
| **压力测试** | 连续请求测试稳定性 |
| **Token 统计** | 显示 Token 使用情况 |
| **速率限制查询** | 查看剩余请求额度 (RPM/TPM) |
| **配置保存** | 本地保存 API Key，下次免输入 |

---

## 环境要求

- **Python**: 3.10+
- **依赖库**: `requests`, `urllib3`

安装依赖：
```bash
pip install requests
```

---

## 快速开始

### 1. 启动程序

```bash
python main.py
```

### 2. 主界面

```
============================================================
  🤖 大模型 API 检测工具
============================================================

📍 国内厂商:
  [ 1] 深度求索 DeepSeek
  [ 2] 阿里云通义千问 Qwen
  ...

🌍 国外厂商:
  [11] OpenAI
  [12] Google Gemini
  ...

  ─────────────────────────────────────
  [0]  自定义配置 (自定义端点/模型)
  [Q]  退出
```

### 3. 基本使用流程

```
选择厂商 → 输入API Key → 选择模型 → 查看测试结果 → 压力测试(可选) → 返回主菜单
```

---

## 详细使用指南

### 单个厂商测试

**步骤 1：选择厂商**

输入厂商编号（如 `1` 选择 DeepSeek）

**步骤 2：输入 API Key**

```
请输入 DeepSeek 的 API Key:
  💡 支持批量输入，每行一个，最多20个
  💡 输入空行结束

  API Key [1/20]: sk-xxxxxxxxxxxxxxxx
  API Key [2/20]:
```

**步骤 3：查看模型列表**

```
📋 正在获取可用模型列表...
   ✅ 发现 5 个可用模型
```

**步骤 4：选择测试模型**

分页选择模型，支持输入编号、名称或回车使用默认模型。

**步骤 5：查看测试结果**

测试完成后显示状态码、延迟、模型回复、Token 消耗和速率限制信息。

**步骤 6：压力测试（可选）**

```
是否进行压力测试?
  [1] 快速测试 (5次, 间隔1秒)
  [2] 标准测试 (10次, 间隔2秒)
  [3] 自定义测试
  [其他] 跳过
```

### 批量测试

输入多个 API Key 后，工具会依次测试所有 Key 并生成报告。

### 自定义配置

选择 `[0]` 可使用自定义 API 地址、Key 和模型名进行测试，支持 OpenAI/Anthropic/Gemini 三种格式。

---

## 支持的厂商列表

### 国内厂商

| 编号 | 厂商 | 获取 API Key 地址 |
|:----:|------|-------------------|
| 1 | DeepSeek | https://platform.deepseek.com |
| 2 | 阿里云通义千问 | https://dashscope.console.aliyun.com |
| 3 | 智谱AI (GLM) | https://open.bigmodel.cn |
| 4 | Moonshot (Kimi) | https://platform.moonshot.cn |
| 5 | 百川智能 | https://platform.baichuan-ai.com |
| 6 | MiniMax | https://www.minimaxi.com |
| 7 | 硅基流动 (SiliconFlow) | https://cloud.siliconflow.cn |
| 8 | 零一万物 (Yi) | https://platform.lingyiwanwu.com |

### 国外厂商

| 编号 | 厂商 | 获取 API Key 地址 |
|:----:|------|-------------------|
| 11 | OpenAI (GPT) | https://platform.openai.com |
| 12 | Google Gemini | https://aistudio.google.com/apikey |
| 13 | Anthropic (Claude) | https://console.anthropic.com |
| 14 | xAI (Grok) | https://console.x.ai |
| 15 | Mistral AI | https://console.mistral.ai |
| 16 | Groq | https://console.groq.com |
| 17 | Cohere | https://dashboard.cohere.com |
| 18 | Perplexity AI | https://www.perplexity.ai/settings/api |
| 19 | Together AI | https://api.together.xyz |
| 20 | OpenRouter | https://openrouter.ai/keys |
| 21 | Fireworks AI | https://fireworks.ai/api-keys |
| 22 | Cerebras | https://cloud.cerebras.ai |
| 23 | Replicate | https://replicate.com/account/api-tokens |
| 24 | DeepInfra | https://deepinfra.com/dash/api_keys |
| 25 | Novita AI | https://novita.ai/settings/key-management |

---

## 常见问题

### Q: 如何添加新的厂商？

编辑 `src/api_checker/providers.py` 中的 `PROVIDERS` 字典，按格式添加新厂商配置。

### Q: 测试会消耗 Token 吗？

是的，每次测试都会消耗少量 Token（约 5-20 个）。压力测试会按次数累积消耗。

---

## 文件结构

```
api-checker/
├── main.py                  # 程序入口
├── proxy_checker.py         # 代理节点检测工具
├── pyproject.toml           # 项目配置
├── src/
│   └── api_checker/
│       ├── __init__.py      # 包初始化
│       ├── checker.py       # 核心检测逻辑
│       ├── providers.py     # 厂商配置
│       └── errors.py        # 错误翻译
├── tests/                   # 测试目录
└── data/                    # 测试报告输出目录
```
