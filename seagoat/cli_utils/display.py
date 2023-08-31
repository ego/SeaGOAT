# pylint: disable=import-outside-toplevel
import math
from functools import cache
from typing import Optional

import click


@cache
def get_highlighted_lines(file_name: str):
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import get_lexer_for_filename
    from pygments.lexers.javascript import JavascriptLexer
    from pygments.lexers.javascript import TypeScriptLexer

    with open(file_name, "r", encoding="utf-8") as source_code_file:
        code = source_code_file.read()

    if file_name.endswith(".md"):
        return code.splitlines()

    if file_name.endswith(".jsx"):
        lexer = JavascriptLexer()
    elif file_name.endswith(".tsx"):
        lexer = TypeScriptLexer()
    else:
        lexer = get_lexer_for_filename(file_name)

    result = highlight(code, lexer, TerminalFormatter())

    return result.splitlines()


def print_result_line(result, line, color_enabled):
    if color_enabled:
        highlighted_lines = get_highlighted_lines(str(result["fullPath"]))
        click.echo(
            f"{result['path']}:{click.style(str(line), bold=True)}:{highlighted_lines[line - 1]}",
            color=True,
        )
    else:
        for line_content in result["lines"]:
            if line_content["line"] == line:
                click.echo(f"{result['path']}:{line}:{line_content['lineText']}")
                break


def iterate_result_lines(results, max_results: Optional[int]):
    if max_results == 0:
        return

    lines_left_to_print = max_results if max_results is not None else math.inf

    for result in results:
        if lines_left_to_print <= 0:
            return

        for line in result.get("lines", []):
            if "result" in line["resultTypes"]:
                if lines_left_to_print <= 0:
                    return

            yield result, line

            if "result" in line["resultTypes"]:
                if max_results is not None:
                    lines_left_to_print -= 1
