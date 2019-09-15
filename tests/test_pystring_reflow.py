from typing import List, NamedTuple

import pytest

import pystring_reflow


class Datum(NamedTuple):
    input: str
    expected_output: str


test_data: List[Datum] = [
    Datum(
        """
if something_is_true:
    print(
        f"This is a message that goes on far longer than it should on a single line. But there's more! "
        f"On the next line, there's another f-string."
    )
""",
        """
if something_is_true:
    print(
        f"This is a message that goes on far longer than it should on a single "
        f"line. But there's more! On the next line, there's another f-string."
    )
""",
    ),
    Datum(
        """
    f"This is a multi-line f-string but it has {valid + variable() * interpolation / with.operators} "
    f"at a point that we would otherwise want to break it."
""",
        """
    f"This is a multi-line f-string but it has "
    f"{valid + variable() * interpolation / with.operators} at a point that we "
    f"would otherwise want to break it."
""",
    ),
    Datum(
        """
    f"This string starts out as an f-string and continues on that way past a first "
    f"newline, but after a second, subsequent newline, it's going to turn into a "
    "non-f-string (though it wouldn't need to be escaped to be one)."
""",
        """
    f"This string starts out as an f-string and continues on that way past a "
    f"first newline, but after a second, subsequent newline, it's going to "
    f"turn into a "
    "non-f-string (though it wouldn't need to be escaped to be one)."
""",
    ),
    Datum(
        '''
"""
This is a heredoc. It might get really long, but we shouldn't mess with it. No, seriously.
"""
''',
        '''
"""
This is a heredoc. It might get really long, but we shouldn't mess with it. No, seriously.
"""
''',
    ),
    Datum(
        """
    f"This string is sneakily using double curly braces {{as literal curly braces}} but "
    f"it's fine to break inside of them!"
""",
        """
    f"This string is sneakily using double curly braces {{as literal curly "
    f"braces}} but it's fine to break inside of them!"
""",
    ),
]


@pytest.mark.parametrize("datum", test_data)
def test_reflows(datum):
    reflowed_text = pystring_reflow.reflow_text(datum.input, cols=80)
    assert reflowed_text == datum.expected_output
