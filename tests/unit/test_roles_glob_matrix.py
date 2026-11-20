"""Glob matrix for `match_glob` (task 9.29).

`match_glob` (`src/airlock/roles.py`) splits the pattern and the path on `/` and lets a `**`
segment consume any number of path segments, zero included, while `*` and `?` stay inside one
segment (`ARCHITECTURE.md` 6.2). `tests/unit/test_roles.py` covers one `**` per pattern; a
roles glob such as `**/.github/workflows/**/*.yml` is decided by the rows below instead: two
`**` groups, adjacent `**/**`, a `**` between two literals that matches zero or many segments,
and a trailing `**` with zero and several segments left.

Every expected value is written down by hand, never computed from `match_glob`, so a change to
the matcher fails a row rather than quietly moving the answer. The rows `test_roles.py` already
has for the root config and the double star are repeated here so this file is a complete record.
"""

from __future__ import annotations

from typing import NamedTuple

import pytest

from airlock.roles import match_glob


class GlobCase(NamedTuple):
    """One row: an id named in the failure message, the pattern, the path, the expected result."""

    case_id: str
    pattern: str
    path: str
    expected: bool


#: The workflow-shaped pattern the issue names: two `**` groups around two literals.
TWO_GROUPS = "**/.github/workflows/**/*.yml"
ADJACENT = "**/**/x.js"
BETWEEN = "src/**/index.ts"
BOTH_ENDS = "**/node_modules/**"

CASES: tuple[GlobCase, ...] = (
    # Repeated from tests/unit/test_roles.py (root config and double star).
    GlobCase("root-config-zero-dirs", "**/postcss.config.*", "postcss.config.mjs", True),
    GlobCase("config-two-dirs-deep", "**/postcss.config.*", "apps/web/postcss.config.js", True),
    GlobCase("double-star-js-at-root", "**/*.js", "a.js", True),
    GlobCase("double-star-js-deep", "**/*.js", "deep/nested/path/file.js", True),
    GlobCase("lone-double-star-one-segment", "**", "a", True),
    GlobCase("trailing-double-star-three-segments", "vendor/**", "vendor/a/b/c.js", True),
    GlobCase("trailing-double-star-wrong-prefix", "vendor/**", "vendored/a.js", False),
    # Two `**` groups in one pattern.
    GlobCase("two-groups-both-zero", TWO_GROUPS, ".github/workflows/ci.yml", True),
    GlobCase("two-groups-both-many", TWO_GROUPS, "repo/sub/.github/workflows/a/b/ci.yml", True),
    GlobCase("two-groups-first-zero-second-many", TWO_GROUPS, ".github/workflows/x/ci.yml", True),
    GlobCase("two-groups-first-many-second-zero", TWO_GROUPS, "a/.github/workflows/ci.yml", True),
    GlobCase("two-groups-wrong-extension", TWO_GROUPS, ".github/workflows/ci.yaml", False),
    GlobCase("two-groups-missing-literal", TWO_GROUPS, ".github/ci.yml", False),
    GlobCase("two-groups-literals-split-apart", TWO_GROUPS, "a/.github/b/workflows/ci.yml", False),
    # Adjacent `**/**`.
    GlobCase("adjacent-groups-zero", ADJACENT, "x.js", True),
    GlobCase("adjacent-groups-many", ADJACENT, "a/b/c/x.js", True),
    GlobCase("adjacent-groups-wrong-name", ADJACENT, "a/b/y.js", False),
    # A `**` between two literal segments.
    GlobCase("between-literals-zero", BETWEEN, "src/index.ts", True),
    GlobCase("between-literals-one", BETWEEN, "src/a/index.ts", True),
    GlobCase("between-literals-many", BETWEEN, "src/a/b/c/index.ts", True),
    GlobCase("between-literals-wrong-tail", BETWEEN, "src/a/index.js", False),
    GlobCase("between-literals-wrong-head", BETWEEN, "lib/src/index.ts", False),
    # A leading and a trailing `**` around one literal, both consuming zero or many.
    GlobCase("both-ends-zero", BOTH_ENDS, "node_modules", True),
    GlobCase("both-ends-many", BOTH_ENDS, "a/b/node_modules/c/d.js", True),
    GlobCase("both-ends-near-miss", BOTH_ENDS, "node_modules_old/d.js", False),
    # A trailing `**` against an empty remainder and against several segments.
    GlobCase("trailing-double-star-zero-segments", "vendor/**", "vendor", True),
    GlobCase("trailing-double-star-one-segment", "vendor/**", "vendor/a.js", True),
)


def test_the_matrix_is_large_enough_and_ids_are_unique() -> None:
    ids = [case.case_id for case in CASES]
    assert len(CASES) >= 12, f"the matrix needs at least twelve rows, has {len(CASES)}"
    assert len(ids) == len(set(ids)), "every row needs its own id"


@pytest.mark.parametrize("case", CASES, ids=[case.case_id for case in CASES])
def test_glob_matrix(case: GlobCase) -> None:
    actual = match_glob(case.pattern, case.path)
    assert actual is case.expected, (
        f"{case.case_id}: match_glob({case.pattern!r}, {case.path!r}) "
        f"returned {actual}, expected {case.expected}"
    )
