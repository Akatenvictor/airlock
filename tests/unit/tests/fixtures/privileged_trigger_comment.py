"""`pat-privileged-trigger` reads the trigger key, not the word (task 9.30).

The pattern used to be `\\bpull_request_target\\b`, so a YAML comment such as "never use
pull_request_target here" fired the WARN although the workflow declares no such trigger. It is now
anchored to the three ways a workflow enables it: `on: pull_request_target` (or a flow list on the
`on:` line), the key on its own line under `on:`, and a list item under `on:`.

Each builder returns one workflow under `.github/workflows/`, so it resolves to the `workflow` role
the rule reads. The trigger and the head ref are assembled at call time, as in `ci_surface.py`, so
no committed file holds the whole shape (`AGENTS.md` 4). None of these is a rule's named fixture, so
they are not in a `BUILDERS` map: the orphan check would report a builder no rule asks for.
"""

from __future__ import annotations

from . import Case, File, assemble

WORKFLOW_PATH = ".github/workflows/triage.yml"

TRIGGER = assemble("pull_request_", "target")
HEAD_REF = assemble("ref: ${{ github.event.pull", "_request.head.sha }}")
CHECKOUT = assemble("uses: actions/checkout@", "v4")

#: The steps that turn a privileged trigger into the HIGH: a checkout told to use the head ref.
HEAD_CHECKOUT_STEPS = (
    "jobs:",
    "  build:",
    "    runs-on: ubuntu-latest",
    "    steps:",
    f"      - {CHECKOUT}",
    "        with:",
    f"          {HEAD_REF}",
)


def _workflow(*lines: str) -> Case:
    return Case(files=(File(WORKFLOW_PATH, text="\n".join(lines) + "\n"),))


def comment_only() -> Case:
    """The warning comment from the issue, above an ordinary `pull_request` trigger."""
    return _workflow(
        f"# never use {TRIGGER} here: this job checks out contributor code",
        "on:",
        "  pull_request:",
        "    types: [opened, synchronize]",
        "jobs:",
        "  test:",
        "    runs-on: ubuntu-latest",
        "    steps: []",
    )


def comment_with_head_checkout() -> Case:
    """The comment, a `pull_request` trigger and a head checkout: reviewed code, no base context."""
    return _workflow(
        f"# {TRIGGER} plus a head checkout is how this leaks",
        "on:",
        "  pull_request:",
        *HEAD_CHECKOUT_STEPS,
    )


def on_line_scalar() -> Case:
    """`on: pull_request_target`, the trigger as the whole value of `on:`. Line 1."""
    return _workflow(f"on: {TRIGGER}", "jobs:", "  label:", "    steps: []")


def on_line_flow_list() -> Case:
    """`on: [push, pull_request_target]`, the trigger in a flow list on the `on:` line. Line 1."""
    return _workflow(f"on: [push, {TRIGGER}]", "jobs:", "  label:", "    steps: []")


def key_on_its_own_line() -> Case:
    """The trigger as a mapping key under `on:`, with its own settings below it. Line 2."""
    return _workflow(
        "on:",
        f"  {TRIGGER}:",
        "    types: [closed]",
        "jobs:",
        "  label:",
        "    steps: []",
    )


def list_item() -> Case:
    """The trigger as a block list item under `on:`. Line 3."""
    return _workflow("on:", "  - push", f"  - {TRIGGER}", "jobs:", "  label:", "    steps: []")


def keyed_head_checkout() -> Case:
    """The keyed trigger with a checkout of the head ref: the shape the HIGH exists for."""
    return _workflow("on:", f"  {TRIGGER}:", *HEAD_CHECKOUT_STEPS)
