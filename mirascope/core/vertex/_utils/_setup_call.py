"""This module contains the setup_call function, which is used to set up the"""

from collections.abc import Awaitable, Callable
from dataclasses import asdict, is_dataclass
from typing import Any, cast, overload

from vertexai.generative_models import (
    Content,
    GenerationResponse,
    GenerativeModel,
    ToolConfig,
)

from ...base import BaseMessageParam, BaseTool, _utils
from ...base._utils import AsyncCreateFn, CreateFn, get_async_create_fn, get_create_fn
from ...base._utils._protocols import fn_is_async
from ..call_kwargs import VertexCallKwargs
from ..call_params import VertexCallParams
from ..dynamic_config import VertexDynamicConfig
from ..tool import VertexTool
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: GenerativeModel | None,
    fn: Callable[..., Awaitable[VertexDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: VertexDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: VertexCallParams,
    extract: bool = False,
) -> tuple[
    AsyncCreateFn[GenerationResponse, GenerationResponse],
    str | None,
    list[Content],
    list[type[VertexTool]] | None,
    VertexCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: GenerativeModel | None,
    fn: Callable[..., VertexDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: VertexDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: VertexCallParams,
    extract: bool = False,
) -> tuple[
    CreateFn[GenerationResponse, GenerationResponse],
    str | None,
    list[Content],
    list[type[VertexTool]] | None,
    VertexCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: GenerativeModel | None,
    fn: Callable[..., VertexDynamicConfig | Awaitable[VertexDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: VertexDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: VertexCallParams,
    extract: bool = False,
) -> tuple[
    CreateFn[GenerationResponse, GenerationResponse]
    | AsyncCreateFn[GenerationResponse, GenerationResponse],
    str | None,
    list[Content],
    list[type[VertexTool]] | None,
    VertexCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, VertexTool, call_params
    )
    call_kwargs = cast(VertexCallKwargs, base_call_kwargs)
    messages = cast(list[BaseMessageParam | Content], messages)
    messages = convert_message_params(messages)
    if json_mode:
        generation_config = call_kwargs.get("generation_config", {})
        if is_dataclass(generation_config):
            generation_config = asdict(generation_config)
        generation_config["response_mime_type"] = "application/json"
        call_kwargs["generation_config"] = generation_config
        messages[-1]["parts"].append(
            _utils.json_mode_content(tool_types[0] if tool_types else None)
        )
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs.pop("tool_config", None)
        tool_config = ToolConfig(
            function_calling_config=ToolConfig.FunctionCallingConfig(
                mode="any",
                allowed_function_names=[tool_types[0]._name()],
            )
        )
        call_kwargs["tool_config"] = tool_config
    call_kwargs |= {"contents": messages}

    if client is None:
        client = GenerativeModel(model_name=model)

    create = (
        get_async_create_fn(client.generate_content_async)
        if fn_is_async(fn)
        else get_create_fn(client.generate_content)
    )

    return create, prompt_template, messages, tool_types, call_kwargs
