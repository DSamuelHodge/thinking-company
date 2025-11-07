# Contract: LLM Provider Interface

**Feature**: 001-restack-gen-cli  
**Date**: November 6, 2025  
**Status**: Draft  
**Related**: FR-005 (Multi-provider LLM support), data-model.md (LLMIntegration)

## Purpose

Defines the abstract interface for LLM provider implementations to ensure consistent multi-provider support with Gemini as the default implementation.

## Provider Interface

All LLM providers MUST implement the following abstract interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class LLMRequest(BaseModel):
    """Standardized request format across providers"""
    messages: List[Dict[str, str]]  # [{"role": "user", "content": "..."}]
    model: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 0.7
    metadata: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    """Standardized response format across providers"""
    content: str
    model: str
    usage: Dict[str, int]  # {"prompt_tokens": X, "completion_tokens": Y}
    metadata: Optional[Dict[str, Any]] = None

class LLMProviderBase(ABC):
    """Abstract base class for all LLM providers"""
    
    @abstractmethod
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """
        Send a chat completion request to the LLM provider.
        
        Args:
            request: Standardized LLM request
            
        Returns:
            Standardized LLM response
            
        Raises:
            LLMError: On provider-specific errors
            RateLimitError: When rate limits are exceeded
            TimeoutError: When request exceeds timeout
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier (e.g., 'gemini', 'openai')"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration (API keys, endpoints)"""
        pass
    
    @abstractmethod
    def estimate_cost(self, request: LLMRequest) -> float:
        """Estimate request cost in USD"""
        pass
```

## Supported Providers

### Phase 1 (MVP)
- **Gemini** (google-generativeai): Default implementation, full support

### Phase 2 (Future)
- **OpenAI** (openai package): Stub implementation with TODO markers
- **Anthropic** (anthropic package): Stub implementation with TODO markers

## Configuration Schema

Each provider configuration in `restack.toml`:

```toml
[llm.providers.gemini]
enabled = true
model = "gemini-1.5-pro"
api_key_env = "GEMINI_API_KEY"
max_tokens = 8192
temperature = 0.7
timeout_ms = 30000

[llm.providers.openai]
enabled = false
model = "gpt-4"
api_key_env = "OPENAI_API_KEY"
# ... similar structure
```

## Error Handling

Providers MUST raise specific exceptions:

```python
class LLMError(Exception):
    """Base exception for LLM provider errors"""
    pass

class RateLimitError(LLMError):
    """Raised when provider rate limits are exceeded"""
    pass

class AuthenticationError(LLMError):
    """Raised when API key is invalid or missing"""
    pass

class ModelNotFoundError(LLMError):
    """Raised when requested model doesn't exist"""
    pass
```

## Provider Registry

The CLI MUST maintain a provider registry:

```python
PROVIDER_REGISTRY: Dict[str, Type[LLMProviderBase]] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,  # Future
    "anthropic": AnthropicProvider,  # Future
}
```

## Integration Pattern

Generated code using LLM providers:

```python
from restack_gen.llm import get_provider, LLMRequest

async def call_llm(prompt: str):
    provider = get_provider("gemini")  # From config
    request = LLMRequest(
        messages=[{"role": "user", "content": prompt}],
        model="gemini-1.5-pro"
    )
    response = await provider.chat(request)
    return response.content
```

## Acceptance Criteria

- [ ] Base interface defined with all abstract methods
- [ ] Gemini provider fully implemented
- [ ] OpenAI/Anthropic stubs with TODO markers
- [ ] Configuration schema validated with Pydantic
- [ ] Error hierarchy defined and raised appropriately
- [ ] Provider registry enables runtime selection
- [ ] Generated code successfully calls providers
- [ ] Tests cover provider switching and fallback

## Non-Requirements

- **Not in scope**: Streaming responses (future enhancement)
- **Not in scope**: Function calling / tool use (Phase 2)
- **Not in scope**: Vision/multimodal inputs (future enhancement)
- **Not in scope**: Fine-tuning or embedding endpoints

## Notes

- Provider selection driven by configuration, not code
- API keys MUST be read from environment variables, never hardcoded
- Timeout and retry logic handled by LLM Router (separate component)
- Cost estimation is best-effort for Phase 1
