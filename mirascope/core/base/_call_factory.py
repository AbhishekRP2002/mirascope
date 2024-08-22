"""The `call_factory` method for generating provider specific call decorators."""

from collections.abc import AsyncIterable, Callable, Iterable
from enum import Enum
from functools import partial
from typing import (
    Annotated,
    Literal,
    NoReturn,
    TypeVar,
    overload,
)

from pydantic import BaseModel

from ._create import create_factory
from ._extract import extract_factory
from ._utils import (
    BaseType,
    GetJsonOutput,
    HandleStream,
    HandleStreamAsync,
    LLMFunctionDecorator,
    SetupCall,
)
from .call_params import BaseCallParams
from .call_response import BaseCallResponse
from .call_response_chunk import BaseCallResponseChunk
from .dynamic_config import BaseDynamicConfig
from .stream import BaseStream, stream_factory
from .structured_stream import structured_stream_factory
from .tool import BaseTool

_BaseCallResponseT = TypeVar("_BaseCallResponseT", bound=BaseCallResponse)
_BaseCallResponseChunkT = TypeVar(
    "_BaseCallResponseChunkT", bound=BaseCallResponseChunk
)
_ResponseModelT = TypeVar(
    "_ResponseModelT", bound=BaseModel | BaseType | Enum | Annotated
)
_ParsedOutputT = TypeVar("_ParsedOutputT")
_BaseCallParamsT = TypeVar("_BaseCallParamsT", bound=BaseCallParams)
_BaseDynamicConfigT = TypeVar("_BaseDynamicConfigT", bound=BaseDynamicConfig)
_BaseStreamT = TypeVar("_BaseStreamT", bound=BaseStream)
_BaseClientT = TypeVar("_BaseClientT", bound=object)
_BaseToolT = TypeVar("_BaseToolT", bound=BaseTool)
_ResponseT = TypeVar("_ResponseT")
_ResponseChunkT = TypeVar("_ResponseChunkT")


