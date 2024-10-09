"""This module contains the setup_call function for Mistral tools."""

import os
from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any, cast, overload

from mistralai import Mistral
from mistralai.models import (
    AssistantMessage,
    ChatCompletionResponse,
    CompletionEvent,
    ResponseFormat,
    SystemMessage,
    ToolChoiceEnum,
    ToolMessage,
    UserMessage,
)

from ...base import BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn, get_async_create_fn, get_create_fn
from ...base._utils._protocols import fn_is_async
from ..call_kwargs import MistralCallKwargs
from ..call_params import MistralCallParams
from ..dynamic_config import MistralDynamicConfig
from ..tool import MistralTool
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: Mistral | None,
    fn: Callable[..., Awaitable[MistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    AsyncCreateFn[ChatCompletionResponse, CompletionEvent],
    str | None,
    list[AssistantMessage | SystemMessage | ToolMessage | UserMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: Mistral | None,
    fn: Callable[..., MistralDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletionResponse, CompletionEvent],
    str | None,
    list[AssistantMessage | SystemMessage | ToolMessage | UserMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: Mistral | None,
    fn: Callable[..., MistralDynamicConfig | Awaitable[MistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams,
    extract: bool,
) -> tuple[
    CreateFn[ChatCompletionResponse, CompletionEvent]
    | AsyncCreateFn[ChatCompletionResponse, CompletionEvent],
    str | None,
    list[AssistantMessage | SystemMessage | ToolMessage | UserMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, MistralTool, call_params
    )
    call_kwargs = cast(MistralCallKwargs, base_call_kwargs)
    messages = cast(
        list[AssistantMessage | SystemMessage | ToolMessage | UserMessage], messages
    )
    messages = convert_message_params(messages)
    if json_mode:
        call_kwargs["response_format"] = ResponseFormat(type="json_object")
        json_mode_content = _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        if messages[-1].role == "user":
            messages[-1].content += json_mode_content
        else:
            messages.append(UserMessage(content=json_mode_content.strip()))
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = cast(ToolChoiceEnum, "any")
    call_kwargs |= {"model": model, "messages": messages}

    if client is None:
        client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY", ""))
    if fn_is_async(fn):
        create_or_stream = get_async_create_fn(
            client.chat.complete_async, client.chat.stream_async
        )
    else:
        create_or_stream = get_create_fn(client.chat.complete, client.chat.stream)
    return create_or_stream, prompt_template, messages, tool_types, call_kwargs
