import os
import sys
import re
from litellm import completion


# /Users/tumf/Library/Mobile Documents/iCloud~md~obsidian/Documents/Inbox/Untitled 1.md
def search_untitled_files(directory) -> [str]:
    untitled_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            pattern = re.compile(r"^(無題のファイル|Untitled)( \d+)?\.md$")
            if pattern.match(file):
                untitled_files.append(os.path.join(root, file))
    return untitled_files


def generate_title(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    prompt = """
    Generate a title as title of filename in 20 chars or less for the following markdown content.
    """
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": content},
    ]
    response = completion(messages=messages, model="gpt-4o")
    return response.choices[0].message.content


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
