"""AtCoder Local Sample Runner (actest)

Runs Python solutions against sample test cases with automatic AC/WA/RE verdict.
Supports single-file or multi-file sample layout (e.g. samples/a/1.txt, samples/a/2.txt).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import difflib
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap
import time


# ANSI Color formatting
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    GRAY = "\033[90m"


def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stdout, "isatty"):
        return False
    return sys.stdout.isatty()


USE_COLOR = supports_color()


def color(text: str, *styles: str) -> str:
    if not USE_COLOR or not styles:
        return text
    return f"{''.join(styles)}{text}{Style.RESET}"


@dataclass
class TestCase:
    name: str
    input_text: str
    expected_output: str | None = None
    source_file: str | None = None


# Patterns for recognizing AtCoder sample sections
RE_INPUT_HEADER = re.compile(
    r"^(?:#+\s*)?(?:\*{1,2})?(?:(?:入力例|sample\s*input)\s*(\d+)|===\s*(?:in|input)(?:\s*(\d+))?|---\s*(?:in|input)(?:\s*(\d+))?|\[(?:in|input)(?:\s*(\d+))?\])(?:\*{1,2})?",
    re.IGNORECASE,
)
RE_OUTPUT_HEADER = re.compile(
    r"^(?:#+\s*)?(?:\*{1,2})?(?:(?:出力例|sample\s*output)\s*(\d+)|===\s*(?:out|output)(?:\s*(\d+))?|---\s*(?:out|output)(?:\s*(\d+))?|\[(?:out|output)(?:\s*(\d+))?\])(?:\*{1,2})?",
    re.IGNORECASE,
)
RE_COPY_BUTTON = re.compile(r"^\s*(?:copy|コピー)\s*$", re.IGNORECASE)
RE_CODE_FENCE = re.compile(r"^\s*```")
RE_SIMPLE_DIVIDER = re.compile(r"^\s*(?:={3,}|-{3,})\s*$")

RE_IN_FILENAME = re.compile(
    r"^(?:in[-_]?(\d+)|input[-_]?(\d+)|(\d+)[-_]in|(\d+)[-_]input|(\d+)\.in)$",
    re.IGNORECASE,
)
RE_OUT_FILENAME = re.compile(
    r"^(?:out[-_]?(\d+)|output[-_]?(\d+)|(\d+)[-_]out|(\d+)[-_]output|(\d+)\.out)$",
    re.IGNORECASE,
)



def natural_sort_key(path: Path) -> list[int | str]:
    """Natural sort key so that 1.txt, 2.txt, 10.txt sort in numerical order."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", path.name)]


def parse_sample_text(text: str, default_name_prefix: str = "Sample") -> list[TestCase]:
    """Parse sample input/output text into a list of TestCase objects."""
    lines = text.splitlines()

    cases: dict[str, dict[str, any]] = {}
    current_case_id: str | None = None
    current_section: str | None = None  # "input" or "output"
    auto_id_counter = 1
    has_headers = False

    for raw_line in lines:
        line = raw_line.strip()

        # Check for input header
        m_in = RE_INPUT_HEADER.match(line)
        if m_in:
            has_headers = True
            matched_id = next((g for g in m_in.groups() if g is not None), None)
            cid = matched_id if matched_id else str(auto_id_counter)
            if not matched_id:
                auto_id_counter += 1
            current_case_id = cid
            current_section = "input"
            if cid not in cases:
                cases[cid] = {"name": f"{default_name_prefix} {cid}", "input": [], "output": []}
            continue

        # Check for output header
        m_out = RE_OUTPUT_HEADER.match(line)
        if m_out:
            has_headers = True
            matched_id = next((g for g in m_out.groups() if g is not None), None)
            if matched_id:
                cid = matched_id
            elif current_case_id:
                cid = current_case_id
            else:
                cid = str(auto_id_counter)
                auto_id_counter += 1
            current_case_id = cid
            current_section = "output"
            if cid not in cases:
                cases[cid] = {"name": f"{default_name_prefix} {cid}", "input": [], "output": []}
            continue

        # Skip browser "Copy" button artifacts
        if RE_COPY_BUTTON.match(line):
            continue

        # Skip markdown code fences
        if RE_CODE_FENCE.match(line):
            continue

        # Skip comment lines if outside any section
        if current_section is None and line.startswith("#"):
            continue

        # Accumulate content into current section
        if current_case_id and current_section:
            cases[current_case_id][current_section].append(raw_line)

    if not has_headers:
        # Check for simple divider format (--- or === separating input and output, or multiple inputs)
        divider_cases = _parse_simple_divider(lines, default_name_prefix)
        if divider_cases:
            return divider_cases

        # Whole text as single case with no output
        cleaned = text.strip()
        if cleaned:
            return [TestCase(name=f"{default_name_prefix} 1", input_text=cleaned + "\n")]
        return []

    result: list[TestCase] = []
    for cid, data in cases.items():
        in_raw = "\n".join(data["input"])
        in_dedented = textwrap.dedent(in_raw).strip()
        in_str = (in_dedented + "\n") if in_dedented else ""

        out_str: str | None = None
        if data["output"]:
            out_raw = "\n".join(data["output"])
            out_dedented = textwrap.dedent(out_raw).strip()
            out_str = (out_dedented + "\n") if out_dedented else ""

        result.append(TestCase(name=data["name"], input_text=in_str, expected_output=out_str))

    return result


