#!/usr/bin/env python3
"""
Create GitHub labels and issues for the Legacy Gateway requirements backlog.

Requires the GitHub CLI (https://cli.github.com), logged in with `gh auth login`.

Usage:
    python create_backlog_issues.py --repo OWNER/REPO --dry-run   # preview, creates nothing
    python create_backlog_issues.py --repo OWNER/REPO             # create labels + issues

What it does:
    1. Validates backlog.json (unique IDs, valid dependencies, no dependency cycles)
    2. Creates labels for type, priority (MoSCoW), area, and story points
    3. Creates one issue per requirement, titled "[REQ-###] Title"
    4. Edits each issue to link its dependencies ("Depends on" / "Blocks") by issue number
    5. Writes BACKLOG.md, a summary table of the whole backlog
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

LABELS = {
    "type:functional": ("1d76db", "Describes something the system does"),
    "type:non-functional": ("5319e7", "Describes a quality or constraint of the system"),
    "priority:must": ("b60205", "MoSCoW: required for the term project"),
    "priority:should": ("d93f0b", "MoSCoW: important but not critical"),
    "priority:could": ("fbca04", "MoSCoW: nice to have if time allows"),
    "priority:wont": ("cccccc", "MoSCoW: out of scope this term"),
    "area:legacy-app": ("c2e0c6", "Demo legacy application"),
    "area:deployment": ("c2e0c6", "Containers, configuration, deployment"),
    "area:isolation": ("c2e0c6", "Network isolation of the legacy system"),
    "area:proxy": ("c2e0c6", "Reverse proxy and request forwarding"),
    "area:auth": ("c2e0c6", "Authentication and sessions"),
    "area:mfa": ("c2e0c6", "Multi-factor authentication"),
    "area:authorization": ("c2e0c6", "Roles and access rules"),
    "area:encryption": ("c2e0c6", "TLS and transport security"),
    "area:logging": ("c2e0c6", "Audit and security logging"),
    "area:dashboard": ("c2e0c6", "Admin dashboard"),
    "area:monitoring": ("c2e0c6", "Suspicious activity detection and alerts"),
    "area:testing": ("c2e0c6", "Automated tests and CI"),
    "area:docs": ("c2e0c6", "Documentation"),
    "sp:1": ("ededed", "Story points: 1"),
    "sp:2": ("ededed", "Story points: 2"),
    "sp:3": ("ededed", "Story points: 3"),
    "sp:5": ("ededed", "Story points: 5"),
    "sp:8": ("ededed", "Story points: 8"),
}

PRIORITY_NAMES = {
    "must": "Must have",
    "should": "Should have",
    "could": "Could have",
    "wont": "Won't have (this term)",
}


def gh(args, repo, dry_run):
    """Run a gh command and return stdout. In dry-run mode, just print it."""
    cmd = ["gh"] + args + (["--repo", repo] if repo else [])
    if dry_run:
        return ""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"Command failed: {' '.join(cmd[:3])} ...\n{result.stderr.strip()}")
    return result.stdout.strip()


def validate(reqs):
    ids = [r["id"] for r in reqs]
    if len(ids) != len(set(ids)):
        sys.exit("Duplicate requirement IDs found in backlog.json")
    known = set(ids)
    for r in reqs:
        for dep in r["depends_on"]:
            if dep not in known:
                sys.exit(f"{r['id']} depends on unknown requirement {dep}")
            if dep == r["id"]:
                sys.exit(f"{r['id']} depends on itself")
        if r["priority"] not in PRIORITY_NAMES:
            sys.exit(f"{r['id']} has invalid priority {r['priority']}")
        for label in labels_for(r):
            if label not in LABELS:
                sys.exit(f"{r['id']} uses undefined label {label}")

    # Detect dependency cycles with a depth-first search
    graph = {r["id"]: r["depends_on"] for r in reqs}
    state = {}  # id -> "visiting" | "done"

    def visit(node, path):
        if state.get(node) == "done":
            return
        if state.get(node) == "visiting":
            sys.exit("Dependency cycle: " + " -> ".join(path + [node]))
        state[node] = "visiting"
        for dep in graph[node]:
            visit(dep, path + [node])
        state[node] = "done"

    for node in graph:
        visit(node, [])


def labels_for(r):
    labels = [f"type:{r['type']}", f"priority:{r['priority']}", f"area:{r['area']}"]
    if r["points"]:
        labels.append(f"sp:{r['points']}")
    return labels


def ref(req_id, numbers, titles):
    """How to reference another requirement: '#12 (REQ-004 Title)' once issues exist."""
    if req_id in numbers:
        return f"#{numbers[req_id]} ({req_id}: {titles[req_id]})"
    return f"{req_id}: {titles[req_id]}"


def build_body(r, numbers, titles, blocks):
    points = r["points"] if r["points"] else "Not estimated (out of scope)"
    lines = [
        f"**Requirement ID:** {r['id']}",
        f"**Stakeholder:** {r['stakeholder']}",
        f"**Type:** {r['type'].capitalize()}",
        f"**Priority:** {PRIORITY_NAMES[r['priority']]}",
        f"**Story points:** {points}",
        "",
        "### User story",
        r["story"],
        "",
        "### Acceptance criteria",
    ]
    lines += [f"- [ ] {c}" for c in r["acceptance"]]
    lines += ["", "### Dependencies", "**Depends on:**"]
    lines += [f"- {ref(d, numbers, titles)}" for d in r["depends_on"]] or ["- None"]
    lines += ["", "**Blocks:**"]
    lines += [f"- {ref(b, numbers, titles)}" for b in blocks.get(r["id"], [])] or ["- None"]
    return "\n".join(lines)


def write_summary(reqs, numbers, titles, path):
    rows = [
        "# Requirements Backlog",
        "",
        "Initial requirements elicitation pass for the Legacy Gateway project. "
        "Each requirement is tracked as a GitHub issue with labels for type, "
        "priority (MoSCoW), area, and story points.",
        "",
        "| Issue | ID | Requirement | Type | Priority | Points | Area | Depends on |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in reqs:
        issue = f"#{numbers[r['id']]}" if r["id"] in numbers else "-"
        deps = ", ".join(
            f"#{numbers[d]}" if d in numbers else d for d in r["depends_on"]
        ) or "None"
        rows.append(
            f"| {issue} | {r['id']} | {titles[r['id']]} | {r['type']} | "
            f"{PRIORITY_NAMES[r['priority']]} | {r['points'] or '-'} | {r['area']} | {deps} |"
        )
    path.write_text("\n".join(rows) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", help="OWNER/REPO (defaults to the repo in the current directory)")
    parser.add_argument("--file", default="backlog.json", help="Path to the backlog JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating anything")
    args = parser.parse_args()

    data = json.loads(Path(args.file).read_text())
    reqs = data["requirements"]
    validate(reqs)
    titles = {r["id"]: r["title"] for r in reqs}

    blocks = {}
    for r in reqs:
        for dep in r["depends_on"]:
            blocks.setdefault(dep, []).append(r["id"])

    print(f"Backlog is valid: {len(reqs)} requirements, {len(LABELS)} labels.")

    if args.dry_run:
        print("\nDry run. Nothing will be created. Example issue:\n")
        sample = next(r for r in reqs if r["depends_on"] and r["id"] in blocks)
        print(f"Title:  [{sample['id']}] {sample['title']}")
        print(f"Labels: {', '.join(labels_for(sample))}\n")
        print(build_body(sample, {}, titles, blocks))
        return

    if not shutil.which("gh"):
        sys.exit("GitHub CLI not found. Install it from https://cli.github.com and run `gh auth login`.")
    if subprocess.run(["gh", "auth", "status"], capture_output=True).returncode != 0:
        sys.exit("You're not logged in to the GitHub CLI. Run `gh auth login` first.")

    # Guard against creating duplicates if the script is run twice
    existing = json.loads(gh(["issue", "list", "--state", "all", "--limit", "1000", "--json", "title"], args.repo, False) or "[]")
    if any(i["title"].startswith("[REQ-") for i in existing):
        sys.exit("This repo already has [REQ-###] issues. Stopping so nothing gets duplicated.")

    print("Creating labels...")
    for name, (color, desc) in LABELS.items():
        gh(["label", "create", name, "--color", color, "--description", desc, "--force"], args.repo, False)

    print("Creating issues...")
    numbers = {}
    for r in reqs:
        url = gh(
            ["issue", "create",
             "--title", f"[{r['id']}] {r['title']}",
             "--body", build_body(r, {}, titles, blocks),
             "--label", ",".join(labels_for(r))],
            args.repo, False,
        )
        numbers[r["id"]] = int(url.rstrip("/").split("/")[-1])
        print(f"  #{numbers[r['id']]}  [{r['id']}] {r['title']}")

    print("Linking dependencies...")
    for r in reqs:
        if r["depends_on"] or r["id"] in blocks:
            gh(["issue", "edit", str(numbers[r["id"]]),
                "--body", build_body(r, numbers, titles, blocks)], args.repo, False)

    write_summary(reqs, numbers, titles, Path("BACKLOG.md"))
    print("\nDone. BACKLOG.md written. Commit and push it to include the summary in your repo.")


if __name__ == "__main__":
    main()
