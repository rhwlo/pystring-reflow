import ast
import itertools
import re
import textwrap
from io import BytesIO, StringIO
from typing import Dict, Generator, Iterator, List, NamedTuple, Tuple


class DelimiterPair(NamedTuple):
    open: str
    close: str


DELIMITERS: List[DelimiterPair] = [
    DelimiterPair('f"', '"'),
    DelimiterPair("f'", "'"),
    DelimiterPair('"', '"'),
    DelimiterPair("'", "'"),
]

WORDSEP_RE = textwrap.TextWrapper.wordsep_simple_re
UNBREAKABLE_WORD_RE = re.compile(
    r"((?<!\{)\{(?:[^{}]*)\}(?!=\})|(?:\{\{|\}\}|[^\t\n\x0b\x0c\r\ ])+)"
)


def strip_delimiters(text: str, delimiters: DelimiterPair) -> str:
    if text.startswith(delimiters.open) and text.endswith(delimiters.close):
        return text[len(delimiters.open) : -(len(delimiters.close))]
    raise ValueError(
        f"String {text} does not start with {delimiters.open} and end with " f"{delimiters.close}"
    )


def split_into_lines(
    text: str, line_length: int, indent: str, delimiters: DelimiterPair
) -> List[str]:
    effective_length = line_length - len(indent) - len(delimiters.open) - len(delimiters.close)
    lines = []
    cur_offset = 0
    # If we're using an f-string, then we need to avoid breaking text inside of a {}
    # interpolation:
    if delimiters.open.startswith("f"):
        break_indices = [match.span()[0] for match in UNBREAKABLE_WORD_RE.finditer(text)]
    else:
        # If we're not using an f-string, then we can just break on word separators
        break_indices = [match.span()[1] for match in WORDSEP_RE.finditer(text)]
    while "".join(lines) != text:
        # If the remaining text is short enough, we're already done!
        if len(text[cur_offset:]) <= effective_length:
            lines.append(text[cur_offset:])
            break

        # Otherwise, what's the largest break index that's on this line?
        try:
            break_index = max(
                b_i
                for b_i in break_indices
                if cur_offset < b_i and cur_offset + effective_length >= b_i
            )
        except ValueError:
            # a ValueError from max() means that no break index exists on this line; in that case,
            # we should take the next available one.
            break_index = min(b_i for b_i in break_indices if cur_offset < b_i)
        new_line = text[cur_offset:break_index]
        lines.append(new_line)
        cur_offset = break_index
    return lines


def is_compatible_delimiter(open_del_a, open_del_b):
    return open_del_a == open_del_b


def matches_group(group, match):
    *_, final_match = group
    return (
        final_match.span()[1] + 1 == match.span()[0]
        and final_match.group(1) == match.group(1)
        and is_compatible_delimiter(final_match.group(2), match.group(2))
    )


def reflow_text(text: str, cols: int) -> str:
    replacements: Dict[Tuple[int, int], str] = {}

    for delimiter in DELIMITERS:
        line_regex = re.compile(f"^( *)({delimiter.open})(.+)({delimiter.close})+$", re.MULTILINE)
        matches = line_regex.finditer(text)
        grouped_matches = []
        for match in matches:
            if grouped_matches and matches_group(grouped_matches[-1], match):
                grouped_matches[-1].append(match)
            else:
                grouped_matches.append([match])
        for grouped_match in grouped_matches:
            indent, *_ = grouped_match[0].groups()
            start_span, *_ = grouped_match[0].span()
            *_, end_span = grouped_match[-1].span()
            if (start_span, end_span) in replacements.keys():
                continue
            complete_string = "".join(match.group(3) for match in grouped_match)
            lines = split_into_lines(
                complete_string, line_length=cols, indent=indent, delimiters=delimiter
            )
            replacement_text = "\n".join(
                f"{indent}{delimiter.open}{line}{delimiter.close}" for line in lines
            )
            replacements[(start_span, end_span)] = replacement_text

    output_text = ""
    cur_index = 0
    for (start_index, end_index) in sorted(replacements.keys()):
        output_text += text[cur_index:start_index]
        output_text += replacements[(start_index, end_index)]
        cur_index = end_index
    output_text += text[cur_index:]
    return output_text
