from src.actest import parse_sample_text, are_outputs_equal, normalize_output


def test_parse_japanese_headers():
    text = """
    入力例 1
    3 2
    1 2
    2 3
    出力例 1
    Yes

    入力例 2
    2 1
    1 2
    出力例 2
    No
    """
    cases = parse_sample_text(text)
    assert len(cases) == 2
    assert cases[0].name == "Sample 1"
    assert cases[0].input_text == "3 2\n1 2\n2 3\n"
    assert cases[0].expected_output == "Yes\n"

    assert cases[1].name == "Sample 2"
    assert cases[1].input_text == "2 1\n1 2\n"
    assert cases[1].expected_output == "No\n"


def test_parse_english_headers():
    text = """
    Sample Input 1
    10 20
    Sample Output 1
    30
    """
    cases = parse_sample_text(text)
    assert len(cases) == 1
    assert cases[0].name == "Sample 1"
    assert cases[0].input_text == "10 20\n"
    assert cases[0].expected_output == "30\n"


def test_parse_with_copy_button_text():
    text = """
    入力例 1
    Copy
    5
    1 2 3 4 5
    出力例 1
    コピー
    15
    """
    cases = parse_sample_text(text)
    assert len(cases) == 1
    assert cases[0].input_text == "5\n1 2 3 4 5\n"
    assert cases[0].expected_output == "15\n"


def test_parse_simple_divider():
    text = """
    1 2
    ===
    3 4
    ===
    5 6
    """
    cases = parse_sample_text(text)
    assert len(cases) == 3
    assert cases[0].input_text == "1 2\n"
    assert cases[0].expected_output is None
    assert cases[1].input_text == "3 4\n"
    assert cases[2].input_text == "5 6\n"


def test_parse_custom_in_out_headers():
    text = """
    === in 1
    foo
    === out 1
    bar
    === in 2
    hoge
    === out 2
    fuga
    """
    cases = parse_sample_text(text)
    assert len(cases) == 2
    assert cases[0].input_text == "foo\n"
    assert cases[0].expected_output == "bar\n"
    assert cases[1].input_text == "hoge\n"
    assert cases[1].expected_output == "fuga\n"


def test_are_outputs_equal_exact():
    assert are_outputs_equal("Yes\n", "Yes")
    assert are_outputs_equal("  Yes  \n", "  Yes\n\n")
    assert not are_outputs_equal("Yes", "No")


def test_are_outputs_equal_floats():
    assert are_outputs_equal("3.14159265\n", "3.14159266")
    assert not are_outputs_equal("3.14\n", "3.50")


def test_parse_markdown_headings_and_fences():
    text = """
    ### 入力例 1
    ```
    4 2
    1 3
    ```
    ### 出力例 1
    ```
    2
    ```
    """
    cases = parse_sample_text(text)
    assert len(cases) == 1
    assert cases[0].input_text == "4 2\n1 3\n"
    assert cases[0].expected_output == "2\n"


def test_parse_single_file_with_divider(tmp_path):
    f = tmp_path / "1.txt"
    f.write_text("3 2\n1 2\n---\nYes\n", encoding="utf-8")
    from src.actest import parse_single_file_as_one_case
    case = parse_single_file_as_one_case(f, "Sample 1")
    assert case.name == "Sample 1"
    assert case.input_text == "3 2\n1 2\n"
    assert case.expected_output == "Yes\n"


def test_natural_sort():
    from src.actest import natural_sort_key
    from pathlib import Path
    files = [Path("10.txt"), Path("1.txt"), Path("2.txt")]
    files.sort(key=natural_sort_key)
    assert [f.name for f in files] == ["1.txt", "2.txt", "10.txt"]


def test_load_paired_cases_with_separate_in_out_files(tmp_path):
    from src.actest import load_paired_cases_from_files
    in1 = tmp_path / "1_in.txt"
    out1 = tmp_path / "1_out.txt"
    in2 = tmp_path / "2_in.txt"
    out2 = tmp_path / "2_out.txt"

    in1.write_text("3 2\n1 2\n", encoding="utf-8")
    out1.write_text("Yes\n", encoding="utf-8")
    in2.write_text("4 1\n", encoding="utf-8")
    out2.write_text("No\n", encoding="utf-8")

    cases = load_paired_cases_from_files([in1, out1, in2, out2])
    assert cases is not None
    assert len(cases) == 2
    assert cases[0].name == "Sample 1"
    assert cases[0].input_text == "3 2\n1 2\n"
    assert cases[0].expected_output == "Yes\n"
    assert cases[0].source_file == "1_in.txt / 1_out.txt"

    assert cases[1].name == "Sample 2"
    assert cases[1].input_text == "4 1\n"
    assert cases[1].expected_output == "No\n"


def test_load_paired_cases_with_in_num_out_num(tmp_path):
    from src.actest import load_paired_cases_from_files
    in1 = tmp_path / "in1.txt"
    out1 = tmp_path / "out1.txt"

    in1.write_text("hello\n", encoding="utf-8")
    out1.write_text("world\n", encoding="utf-8")

    cases = load_paired_cases_from_files([in1, out1])
    assert cases is not None
    assert len(cases) == 1
    assert cases[0].name == "Sample 1"
    assert cases[0].input_text == "hello\n"
    assert cases[0].expected_output == "world\n"


def test_cio_creates_files(tmp_path, monkeypatch):
    import subprocess
    # Run cio via python module or main
    from src.cio import main
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["cio", "c", "2"])

    ret = main()
    assert ret == 0

    assert (workspace / "c.py").is_file()
    sample_dir = workspace / "samples" / "c"
    assert (sample_dir / "1_in.txt").is_file()
    assert (sample_dir / "1_out.txt").is_file()
    assert (sample_dir / "2_in.txt").is_file()
    assert (sample_dir / "2_out.txt").is_file()




