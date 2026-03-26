import json
import re

ERROR_TRANSLATIONS = {
    "insufficient_quota": "配额不足",
    "insufficient funds": "余额不足",
    "rate limit": "请求频率超限",
    "rate_limit": "请求频率超限",
    "too many requests": "请求过于频繁",
    "invalid api key": "API密钥无效",
    "invalid_api_key": "API密钥无效",
    "unauthorized": "未授权，请检查API密钥",
    "authentication": "认证失败",
    "permission denied": "权限被拒绝",
    "access denied": "访问被拒绝",
    "model not found": "模型不存在",
    "model_not_found": "模型不存在",
    "does not exist": "不存在",
    "not found": "未找到",
    "context length": "上下文长度超限",
    "context_length": "上下文长度超限",
    "maximum context": "最大上下文超限",
    "token limit": "Token限制",
    "max_tokens": "最大Token数超限",
    "billing not active": "账单未激活",
    "billing_not_active": "账单未激活",
    "quota exceeded": "配额已用尽",
    "quota_exceeded": "配额已用尽",
    "credits": "余额不足",
    "balance": "余额不足",
    "payment required": "需要付费",
    "overloaded": "服务过载",
    "overload": "服务过载",
    "server error": "服务器错误",
    "internal error": "内部错误",
    "service unavailable": "服务不可用",
    "timeout": "请求超时",
    "timed out": "请求超时",
    "connection": "连接失败",
    "network": "网络错误",

    "余额不足": "账户余额不足，请充值",
    "无可用资源包": "没有可用的资源包",
    "请充值": "请充值后重试",
    "资源包": "资源包",
    "次数用尽": "调用次数已用尽",
    "账号异常": "账号状态异常",
    "模型下线": "该模型已下线",
    "参数错误": "请求参数有误",
    "内容违规": "内容不符合规范",
    "敏感词": "包含敏感词",
    "审核不通过": "内容审核未通过",
}


def translate_error(error_text):
    if not error_text:
        return "", ""

    message = error_text

    try:
        data = json.loads(error_text)
        if 'error' in data:
            err = data['error']
            if isinstance(err, dict):
                message = err.get('message', error_text)
            else:
                message = str(err)
    except Exception:
        pass

    translation = ""
    message_lower = message.lower()

    for key, trans in ERROR_TRANSLATIONS.items():
        if key.lower() in message_lower:
            translation = trans
            break

    if re.search(r'[\u4e00-\u9fff]', message) and not translation:
        return message, ""

    return message, translation
