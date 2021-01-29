import pathlib

import pytest

import pystring_reflow

test_dir = pathlib.Path(__file__).absolute().parent
input_dir = test_dir / "inputs"
output_dir = test_dir / "outputs"

paired_file_paths = [
    (input_dir / (test_file.name), output_dir / (test_file.name))
    for test_file in input_dir.glob("case_*.py")
]


@pytest.mark.parametrize("input_file_path,output_file_path", paired_file_paths)
def test_reflows(input_file_path, output_file_path):
    with open(input_file_path) as input_fp:
        reflowed_text = pystring_reflow.reflow_text(input_fp.read(), cols=80)
    with open(output_file_path) as output_fp:
        expected_output = output_fp.read()
    assert (
        reflowed_text == expected_output
    ), "Expected reflowed text to match example output"
