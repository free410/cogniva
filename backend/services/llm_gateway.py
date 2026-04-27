from typing import Optional, List, Dict, Any, AsyncIterator, Iterator
import httpx
import asyncio
from openai import OpenAI
from core.config import settings


class AsyncIterableAdapter:
    """将同步生成器适配为异步迭代器，使用线程池避免阻塞"""
    def __init__(self, sync_gen_fn):
        self.sync_gen_fn = sync_gen_fn
        self._queue: asyncio.Queue = asyncio.Queue()
        self._done = False

    def _sync_iter(self):
        """在单独线程中运行同步生成器"""
        gen = self.sync_gen_fn()
        for item in gen:
            self._queue.put_nowait(item)
        self._queue.put_nowait(None)  # 发送结束信号

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._done:
            raise StopAsyncIteration
        
        # 首次调用时启动线程
        if not hasattr(self, '_started'):
            self._started = True
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._sync_iter)
        
        item = await self._queue.get()
        if item is None:
            self._done = True
            raise StopAsyncIteration
        return item


class LLMError(Exception):
    """LLM 相关错误基类"""
    def __init__(self, message: str, provider: str, status_code: Optional[int] = None):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider}] {message}")


class LLMGateway:
    """统一的 LLM API 封装层，支持多提供商切换"""

    # 支持的提供商配置
    PROVIDER_CONFIG = {
        "deepseek": {
            "models": ["deepseek-chat", "deepseek-coder"],
            "default_model": "deepseek-chat",
            "supports_streaming": True,
            "supports_function_calling": True,
        },
        "openai": {
            "models": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "default_model": "gpt-4-turbo-preview",
            "supports_streaming": True,
            "supports_function_calling": True,
        },
        "anthropic": {
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "default_model": "claude-3-sonnet-20240229",
            "supports_streaming": True,
            "supports_function_calling": False,
        },
        "ollama": {
            "models": ["llama3", "llama2", "mistral", "codellama"],
            "default_model": "llama3",
            "supports_streaming": True,
            "supports_function_calling": False,
        },
        "dashscope": {
            "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "default_model": "qwen-turbo",
            "supports_streaming": True,
            "supports_function_calling": False,
        }
    }

    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self._init_providers()

    def _init_providers(self):
        """初始化所有可用的提供商"""
        # 禁用 langchain 依赖的提供商
        # if settings.OPENAI_API_KEY:
        #     self.providers["openai"] = self._init_openai()

        # if settings.ANTHROPIC_API_KEY:
        #     self.providers["anthropic"] = self._init_anthropic()

        if settings.DEEPSEEK_API_KEY:
            self.providers["deepseek"] = self._init_deepseek()

        # Ollama 和 DashScope 不需要预初始化
        self.providers["ollama"] = "available"
        self.providers["dashscope"] = "available" if settings.DASHSCOPE_API_KEY else None

    # 已禁用 - 如需启用请安装 langchain-openai
    # def _init_openai(self) -> Optional[ChatOpenAI]:
    #     return ChatOpenAI(...)
    #
    # def _init_anthropic(self) -> Optional[ChatAnthropic]:
    #     return ChatAnthropic(...)

    def _init_deepseek(self) -> Optional[OpenAI]:
        return OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """获取所有可用的提供商列表"""
        available = []
        for name, config in self.PROVIDER_CONFIG.items():
            is_available = self.providers.get(name) is not None
            if name in ["ollama", "dashscope"]:
                is_available = self.providers.get(name) == "available"

            available.append({
                "name": name,
                "display_name": config["models"][0].split("-")[0].title() if config["models"] else name,
                "models": config["models"],
                "default_model": config["default_model"],
                "available": is_available,
                "supports_streaming": config["supports_streaming"],
                "supports_function_calling": config["supports_function_calling"],
            })
        return available

    def is_provider_available(self, provider: str) -> bool:
        """检查提供商是否可用"""
        if provider not in self.PROVIDER_CONFIG:
            return False

        provider_info = self.providers.get(provider)
        if provider in ["ollama", "dashscope"]:
            return provider_info == "available"
        return provider_info is not None

    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: str = "deepseek",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """发送对话请求到指定 provider"""
        # 验证 provider
        if not self.is_provider_available(provider):
            # 尝试找备用 provider
            fallback = await self._find_available_provider(provider)
            if fallback:
                provider = fallback
            else:
                raise LLMError(
                    f"Provider '{provider}' is not available and no fallback found",
                    provider
                )

        # 调用对应 provider
        try:
            if provider == "openai":
                return await self._chat_openai(messages, model, temperature, max_tokens, **kwargs)
            elif provider == "anthropic":
                return await self._chat_anthropic(messages, model, temperature, max_tokens, **kwargs)
            elif provider == "deepseek":
                return await self._chat_deepseek(messages, model, temperature, max_tokens, **kwargs)
            elif provider == "ollama":
                return await self._chat_ollama(messages, model, temperature, **kwargs)
            elif provider == "dashscope":
                return await self._chat_dashscope(messages, model, temperature, **kwargs)
            else:
                raise LLMError(f"Unknown provider: {provider}", provider)
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Chat error: {str(e)}", provider)

    async def _find_available_provider(self, preferred: str) -> Optional[str]:
        """按优先级找可用的 provider"""
        priority = ["deepseek", "openai", "anthropic", "ollama", "dashscope"]

        # 优先尝试非首选的 provider
        for p in priority:
            if p != preferred and self.is_provider_available(p):
                return p
        return None

    async def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        llm = self.providers["openai"]
        model = model or "gpt-4-turbo-preview"
        response = await llm.agenerate([messages])
        return response.generations[0][0].text

    async def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        llm = self.providers["anthropic"]
        model = model or "claude-3-sonnet-20240229"
        response = await llm.agenerate([messages])
        return response.generations[0][0].text

    async def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: Optional[float],
        **kwargs
    ) -> str:
        model = model or settings.OLLAMA_MODEL
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature or 0.7
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

    async def _chat_deepseek(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> str:
        client = self.providers["deepseek"]
        model = model or settings.DEEPSEEK_MODEL
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def _chat_dashscope(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: Optional[float],
        **kwargs
    ) -> str:
        if not settings.DASHSCOPE_API_KEY:
            raise LLMError("DASHSCOPE_API_KEY not configured", "dashscope")

        import dashscope
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        model = model or "qwen-turbo"

        messages_formatted = [{"role": m["role"], "content": m["content"]} for m in messages]

        response = dashscope.Generation.call(
            model=model,
            messages=messages_formatted,
            temperature=temperature,
            **kwargs
        )

        if response.status_code != 200:
            raise LLMError(
                f"DashScope API error: {response.message}",
                "dashscope",
                response.status_code
            )

        return response.output.choices[0].message.content

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        provider: str = "deepseek",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式对话"""
        if not self.is_provider_available(provider):
            fallback = await self._find_available_provider(provider)
            if fallback:
                provider = fallback
            else:
                raise LLMError(f"No available provider for streaming", provider)

        try:
            if provider == "deepseek":
                async for chunk in self._stream_deepseek(messages, model, temperature, **kwargs):
                    yield chunk
            elif provider == "openai":
                async for chunk in self._stream_openai(messages, model, temperature, **kwargs):
                    yield chunk
            elif provider == "ollama":
                async for chunk in self._stream_ollama(messages, model, temperature, **kwargs):
                    yield chunk
            elif provider == "anthropic":
                # Anthropic 不支持真正的流式，通过普通调用模拟
                content = await self._chat_anthropic(messages, model, temperature, None, **kwargs)
                for char in content:
                    yield char
                    await asyncio.sleep(0.01)
            else:
                # 非流式降级
                content = await self.chat(messages, provider, model, temperature, **kwargs)
                for char in content:
                    yield char
                    await asyncio.sleep(0.01)
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"Streaming error: {str(e)}", provider)

    async def _stream_deepseek(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: Optional[float],
        **kwargs
    ) -> AsyncIterator[str]:
        client = self.providers["deepseek"]
        model = model or settings.DEEPSEEK_MODEL

        def _sync_generator():
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=temperature,
                **kwargs
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        # 在线程中运行同步生成器，避免阻塞事件循环
        async for content in AsyncIterableAdapter(_sync_generator):
            yield content

    async def _stream_openai(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: Optional[float],
        **kwargs
    ) -> AsyncIterator[str]:
        llm = self.providers["openai"]
        model = model or "gpt-4-turbo-preview"
        async for chunk in llm.stream(messages):
            yield chunk

    async def _stream_ollama(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str],
        temperature: Optional[float],
        **kwargs
    ) -> AsyncIterator[str]:
        model = model or settings.OLLAMA_MODEL
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True,
                    "options": {"temperature": temperature or 0.7}
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue

    async def count_tokens(self, messages: List[Dict[str, str]], provider: str = "deepseek") -> int:
        """估算 token 数量（简化版）"""
        total_chars = sum(len(m.get("content", "")) for m in messages)
        return total_chars // 4

    async def get_model_info(self, provider: str, model: Optional[str] = None) -> Dict[str, Any]:
        """获取模型信息"""
        config = self.PROVIDER_CONFIG.get(provider, {})
        model = model or config.get("default_model")

        return {
            "provider": provider,
            "model": model,
            "supports_streaming": config.get("supports_streaming", False),
            "supports_function_calling": config.get("supports_function_calling", False),
            "available": self.is_provider_available(provider),
        }


llm_gateway = LLMGateway()