def _parse_simple_divider(lines: list[str], prefix: str = "Sample") -> list[TestCase]:
    """Parse text using simple dividers like '===' or '---'."""
    blocks: list[list[str]] = []
    current_block: list[str] = []

    for raw_line in lines:
        if RE_SIMPLE_DIVIDER.match(raw_line):
            if current_block:
                blocks.append(current_block)
                current_block = []
        else:
            current_block.append(raw_line)
    if current_block:
        blocks.append(current_block)

    non_empty_blocks = ["\n".join(b).strip() for b in blocks if "\n".join(b).strip()]

    # If exactly 2 blocks separated by divider, treat block 0 as Input and block 1 as Output!
    if len(non_empty_blocks) == 2:
        return [
            TestCase(
                name=f"{prefix} 1",
                input_text=non_empty_blocks[0] + "\n",
                expected_output=non_empty_blocks[1] + "\n",
            )
        ]

    if len(non_empty_blocks) <= 1:
        return []

    return [
        TestCase(name=f"{prefix} {i + 1}", input_text=b + "\n")
        for i, b in enumerate(non_empty_blocks)
    ]


def parse_single_file_as_one_case(file_path: Path, case_name: str) -> TestCase:
    """Parse a single file representing one test case (e.g. 1.txt)."""
    text = file_path.read_text(encoding="utf-8")

    # If it contains explicit headers ("入力例" / "出力例" etc.)
    cases = parse_sample_text(text, default_name_prefix=case_name)
    if cases:
        # Return first parsed case with the assigned case_name
        case = cases[0]
        case.name = case_name
        case.source_file = file_path.name
        return case

    # Check for simple divider (--- or ===) dividing input and expected output
    lines = text.splitlines()
    div_idx = next((i for i, l in enumerate(lines) if RE_SIMPLE_DIVIDER.match(l)), None)
    if div_idx is not None:
        in_part = textwrap.dedent("\n".join(lines[:div_idx])).strip() + "\n"
        out_part = textwrap.dedent("\n".join(lines[div_idx + 1 :])).strip() + "\n"
        return TestCase(
            name=case_name,
            input_text=in_part,
            expected_output=out_part,
            source_file=file_path.name,
        )

    # Check if a sibling output file exists (e.g. 1.in -> 1.out, in1.txt -> out1.txt)
    parent = file_path.parent
    stem = file_path.stem
    out_candidates = [
        parent / f"{stem}.out",
        parent / f"{stem}_out.txt",
        parent / f"{stem.replace('in', 'out')}.txt" if "in" in stem else None,
    ]
    for oc in out_candidates:
        if oc and oc.is_file():
            out_text = oc.read_text(encoding="utf-8").strip() + "\n"
            return TestCase(
                name=case_name,
                input_text=text.strip() + "\n",
                expected_output=out_text,
                source_file=file_path.name,
            )

    return TestCase(
        name=case_name,
        input_text=text.strip() + "\n",
        expected_output=None,
        source_file=file_path.name,
    )


