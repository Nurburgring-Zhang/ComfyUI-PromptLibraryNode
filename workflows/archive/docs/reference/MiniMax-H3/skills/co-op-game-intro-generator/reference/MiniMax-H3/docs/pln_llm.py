# ============================================================
# LLM 调用封装 — AI请求/翻译/重试
# ============================================================
import json
import urllib.request
import urllib.error
import urllib.parse
import time as _time
import random


def _validate_api_url(api_url):
    """校验API URL协议，防止SSRF攻击"""
    if not api_url:
        return False, "API地址为空"
    try:
        parsed = urllib.parse.urlparse(api_url)
        if parsed.scheme not in ('http', 'https'):
            return False, f"不支持的URL协议: {parsed.scheme}，仅支持 http/https"
        if not parsed.hostname:
            return False, "URL缺少主机名"
        return True, ""
    except Exception as e:
        return False, f"URL格式错误: {str(e)[:100]}"


def call_ai(api_url, api_key, model_name, system_prompt, user_message, temperature, max_tokens):
    """调用AI API（OpenAI兼容格式），带指数退避重试+抖动
    
    返回:
        tuple: (result_text, error_text)
            - 成功时: (结果文本, "")
            - 失败时: ("", 错误描述)
    """
    if not api_url:
        return "", "API地址为空"

    # [P3修复] URL协议校验，防止SSRF
    valid, err_msg = _validate_api_url(api_url)
    if not valid:
        return "", err_msg

    last_error = ""
    for attempt in range(3):
        try:
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_message})

            payload = {
                "model": model_name or "default",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            if "choices" in result and len(result["choices"]) > 0:
                c = result["choices"][0]
                content = c.get("message", {}).get("content", "") or c.get("text", "")
                return content.strip(), ""

            elif "response" in result:
                return result["response"].strip(), ""

            return "", f"API格式异常: {str(result)[:200]}"

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            last_error = f"HTTP {e.code}: {body}"

            if e.code in (429, 502, 503, 504) and attempt < 2:
                # 指数退避 + 抖动
                delay = (2 ** attempt) + random.uniform(0, 1)
                _time.sleep(delay)
                continue
            return "", last_error

        except urllib.error.URLError as e:
            reason = str(e.reason)[:100] if e.reason else "未知"
            last_error = f"连接失败: {reason}"
            if attempt < 2:
                delay = (2 ** attempt) + random.uniform(0, 1)
                _time.sleep(delay)
                continue
            return "", last_error

        except Exception as e:
            last_error = f"错误: {str(e)[:100]}"
            if attempt < 2:
                _time.sleep(1)
                continue
            return "", last_error

    return "", last_error


def translate_prompt(text, direction, api_url, api_key, model_name, temperature, max_tokens):
    """翻译提示词"""
    if not text or not api_url:
        return ""

    prefixes = {
        "中译英": "将以下中文翻译成英文",
        "英译中": "将以下英文翻译成中文",
        "日译中": "将以下日文翻译成中文",
    }
    prefix = prefixes.get(direction, prefixes["中译英"])
    sys_p = "You are a professional translator. Output only the translated text."
    user_msg = f"{prefix}，只输出翻译结果：\n\n{text}"

    result, _ = call_ai(api_url, api_key, model_name, sys_p, user_msg, temperature, max_tokens)
    return result
