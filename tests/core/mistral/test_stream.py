"""Tests the `mistral.stream` module."""

from mistralai.models.chat_completion import (
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    ChatMessage,
    DeltaMessage,
    FunctionCall,
    ToolCall,
    ToolType,
)
from mistralai.models.common import UsageInfo

from mirascope.core.mistral.call_response import MistralCallResponse
from mirascope.core.mistral.call_response_chunk import MistralCallResponseChunk
from mirascope.core.mistral.stream import MistralStream
from mirascope.core.mistral.tool import MistralTool


def test_mistral_stream() -> None:
    """Tests the `MistralStream` class."""
    assert MistralStream._provider == "mistral"

    class FormatBook(MistralTool):
        """Returns the title and author nicely formatted."""

        title: str
        author: str

        def call(self):
            """Dummy call."""

    tool_call = ToolCall(
        id="id",
        function=FunctionCall(
            name="FormatBook",
            arguments='{"title": "The Name of the Wind", "author": "Patrick Rothfuss"}',
        ),
        type=ToolType.function,
    )
    usage = UsageInfo(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    chunks = [
        ChatCompletionStreamResponse(
            id="id",
            choices=[
                ChatCompletionResponseStreamChoice(
                    delta=DeltaMessage(content="content", tool_calls=None),
                    index=0,
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
        ),
        ChatCompletionStreamResponse(
            id="id",
            choices=[
                ChatCompletionResponseStreamChoice(
                    index=0,
                    delta=DeltaMessage(
                        content=None,
                        tool_calls=[tool_call],
                    ),
                    finish_reason=None,
                )
            ],
            created=0,
            model="mistral-large-latest",
            object="chat.completion.chunk",
            usage=usage,
        ),
    ]

    tool_call = None

    def generator():
        nonlocal tool_call
        for chunk in chunks:
            call_response_chunk = MistralCallResponseChunk(chunk=chunk)
            if tool_calls := call_response_chunk.chunk.choices[0].delta.tool_calls:
                assert tool_calls[0].function
                tool_call = ToolCall(
                    id="id",
                    function=FunctionCall(**tool_calls[0].function.model_dump()),
                    type=ToolType.function,
                )
                yield (
                    call_response_chunk,
                    FormatBook.from_tool_call(tool_call),
                )
            else:
                yield call_response_chunk, None

    stream = MistralStream(
        stream=generator(),
        metadata={},
        tool_types=[FormatBook],
        call_response_type=MistralCallResponse,
        model="mistral-large-latest",
        prompt_template="",
        fn_args={},
        dynamic_config=None,
        messages=[],
        call_params={},
        call_kwargs={},
    )
    assert stream.cost is None
    for _ in stream:
        pass
    assert stream.cost == 1.2e-5
    assert tool_call is not None
    assert stream.message_param == ChatMessage(
        role="assistant", content="content", tool_calls=[tool_call]
    )
