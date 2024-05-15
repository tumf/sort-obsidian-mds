import os
import sys
import re
from litellm import completion
import json


# /Users/tumf/Library/Mobile Documents/iCloud~md~obsidian/Documents/Inbox/Untitled 1.md
def search_untitled_files(directory) -> [str]:
    untitled_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            pattern = re.compile(r"^(無題のファイル|Untitled)( \d+)?\.md$")
            if pattern.match(file):
                untitled_files.append(os.path.join(root, file))
    return untitled_files


tools = [
    {
        "type": "function",
        "function": {
            "name": "register_title",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "title to register",
                    }
                },
                "required": ["title"],
            },
            "description": "Register the title.",
        },
    }
]


def generate_title(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    prompt = """
    Generate a title as title of filename in 20 chars or less for the following markdown content and register it.
    DO NOT USE special chars except for `!@%^+-_` in the title.
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content},
    ]
    response = completion(
        messages=messages,
        model="gpt-4o",
        tools=tools,
        tool_choice="auto",
        temperature=0.5,
    )
    # get tool call
    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    return args["title"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    untitled_files = search_untitled_files(directory)
    for file in untitled_files:
        # remove if file size zero
        if os.path.getsize(file) == 0:
            print(f"Removing {file}")
            os.remove(file)
            continue
        title = generate_title(file)
        # change filename
        new_file_path = os.path.join(os.path.dirname(file), f"{title}.md")
        # do nothing if new_file_path already exists
        if os.path.exists(new_file_path):
            print(f"File {new_file_path} already exists. Skipping.")
            continue
        os.rename(file, new_file_path)
        print(f"Renaming {file} to {new_file_path}")