def extract_pure_text(text: str, section_type: str = "input") -> str:
    """Extract pure input or output text, safely removing headers if present."""
    lines = text.splitlines()
    header_re = RE_INPUT_HEADER if section_type == "input" else RE_OUTPUT_HEADER
    other_re = RE_OUTPUT_HEADER if section_type == "input" else RE_INPUT_HEADER

    has_header = any(header_re.match(l.strip()) for l in lines)
    if not has_header:
        # No header: just strip code fences and copy button artifacts
        cleaned = [l for l in lines if not RE_CODE_FENCE.match(l) and not RE_COPY_BUTTON.match(l)]
        result = textwrap.dedent("\n".join(cleaned)).strip()
        return (result + "\n") if result else ""

    # If header exists, extract only the relevant section
    cleaned: list[str] = []
    in_section = False
    for l in lines:
        if header_re.match(l.strip()):
            in_section = True
            continue
        if other_re.match(l.strip()):
            in_section = False
            continue
        if in_section:
            if not RE_CODE_FENCE.match(l) and not RE_COPY_BUTTON.match(l):
                cleaned.append(l)

    result = textwrap.dedent("\n".join(cleaned)).strip()
    return (result + "\n") if result else ""


def extract_case_id_from_filename(filename: str, pattern: re.Pattern) -> str | None:
    """Extract case identifier from filename (e.g. 1_in.txt -> '1', in2.txt -> '2', 1.in -> '1')."""
    stem = Path(filename).stem
    m = pattern.match(stem) or pattern.match(filename)
    if m:
        for g in m.groups():
            if g is not None:
                return g
    return None


def load_paired_cases_from_files(files: list[Path]) -> list[TestCase] | None:
    """Detect and pair separate input and output files (e.g. 1_in.txt and 1_out.txt)."""
    in_map: dict[str, Path] = {}
    out_map: dict[str, Path] = {}

    for f in files:
        in_id = extract_case_id_from_filename(f.name, RE_IN_FILENAME)
        if in_id:
            in_map[in_id] = f
            continue
        out_id = extract_case_id_from_filename(f.name, RE_OUT_FILENAME)
        if out_id:
            out_map[out_id] = f

    if not in_map:
        return None

    sorted_ids = sorted(in_map.keys(), key=lambda s: int(s) if s.isdigit() else s)
    cases: list[TestCase] = []

    for cid in sorted_ids:
        in_file = in_map[cid]
        out_file = out_map.get(cid)

        in_text = extract_pure_text(in_file.read_text(encoding="utf-8"), section_type="input")
        out_text = extract_pure_text(out_file.read_text(encoding="utf-8"), section_type="output") if out_file else None

        source_disp = f"{in_file.name} / {out_file.name}" if out_file else in_file.name
        cases.append(
            TestCase(
                name=f"Sample {cid}",
                input_text=in_text,
                expected_output=out_text,
                source_file=source_disp,
            )
        )

    return cases



def find_project_root() -> Path:
    """Find the root directory containing pyproject.toml."""
    curr = Path.cwd().resolve()
    for p in [curr, *curr.parents]:
        if (p / "pyproject.toml").exists():
            return p
    return curr


def resolve_target_file(target_arg: str | None) -> Path:
    """Resolve the Python solution file to test."""
    root = find_project_root()
    workspace = root / "workspace"

    if target_arg:
        p = Path(target_arg)
        if p.is_file():
            return p.resolve()

        candidates = [
            Path.cwd() / target_arg,
            Path.cwd() / f"{target_arg}.py",
            workspace / target_arg,
            workspace / f"{target_arg}.py",
            root / target_arg,
            root / f"{target_arg}.py",
        ]
        for c in candidates:
            if c.is_file():
                return c.resolve()

        raise FileNotFoundError(f"Could not find Python script for '{target_arg}'")

    # Pick the most recently modified .py in workspace or cwd
    search_dirs = [workspace, Path.cwd()]
    candidates: list[Path] = []
    for d in search_dirs:
        if d.is_dir():
            for f in d.glob("*.py"):
                if f.name not in ("__init__.py", "actest.py"):
                    candidates.append(f)

    if not candidates:
        raise FileNotFoundError("No Python script found in workspace or current directory.")

    candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return candidates[0].resolve()


SAMPLE_IN_TEMPLATE = """# ここに入力例 {num} を貼り付け（見出し不要、入力値のみでOK）
"""

SAMPLE_OUT_TEMPLATE = """# ここに出力例 {num} を貼り付け（見出し不要、出力値のみでOK）
"""


