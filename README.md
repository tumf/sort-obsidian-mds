# Obsidian document sorter

- find Untitled and rename (or delete if empty)
- use LLM `gpt-4o` when renaming file name.

you should set `OPENAI_API_KEY`.

```shell
$ python main.py
Usage: python main.py <directory>
```

## test

```shell
$ python -m unittest test_main.py
......
----------------------------------------------------------------------
Ran 6 tests in 4.073s

OK
```
