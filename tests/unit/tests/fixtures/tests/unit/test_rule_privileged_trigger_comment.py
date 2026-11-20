"""A comment that names `pull_request_target` is not a trigger (task 9.30).

`pat-privileged-trigger` is anchored to the YAML key that enables the trigger, so the warning
comment in `comment_only` is quiet while each of the key forms still raises the WARN.
`pat-ptr-head-checkout` reads its trigger half through the same pattern
(`src/airlock/detectors/ci_surface.py`), so the HIGH still holds for a keyed trigger with a head
checkout and no longer pairs a comment, which declares no base-context run.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from tests.fixtures import Case, context, fired, scan
from tests.fixtures.privileged_trigger_comment import (
    comment_only,
    comment_with_head_checkout,
    key_on_its_own_line,
    keyed_head_checkout,
    list_item,
    on_line_flow_list,
    on_line_scalar,
)

from airlock.model import Finding, Severity

TRIGGER_RULE = "pat-privileged-trigger"
HEAD_RULE = "pat-ptr-head-checkout"
#: The fixture line cap is 90; a longer comment would be skipped, not read, and pass for nothing.
LONG_LINE_RULE = "cfg-long-line"


def findings_for(case: Case, rule_id: str) -> list[Finding]:
    return [finding for finding in scan(context(case)) if finding.rule_id == rule_id]


class TestACommentIsNotATrigger:
    def test_the_warning_comment_is_quiet(self) -> None:
        hits = fired(comment_only())
        assert LONG_LINE_RULE not in hits, "the comment must be short enough to be searched"
        assert TRIGGER_RULE not in hits, hits
        assert HEAD_RULE not in hits, hits

    def test_a_comment_beside_a_head_checkout_is_not_the_high(self) -> None:
        hits = fired(comment_with_head_checkout())
        assert LONG_LINE_RULE not in hits, "the comment must be short enough to be searched"
        assert TRIGGER_RULE not in hits, hits
        assert HEAD_RULE not in hits, hits


class TestEachKeyFormFires:
    @pytest.mark.parametrize(
        ("case_fn", "line"),
        [
            (on_line_scalar, 1),
            (on_line_flow_list, 1),
            (key_on_its_own_line, 2),
            (list_item, 3),
        ],
        ids=["on-line-scalar", "on-line-flow-list", "key-on-its-own-line", "list-item"],
    )
    def test_the_key_form_is_one_warning_on_the_trigger_line(
        self, case_fn: Callable[[], Case], line: int
    ) -> None:
        findings = findings_for(case_fn(), TRIGGER_RULE)
        assert [(f.line, f.severity) for f in findings] == [(line, Severity.WARN)]


class TestTheHighStillPairsAKeyedTrigger:
    def test_a_keyed_trigger_with_a_head_checkout_is_the_high(self) -> None:
        findings = findings_for(keyed_head_checkout(), HEAD_RULE)
        assert len(findings) == 1, findings
        assert findings[0].severity is Severity.HIGH
        assert findings[0].line == 9, "the finding sits on the head ref, not on the trigger"