def call_factory(
    *,
    TCallResponse: type[_BaseCallResponseT],
    TCallResponseChunk: type[_BaseCallResponseChunkT],
    TDynamicConfig: type[_BaseDynamicConfigT],
    TToolType: type[_BaseToolT],
    TStream: type[_BaseStreamT],
    TCallParams: type[_BaseCallParamsT],
    default_call_params: _BaseCallParamsT,
    setup_call: SetupCall[
        _BaseClientT,
        _BaseDynamicConfigT,
        _BaseCallParamsT,
        _ResponseT,
        _ResponseChunkT,
        _BaseToolT,
    ],
    get_json_output: GetJsonOutput[_BaseCallResponseT | _BaseCallResponseChunkT],
    handle_stream: HandleStream[_ResponseChunkT, _BaseCallResponseChunkT, _BaseToolT],
    handle_stream_async: HandleStreamAsync[
        _ResponseChunkT, _BaseCallResponseChunkT, _BaseToolT
    ],
):
    """A factory method for creating provider-specific call decorators.

    Args:
        TCallResponse: The provider-specific `BaseCallResponse` type.
        TCallResponseChunk: The provider-specific `BaseCallResponseChunk` type.
        TDynamicConfig: The provider-specific `BaseDynamicConfig` type.
        TToolType: The provider-specific `BaseTool` type.
        TStream: The provider-specific `BaseStream` type.
        TCallParams: The provider-specific `BaseCallParams` type.
        default_call_params: The default call parameters to use, which must match the
            `TCallParams` type if provided.
        setup_call: The helper method for setting up a call, which returns the
            configured create function, the prompt template, the list of
            provider-specific messages, the list of provider-specific tool types, and
            the finalized `call_kwargs` with which to make the API call with the create
            function.
        get_json_output: The helper method for getting JSON output from a call response.
        handle_stream: The helper method for converting a provider's original stream
            generator into a generator that returns tuples of `(chunk, tool)` where
            `chunk` and `tool` are provider-specific `BaseCallResponseChunk` and
            `BaseTool` instances, respectively.
        handle_stream_async: The same helper method as `handle_stream` except for
            handling asynchronous streaming.
    """

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> LLMFunctionDecorator[TDynamicConfig, TCallResponse, TCallResponse]: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponse], _ParsedOutputT],
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> LLMFunctionDecorator[TDynamicConfig, _ParsedOutputT, _ParsedOutputT]: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponseChunk], _ParsedOutputT],
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> NoReturn: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: None = None,
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> LLMFunctionDecorator[TDynamicConfig, TStream, TStream]: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponseChunk], _ParsedOutputT],
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> NoReturn: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True] = True,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: None = None,
        output_parser: Callable[[TCallResponse], _ParsedOutputT],
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> NoReturn: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> LLMFunctionDecorator[TDynamicConfig, _ResponseModelT, _ResponseModelT]: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[False] = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[_ResponseModelT], _ParsedOutputT],
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> LLMFunctionDecorator[TDynamicConfig, _ParsedOutputT, _ParsedOutputT]: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True],
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: None = None,
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> LLMFunctionDecorator[
        TDynamicConfig, Iterable[_ResponseModelT], AsyncIterable[_ResponseModelT]
    ]: ...

    @overload
    def base_call(
        model: str,
        *,
        stream: Literal[True],
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT],
        output_parser: Callable[[TCallResponse], _ParsedOutputT]
        | Callable[[TCallResponseChunk], _ParsedOutputT]
        | Callable[[_ResponseModelT], _ParsedOutputT]
        | None,
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> NoReturn: ...

    def base_call(
        model: str,
        *,
        stream: bool = False,
        tools: list[type[BaseTool] | Callable] | None = None,
        response_model: type[_ResponseModelT] | None = None,
        output_parser: Callable[[TCallResponse], _ParsedOutputT]
        | Callable[[TCallResponseChunk], _ParsedOutputT]
        | Callable[[_ResponseModelT], _ParsedOutputT]
        | None = None,
        json_mode: bool = False,
        client: _BaseClientT | None = None,
        call_params: TCallParams | None = None,
    ) -> LLMFunctionDecorator[
        TDynamicConfig,
        TCallResponse
        | _ParsedOutputT
        | TStream
        | _ResponseModelT
        | Iterable[_ResponseModelT],
        TCallResponse
        | _ParsedOutputT
        | TStream
        | _ResponseModelT
        | AsyncIterable[_ResponseModelT],
    ]:
        if stream and output_parser:
            raise ValueError("Cannot use `output_parser` with `stream=True`.")

        if call_params is None:
            call_params = default_call_params

        if response_model:
            if stream:
                return partial(
                    structured_stream_factory(
                        TCallResponse=TCallResponse,
                        TCallResponseChunk=TCallResponseChunk,
                        TStream=TStream,
                        TToolType=TToolType,
                        setup_call=setup_call,
                        get_json_output=get_json_output,
                    ),
                    model=model,
                    response_model=response_model,
                    json_mode=json_mode,
                    client=client,
                    call_params=call_params,
                )  # type: ignore
            else:
                return partial(
                    extract_factory(
                        TCallResponse=TCallResponse,
                        TToolType=TToolType,
                        setup_call=setup_call,
                        get_json_output=get_json_output,
                    ),
                    model=model,
                    response_model=response_model,
                    output_parser=output_parser,
                    json_mode=json_mode,
                    client=client,
                    call_params=call_params,
                )  # type: ignore
        if stream:
            return partial(
                stream_factory(
                    TCallResponse=TCallResponse,
                    TStream=TStream,
                    setup_call=setup_call,
                    handle_stream=handle_stream,
                    handle_stream_async=handle_stream_async,
                ),
                model=model,
                tools=tools,
                json_mode=json_mode,
                client=client,
                call_params=call_params,
            )  # type: ignore
        return partial(
            create_factory(TCallResponse=TCallResponse, setup_call=setup_call),
            model=model,
            tools=tools,
            output_parser=output_parser,
            json_mode=json_mode,
            client=client,
            call_params=call_params,
        )  # type: ignore

    return base_call