def load_test_cases(
    target_file: Path,
    sample_arg: str | None,
    root_dir: Path,
) -> tuple[str, list[TestCase]]:
    """Load test cases from directory (e.g. samples/a/1_in.txt, 1_out.txt) or single file."""
    stem = target_file.stem
    workspace = root_dir / "workspace"

    # Explicit argument
    if sample_arg:
        sp = Path(sample_arg).resolve()
        if sp.is_dir():
            files = sorted([f for f in sp.iterdir() if f.is_file() and not f.name.startswith(".")], key=natural_sort_key)
            paired = load_paired_cases_from_files(files)
            if paired:
                return str(sp.relative_to(root_dir) if sp.is_relative_to(root_dir) else sp), paired
            cases = [parse_single_file_as_one_case(f, f"Sample {f.stem}") for f in files]
            return str(sp.relative_to(root_dir) if sp.is_relative_to(root_dir) else sp), cases
        if sp.is_file():
            content = sp.read_text(encoding="utf-8")
            cases = parse_sample_text(content)
            return str(sp.relative_to(root_dir) if sp.is_relative_to(root_dir) else sp), cases
        raise FileNotFoundError(f"Sample path not found: {sample_arg}")

    # Case 1: Directory for problem (e.g. workspace/samples/a/ or samples/a/)
    dir_candidates = [
        workspace / "samples" / stem,
        Path.cwd() / "samples" / stem,
        workspace / stem,
    ]
    for d in dir_candidates:
        if d.is_dir():
            files = sorted(
                [f for f in d.iterdir() if f.is_file() and not f.name.startswith(".")],
                key=natural_sort_key,
            )
            if files:
                # First try pairing separate input/output files (e.g. 1_in.txt & 1_out.txt, in1.txt & out1.txt)
                paired = load_paired_cases_from_files(files)
                if paired:
                    disp = str(d.relative_to(root_dir) if d.is_relative_to(root_dir) else d)
                    return disp, paired

                # Fallback: each file is a single case with both input and output
                cases = [parse_single_file_as_one_case(f, f"Sample {f.stem}") for f in files]
                disp = str(d.relative_to(root_dir) if d.is_relative_to(root_dir) else d)
                return disp, cases

    # Case 2: Multi-file with prefixes (e.g. workspace/samples/a_1_in.txt, a_1_out.txt)
    search_dirs = [workspace / "samples", Path.cwd() / "samples", workspace]
    for parent in search_dirs:
        if parent.is_dir():
            prefixed = sorted(
                [
                    f
                    for f in parent.glob(f"{stem}_*.*")
                    if f.is_file()
                ]
                + [
                    f
                    for f in parent.glob(f"{stem}-*.*")
                    if f.is_file()
                ],
                key=natural_sort_key,
            )
            if prefixed:
                paired = load_paired_cases_from_files(prefixed)
                if paired:
                    disp = str(parent.relative_to(root_dir) if parent.is_relative_to(root_dir) else parent) + f"/{stem}_*"
                    return disp, paired
                cases = [parse_single_file_as_one_case(f, f"Sample {f.stem.replace(stem, '').strip('_-')}") for f in prefixed]
                disp = str(parent.relative_to(root_dir) if parent.is_relative_to(root_dir) else parent) + f"/{stem}_*.txt"
                return disp, cases

    # Case 3: Single file (e.g. workspace/samples/a.txt)
    single_candidates = [
        workspace / "samples" / f"{stem}.txt",
        Path.cwd() / "samples" / f"{stem}.txt",
        workspace / f"{stem}.txt",
        workspace / "samples" / f"{stem}.in",
    ]
    for sf in single_candidates:
        if sf.is_file():
            cases = parse_sample_text(sf.read_text(encoding="utf-8"))
            disp = str(sf.relative_to(root_dir) if sf.is_relative_to(root_dir) else sf)
            return disp, cases

    # Case 4: Not found -> Create separate input/output files (1_in.txt, 1_out.txt, etc.)
    target_dir = workspace / "samples" / stem
    target_dir.mkdir(parents=True, exist_ok=True)
    created_names: list[str] = []
    for i in (1, 2, 3):
        in_file = target_dir / f"{i}_in.txt"
        out_file = target_dir / f"{i}_out.txt"
        in_file.write_text(SAMPLE_IN_TEMPLATE.format(num=i), encoding="utf-8")
        out_file.write_text(SAMPLE_OUT_TEMPLATE.format(num=i), encoding="utf-8")
        created_names.extend([in_file.name, out_file.name])

    disp = str(target_dir.relative_to(root_dir) if target_dir.is_relative_to(root_dir) else target_dir)
    print(color(f"Created sample directory: {disp}/", Style.GREEN, Style.BOLD))
    print(color(f"  Files: {', '.join(created_names)}", Style.CYAN))
    print(color("Paste inputs into *_in.txt and outputs into *_out.txt, then run actest again.", Style.CYAN))
    return disp, []



