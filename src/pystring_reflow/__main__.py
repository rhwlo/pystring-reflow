import argparse
from difflib import unified_diff

from . import reflow_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--line-length", type=int, default=80)
    parser.add_argument("--diff", action="store_true")
    parser.add_argument("filename")
    args = parser.parse_args()
    with open(args.filename) as fp:
        contents = fp.read()

    reflowed_text = reflow_text(contents, args.line_length)
    if not args.diff:
        print(reflowed_text)
    else:
        print("\n".join(unified_diff(contents.split("\n"), reflowed_text.split("\n"))))
