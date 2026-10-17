"""AtCoder Sample I/O Generator (cio)

Automatically creates empty input/output sample pairs for AtCoder problems.
Usage:
    cio a 3       # Creates workspace/samples/a/{1_in.txt, 1_out.txt, ..., 3_out.txt}
    cio b         # Defaults to 3 sample pairs for problem b
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    GRAY = "\033[90m"


def color(text: str, *styles: str) -> str:
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return text
    return f"{''.join(styles)}{text}{Style.RESET}"


def find_project_root() -> Path:
    curr = Path.cwd().resolve()
    for p in [curr, *curr.parents]:
        if (p / "pyproject.toml").exists():
            return p
    return curr


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="cio",
        description="Create input/output sample file pairs for AtCoder problem.",
    )
    parser.add_argument(
        "problem",
        help="Problem name or script (e.g. 'a', 'b', 'c', 'a.py').",
    )
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=3,
        help="Number of sample pairs to create (default: 3).",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing sample files with empty files.",
    )

    args = parser.parse_args()

    if args.count < 1:
        print(color("Error: count must be at least 1.", Style.RED, Style.BOLD))
        return 1

    root = find_project_root()
    workspace = root / "workspace"
    stem = Path(args.problem).stem.lower()

    # 1. Ensure solution file workspace/{stem}.py exists
    solution_file = workspace / f"{stem}.py"
    if not solution_file.exists():
        solution_file.parent.mkdir(parents=True, exist_ok=True)
        solution_file.write_text("# AtCoder solution\n", encoding="utf-8")
        rel_sol = str(solution_file.relative_to(root) if solution_file.is_relative_to(root) else solution_file)
        print(color(f"Created solution script: {rel_sol}", Style.GRAY))

    # 2. Target sample directory: workspace/samples/{stem}/
    target_dir = workspace / "samples" / stem
    target_dir.mkdir(parents=True, exist_ok=True)

    created_files: list[str] = []
    skipped_files: list[str] = []

    for i in range(1, args.count + 1):
        in_file = target_dir / f"{i}_in.txt"
        out_file = target_dir / f"{i}_out.txt"

        for f in (in_file, out_file):
            if f.exists() and not args.force:
                skipped_files.append(f.name)
            else:
                f.write_text("", encoding="utf-8")
                created_files.append(f.name)

    rel_dir = str(target_dir.relative_to(root) if target_dir.is_relative_to(root) else target_dir)

    print(color(f"Ready: {rel_dir}/ ({args.count} sample pairs)", Style.BOLD, Style.GREEN))
    if created_files:
        print(f"  {color('Created:', Style.CYAN)} {', '.join(created_files)}")
    if skipped_files:
        print(f"  {color('Kept existing:', Style.GRAY)} {', '.join(skipped_files)} (use --force to overwrite)")

    print(color(f"\nNext: Paste your samples, then run `actest {stem}`", Style.BOLD))
    return 0


if __name__ == "__main__":
    sys.exit(main())