def normalize_output(text: str) -> list[str]:
    """Normalize output by trimming trailing whitespace from lines and stripping empty lines at ends."""
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[0] == "":
        lines.pop(0)
    return lines


def are_outputs_equal(actual: str, expected: str, float_tol: float = 1e-6) -> bool:
    """Compare outputs line by line with float tolerance fallback."""
    act_lines = normalize_output(actual)
    exp_lines = normalize_output(expected)

    if len(act_lines) != len(exp_lines):
        return False

    for a_line, e_line in zip(act_lines, exp_lines):
        if a_line == e_line:
            continue
        # Check float token equality
        a_tokens = a_line.split()
        e_tokens = e_line.split()
        if len(a_tokens) != len(e_tokens):
            return False
        tokens_match = True
        for a_tok, e_tok in zip(a_tokens, e_tokens):
            if a_tok == e_tok:
                continue
            try:
                a_val = float(a_tok)
                e_val = float(e_tok)
                if not math.isclose(a_val, e_val, rel_tol=float_tol, abs_tol=float_tol):
                    tokens_match = False
                    break
            except ValueError:
                tokens_match = False
                break
        if not tokens_match:
            return False

    return True


@dataclass
class RunResult:
    case: TestCase
    status: str  # "AC", "WA", "RE"
    actual_output: str
    error_output: str
    duration_ms: float


