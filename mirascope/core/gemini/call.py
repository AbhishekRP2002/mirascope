"""The `gemini_call` decorator for functions as LLM calls."""

from google.generativeai.types import ContentDict

from ..base import call_factory
from ..base._stream import BaseStream
from ..base._utils import SetupCall
from ._utils import (
    calculate_cost,
    get_json_output,
    handle_stream,
    handle_stream_async,
    setup_call,
)
from .call_params import GeminiCallParams
from .call_response import GeminiCallResponse
from .call_response_chunk import GeminiCallResponseChunk
from .dynamic_config import GeminiDynamicConfig
from .tool import GeminiTool


class GeminiStream(
    BaseStream[
        GeminiCallResponse,
        GeminiCallResponseChunk,
        ContentDict,
        ContentDict,
        ContentDict,
        GeminiTool,
        GeminiDynamicConfig,
        GeminiCallParams,
    ]
): ...  # pragma: no cover


gemini_call = call_factory(
    TCallResponse=GeminiCallResponse,
    TCallResponseChunk=GeminiCallResponseChunk,
    TDynamicConfig=GeminiDynamicConfig,
    TStream=GeminiStream,
    TMessageParamType=ContentDict,
    TToolType=GeminiTool,
    TCallParams=GeminiCallParams,
    default_call_params=GeminiCallParams(),
    setup_call=setup_call,  # type: ignore
    get_json_output=get_json_output,
    handle_stream=handle_stream,
    handle_stream_async=handle_stream_async,
    calculate_cost=calculate_cost,
)
'''A decorator for calling the Gemini API with a typed function.

This decorator is used to wrap a typed function that calls the Gemini API. It parses
the docstring of the wrapped function as the messages array and templates the input
arguments for the function into each message's template.

Example:

```python
@gemini_call(model="gemini-1.5-pro")
def recommend_book(genre: str):
    """Recommend a {genre} book."""

response = recommend_book("fantasy")
```

Args:
    model: The Gemini model to use in the API call.
    stream: Whether to stream the response from the API call.
    tools: The tools to use in the Gemini API call.
    **call_params: The `GeminiCallParams` call parameters to use in the API call.

Returns:
    The decorator for turning a typed function into an Gemini API call.
'''
