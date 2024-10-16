import json

from mirascope.core import BaseDynamicConfig, Messages, bedrock, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


class Librarian(BaseModel):
    history: list[bedrock.BedrockMessageParam] = []
    library: list[Book] = [
        Book(title="The Name of the Wind", author="Patrick Rothfuss"),
        Book(title="Mistborn: The Final Empire", author="Brandon Sanderson"),
    ]

    def _available_books(self) -> str:
        """Returns the list of books available in the library."""
        return json.dumps([book.model_dump() for book in self.library])

    @bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", stream=True)
    @prompt_template(
        """
        SYSTEM: You are a librarian
        MESSAGES: {self.history}
        USER: {query}
        """
    )
    def _stream(self, query: str) -> BaseDynamicConfig:
        return {"tools": [self._available_books]}

    def _step(self, query: str) -> None:
        if query:
            self.history.append(Messages.User(query))
        stream = self._stream(query)
        tools_and_outputs = []
        for chunk, tool in stream:
            if tool:
                print(f"[Calling Tool '{tool._name()}' with args {tool.args}]")
                tools_and_outputs.append((tool, tool.call()))
            else:
                print(chunk.content, end="", flush=True)
        self.history.append(stream.message_param)
        if tools_and_outputs:
            self.history += stream.tool_message_params(tools_and_outputs)
            self._step("")

    def run(self) -> None:
        while True:
            query = input("(User): ")
            if query in ["exit", "quit"]:
                break
            print("(Assistant): ", end="", flush=True)
            self._step(query)
            print()


Librarian().run()