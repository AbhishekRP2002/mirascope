from mirascope.core import Messages, azure


@azure.call("gpt-4o-mini")
def summarize(text: str) -> Messages.Type:
    return Messages.User(f"Summarize this text: {text}")


@azure.call("gpt-4o-mini")
def translate(text: str, language: str) -> Messages.Type:
    return Messages.User(f"Translate this text to {language}: {text}")


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)