def run_test_case(
    target_file: Path,
    case: TestCase,
    root_dir: Path,
) -> RunResult:
    """Execute target script against one test case without timeout."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir) + os.pathsep + str(target_file.parent) + os.pathsep + env.get("PYTHONPATH", "")

    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(target_file)],
        input=case.input_text,
        capture_output=True,
        text=True,
        cwd=str(target_file.parent),
        env=env,
    )
    duration_ms = (time.perf_counter() - start) * 1000

    if proc.returncode != 0:
        return RunResult(
            case=case,
            status="RE",
            actual_output=proc.stdout,
            error_output=proc.stderr,
            duration_ms=duration_ms,
        )

    if case.expected_output is None:
        # If no expected output is provided, mark as WA with guidance
        status = "WA"
    elif are_outputs_equal(proc.stdout, case.expected_output):
        status = "AC"
    else:
        status = "WA"

    return RunResult(
        case=case,
        status=status,
        actual_output=proc.stdout,
        error_output=proc.stderr,
        duration_ms=duration_ms,
    )


def print_diff(expected: str, actual: str) -> None:
    exp_lines = normalize_output(expected)
    act_lines = normalize_output(actual)
    diff = list(
        difflib.unified_diff(
            [l + "\n" for l in exp_lines],
            [l + "\n" for l in act_lines],
            fromfile="Expected",
            tofile="Actual",
            lineterm="",
        )
    )
    if diff:
        print(color("Diff:", Style.BOLD))
        for line in diff:
            if line.startswith("+"):
                print(color(line, Style.GREEN))
            elif line.startswith("-"):
                print(color(line, Style.RED))
            elif line.startswith("@@"):
                print(color(line, Style.CYAN))
            else:
                print(f"  {line}")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="actest",
        description="Run AtCoder solution against sample test cases (AC / WA / RE).",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Target script or problem name (e.g. 'a', 'a.py'). Defaults to latest modified script.",
    )
    parser.add_argument(
        "-s",
        "--sample",
        dest="sample",
        default=None,
        help="Explicit path to sample file or directory.",
    )
    parser.add_argument(
        "--case",
        type=str,
        default=None,
        help="Only run specific case (e.g. --case 1).",
    )
    parser.add_argument(
        "-c",
        "--clip",
        action="store_true",
        help="Run against sample text directly from clipboard.",
    )

    args = parser.parse_args()

    try:
        target_file = resolve_target_file(args.target)
    except FileNotFoundError as err:
        print(color(f"Error: {err}", Style.RED, Style.BOLD))
        return 1

    root_dir = find_project_root()

    if args.clip:
        try:
            clip_text = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True).stdout
        except Exception as e:
            print(color(f"Failed to read clipboard: {e}", Style.RED))
            return 1
        sample_disp = "<clipboard>"
        test_cases = parse_sample_text(clip_text)
    else:
        sample_disp, test_cases = load_test_cases(target_file, args.sample, root_dir)
        if not test_cases:
            return 0

    if args.case:
        filtered = [c for c in test_cases if args.case in c.name or c.name.endswith(f" {args.case}")]
        if not filtered:
            print(color(f"No case matching '{args.case}' found. Available cases: {', '.join(c.name for c in test_cases)}", Style.YELLOW))
            return 1
        test_cases = filtered

    rel_target = str(target_file.relative_to(root_dir) if target_file.is_relative_to(root_dir) else target_file)

    divider = "=" * 60
    sub_divider = "-" * 60
    print(color(divider, Style.DIM))
    print(f" {color('Target:', Style.BOLD)}  {color(rel_target, Style.CYAN)}")
    print(f" {color('Sample:', Style.BOLD)}  {color(sample_disp, Style.CYAN)} ({len(test_cases)} cases)")
    print(color(divider, Style.DIM))

    results: list[RunResult] = []
    skipped_count = 0

    for case in test_cases:
        if not case.input_text.strip() and not (case.expected_output or "").strip():
            file_note = f" [{case.source_file}]" if case.source_file else ""
            print(f"\n{color('[ SKIP ]', Style.YELLOW)} {color(case.name + file_note, Style.DIM)} {color('(Empty file: paste sample data)', Style.GRAY)}")
            skipped_count += 1
            continue

        res = run_test_case(target_file, case, root_dir)
        results.append(res)

        # Status badge (AC / WA / RE only)
        if res.status == "AC":
            badge = color("[ AC ]", Style.BOLD, Style.GREEN)
        elif res.status == "WA":
            badge = color("[ WA ]", Style.BOLD, Style.RED)
        else:
            badge = color("[ RE ]", Style.BOLD, Style.MAGENTA)

        file_note = f" [{case.source_file}]" if case.source_file else ""
        print(f"\n{badge} {color(case.name + file_note, Style.BOLD)} {color(f'({res.duration_ms:.0f} ms)', Style.GRAY)}")


        # If WA, show input, expected, actual, and diff
        if res.status == "WA":
            print(color(sub_divider, Style.DIM))
            print(color("Input:", Style.BOLD))
            print(case.input_text.rstrip())
            print(color("Expected:", Style.BOLD, Style.GREEN))
            if case.expected_output is not None:
                print(case.expected_output.rstrip())
            else:
                print(color("(No expected output provided in sample file)", Style.YELLOW))
            print(color("Actual:", Style.BOLD, Style.RED))
            print(res.actual_output.rstrip())
            if case.expected_output:
                print_diff(case.expected_output, res.actual_output)
            print(color(sub_divider, Style.DIM))

        # If RE, show input and stderr
        elif res.status == "RE":
            print(color(sub_divider, Style.DIM))
            print(color("Input:", Style.BOLD))
            print(case.input_text.rstrip())
            print(color("Error (stderr):", Style.BOLD, Style.MAGENTA))
            print(res.error_output.rstrip())
            print(color(sub_divider, Style.DIM))

    # Summary
    print(color(divider, Style.DIM))
    ac_count = sum(1 for r in results if r.status == "AC")
    wa_count = sum(1 for r in results if r.status == "WA")
    re_count = sum(1 for r in results if r.status == "RE")
    total = len(results)
    total_time = sum(r.duration_ms for r in results)

    if total == 0:
        print(f" Result: {color('No test cases run (all sample files are empty)', Style.YELLOW)}")
        print(color(" Please paste inputs into *_in.txt and outputs into *_out.txt.", Style.CYAN))
    elif ac_count == total:
        summary_badge = color(f"All {total} cases AC!", Style.BOLD, Style.GREEN)
        print(f" Result: {summary_badge} {color(f'(Total: {total_time:.0f} ms)', Style.GRAY)}")
    else:
        parts = [f"{ac_count}/{total} AC"]
        if wa_count:
            parts.append(f"{wa_count} WA")
        if re_count:
            parts.append(f"{re_count} RE")
        summary_badge = color(", ".join(parts), Style.BOLD, Style.RED)
        print(f" Result: {summary_badge} {color(f'(Total: {total_time:.0f} ms)', Style.GRAY)}")

    print(color(divider, Style.DIM))


    return 0 if (wa_count == 0 and re_count == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
