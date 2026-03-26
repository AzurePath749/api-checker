PROVIDERS = {
    "1": {
        "name": "深度求索 DeepSeek",
        "base_url": "https://api.deepseek.com",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "deepseek-chat"
    },
    "2": {
        "name": "阿里云通义千问 Qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "qwen-plus"
    },
    "3": {
        "name": "智谱AI GLM",
        "base_url": "https://open.bigmodel.cn/api/anthropic",
        "models_endpoint": None,
        "models_source_url": "https://open.bigmodel.cn/api/paas/v4/models",
        "chat_endpoint": "/v1/messages",
        "default_model": "glm-5",
        "is_anthropic": True
    },
    "4": {
        "name": "月之暗面 Moonshot",
        "base_url": "https://api.moonshot.cn/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "moonshot-v1-8k"
    },
    "5": {
        "name": "百川智能 Baichuan",
        "base_url": "https://api.baichuan-ai.com/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "Baichuan4"
    },
    "6": {
        "name": "MiniMax 海螺AI",
        "base_url": "https://api.minimax.chat/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "abab6.5-chat"
    },
    "7": {
        "name": "硅基流动 SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "Qwen/Qwen2.5-7B-Instruct"
    },
    "8": {
        "name": "零一万物 Yi",
        "base_url": "https://api.lingyiwanwu.com/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "yi-lightning"
    },

    "11": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "gpt-4o-mini"
    },
    "12": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "models_endpoint": "/models",
        "chat_endpoint": "/models",
        "default_model": "gemini-2.0-flash",
        "is_gemini": True
    },
    "13": {
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com/v1",
        "models_endpoint": None,
        "chat_endpoint": "/messages",
        "default_model": "claude-3-5-sonnet-20241022",
        "is_anthropic": True
    },
    "14": {
        "name": "xAI Grok",
        "base_url": "https://api.x.ai/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "grok-2-1212"
    },
    "15": {
        "name": "Mistral AI",
        "base_url": "https://api.mistral.ai/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "mistral-small-latest"
    },
    "16": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "llama-3.3-70b-versatile"
    },
    "17": {
        "name": "Cohere",
        "base_url": "https://api.cohere.ai/v2",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat",
        "default_model": "command-r",
        "is_cohere": True
    },
    "18": {
        "name": "Perplexity AI",
        "base_url": "https://api.perplexity.ai",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "llama-3.1-sonar-small-128k-online"
    },
    "19": {
        "name": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    },
    "20": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "openai/gpt-4o-mini"
    },
    "21": {
        "name": "Fireworks AI",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "accounts/fireworks/models/llama-v3p1-8b-instruct"
    },
    "22": {
        "name": "Cerebras",
        "base_url": "https://api.cerebras.ai/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "llama-3.3-70b"
    },
    "23": {
        "name": "Replicate",
        "base_url": "https://api.replicate.com/v1",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "meta/llama-2-70b-chat"
    },
    "24": {
        "name": "DeepInfra",
        "base_url": "https://api.deepinfra.com/v1/openai",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "meta-llama/Llama-3.3-70B-Instruct"
    },
    "25": {
        "name": "Novita AI",
        "base_url": "https://api.novita.ai/v3/openai",
        "models_endpoint": "/models",
        "chat_endpoint": "/chat/completions",
        "default_model": "deepseek/deepseek-v3-0324"
    }
}
