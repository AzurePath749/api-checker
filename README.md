# 🤖 大模型 API 检测工具 使用说明书

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
| 🔍 **连通性测试** | 快速检测 API 是否可用 |
| 📋 **模型列表查询** | 自动获取账户可用的模型列表 |
| 📊 **性能测试** | 测量 API 响应延迟 |
| 🔥 **压力测试** | 连续请求测试稳定性 |
| 📈 **Token 统计** | 显示 Token 使用情况 |
| ⏱️ **速率限制查询** | 查看剩余请求额度 (RPM/TPM) |
| 💾 **配置保存** | 本地保存 API Key，下次免输入 |

---

## 环境要求

- **Python**: 3.7+
- **依赖库**: `requests`

安装依赖：
```bash
pip install requests
```

---

## 快速开始

### 1. 启动程序

```bash
python api_checker.py
```

### 2. 主界面

```
============================================================
  🤖 大模型 API 检测工具
============================================================

请选择要检测的厂商:

  [1] DeepSeek
  [2] 阿里云通义千问
  [3] 智谱AI (GLM)
  [4] OpenAI
  [5] Moonshot (Kimi)
  [6] 百川智能
  [7] MiniMax
  [8] Groq
  [9] Anthropic (Claude)
  [10] 硅基流动 (SiliconFlow)

  [S] 查看所有已保存的配置
  [D] 删除已保存的配置
  [A] 全部测试(已保存的配置)
  [Q] 退出
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
API Key: sk-xxxxxxxxxxxxxxxx
是否保存此配置? (Y/n): y
```

> 💡 保存后下次可直接使用，无需重复输入

**步骤 3：查看模型列表**

```
📋 正在获取可用模型列表...
   ✅ 发现 5 个可用模型:
      1. deepseek-chat (默认)
      2. deepseek-coder
      3. deepseek-reasoner
```

**步骤 4：选择测试模型**

```
请选择要测试的模型 (直接回车使用默认: deepseek-chat):
模型编号或完整名称: 2    ← 输入编号或完整名称，回车使用默认
```

**步骤 5：查看测试结果**

```
──────────────────────────────────────────────────
📊 测试结果:
──────────────────────────────────────────────────
   状态: ✅ 成功
   延迟: 1.23s
   响应: Hello! How can I assist you today?

   📈 Token 使用情况:
      输入: 8
      输出: 10
      总计: 18

   ⏱️ 速率限制信息:
      x-ratelimit-remaining-requests: 500
      x-ratelimit-remaining-tokens: 100000
──────────────────────────────────────────────────
```

**步骤 6：压力测试（可选）**

```
是否进行压力测试?
  [1] 快速测试 (5次, 间隔1秒)
  [2] 标准测试 (10次, 间隔2秒)
  [3] 自定义测试
  [其他] 跳过

请选择: 1

🔥 开始压力测试 (次数: 5, 间隔: 1s)
──────────────────────────────────────────────────
  [1/5] ✅ 成功 | 延迟: 1.15s
  [2/5] ✅ 成功 | 延迟: 1.08s
  [3/5] ✅ 成功 | 延迟: 1.22s
  [4/5] ✅ 成功 | 延迟: 1.11s
  [5/5] ✅ 成功 | 延迟: 1.05s
──────────────────────────────────────────────────
📊 压测结果: 成功率 5/5 (100%)
   平均延迟: 1.12s | 最小: 1.05s | 最大: 1.22s
```

### 批量测试

保存多个厂商配置后，选择 `[A] 全部测试` 可一次性测试所有已保存的 API：

```
============================================================
  🚀 批量测试所有已保存配置
============================================================

测试 DeepSeek...
测试 阿里云通义千问...
测试 OpenAI...

============================================================
📊 批量测试结果汇总:
============================================================
  ✅ DeepSeek            | 延迟: 1.23s
  ✅ 阿里云通义千问        | 延迟: 0.89s
  ❌ OpenAI             | 延迟: 3.45s
```

### 配置管理

**查看已保存配置**：选择 `[S]`

**删除配置**：选择 `[D]`，可删除单个或全部

---

## 支持的厂商列表

### 📍 国内厂商

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

### 🌍 国外厂商

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

## 测试结果说明

### 状态码含义

| 状态 | 说明 |
|------|------|
| ✅ 成功 | API 正常可用 |
| ❌ 失败 | 请求被拒绝或出错 |
| ⚠️ 异常 | 网络错误或超时 |

### 常见 HTTP 状态码

| 状态码 | 含义 | 解决方法 |
|--------|------|----------|
| 200 | 成功 | - |
| 401 | API Key 无效 | 检查 Key 是否正确 |
| 403 | 权限不足 | 检查账户余额/权限 |
| 429 | 请求过于频繁 | 稍后重试或降低频率 |
| 500/502/503 | 服务器错误 | 厂商服务问题，稍后重试 |

### 速率限制字段说明

| 字段 | 说明 |
|------|------|
| `x-ratelimit-remaining-requests` | 剩余请求数 (RPM) |
| `x-ratelimit-remaining-tokens` | 剩余 Token 数 (TPM) |
| `x-ratelimit-limit-requests` | 请求限制上限 |
| `x-ratelimit-limit-tokens` | Token 限制上限 |

> ⚠️ 不同厂商返回的字段可能不同，部分厂商不提供这些信息

---

## 常见问题

### Q: API Key 保存在哪里？

保存在程序同目录下的 `api_configs.json` 文件中。

### Q: 如何添加新的厂商？

编辑 `api_checker.py` 中的 `PROVIDERS` 字典，按格式添加新厂商配置。

### Q: 为什么获取不到模型列表？

可能原因：
- API Key 权限不足
- 厂商不支持 `/models` 接口
- 网络问题

### Q: 压力测试有什么用？

可以测试：
- API 稳定性
- 响应延迟波动
- 是否触发速率限制

### Q: 测试会消耗 Token 吗？

是的，每次测试都会消耗少量 Token（约 5-20 个）。压力测试会按次数累积消耗。

---

## 文件说明

```
api检测代码/
├── api_checker.py      # 主程序
├── api_configs.json    # 保存的配置（运行后生成）
└── README.md           # 本说明文档
```

---

## 更新日志

**v1.0.0** (2024-03)
- 支持 10 家主流厂商
- 单次测试和压力测试
- 配置保存和管理
- 批量测试功能

---

如有问题或建议，欢迎反馈！
