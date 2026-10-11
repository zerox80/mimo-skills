#!/usr/bin/env python3
"""Consistency gate for mimo-security-scan/v1 deep-security-scan artifacts.

Stdlib only. Validates structure and cross-artifact consistency that prose
cannot enforce. Factual correctness of findings is NOT tested.

Checks:
  - required artifact files present
  - format markers
  - findings schema (ids, severity/confidence, locations, evidence, remediation)
  - coverage honesty (no path both reviewed and remaining; clean path strings)
  - candidate outcomes are terminal and disjoint from findings
  - report.md mentions exactly the findings.json ids (no resurrected disproven ones)
  - scan-manifest pass counts and artifact list

Usage:
  python validate_artifacts.py <output-dir>
  python validate_artifacts.py --findings F.json --coverage C.json --manifest M.json --report R.md

Exit codes: 0 PASS (warnings allowed), 1 FAIL, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEVERITIES = {"critical", "high", "medium", "low"}
CONFIDENCES = {"high", "medium", "low"}
CANDIDATE_OUTCOMES = {"reportable", "suppressed", "not_applicable", "deferred", "disproven", "disproven_as_reportable"}
# Outcomes that must NOT reappear as findings
NOT_REPORTABLE = {"suppressed", "not_applicable", "deferred", "disproven", "disproven_as_reportable"}
PATH_ROLES = {
    "entrypoint", "root_control", "sink", "concrete_implementation", "source",
    "control", "config", "caller", "test", "other",
}

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_json(path: Path, label: str) -> dict | None:
    if not path.is_file():
        err(f"{label}: missing file {path}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        err(f"{label}: unreadable JSON ({e})")
        return None
    if not isinstance(data, dict):
        err(f"{label}: top level must be an object")
        return None
    return data


def check_format(obj: dict | None, label: str) -> None:
    if obj is None:
        return
    fmt = obj.get("format")
    if fmt not in ("mimo-security-scan/v1", "claude-security-scan/v1"):
        err(f"{label}: format must be mimo-security-scan/v1 (got {fmt!r})")
    elif fmt == "claude-security-scan/v1":
        warn(f"{label}: imported claude-security-scan/v1 — keep as provenance; new output should use mimo-security-scan/v1")


def check_location(loc: object, finding_id: str, idx: int) -> None:
    where = f"{finding_id}.locations[{idx}]"
    if not isinstance(loc, dict):
        err(f"{where}: must be an object")
        return
    # accept legacy affected_locations shape
    path = loc.get("path") or loc.get("file")
    if not path or not isinstance(path, str):
        err(f"{where}: needs 'path' (or legacy 'file')")
        return
    if " (" in path or path.endswith(")") and " (" in path:
        warn(f"{where}: path contains annotation {path!r} — use a clean repo-relative path and put notes in 'detail'")
    if path.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", path):
        warn(f"{where}: path looks absolute ({path!r}) — prefer repository-relative")
    if "startLine" in loc:
        sl = loc["startLine"]
        if not isinstance(sl, int) or sl < 1:
            err(f"{where}.startLine: must be a positive integer")
        el = loc.get("endLine")
        if el is not None and (not isinstance(el, int) or el < (sl or 0)):
            err(f"{where}.endLine: must be an integer >= startLine")
    elif isinstance(loc.get("lines"), str):
        pass  # legacy string form
    else:
        warn(f"{where}: no startLine — include exact line numbers when available")
    roles = loc.get("roles")
    if roles is not None:
        if not isinstance(roles, list) or not all(isinstance(r, str) for r in roles):
            err(f"{where}.roles: must be a list of strings")
        else:
            unknown = [r for r in roles if r not in PATH_ROLES]
            if unknown:
                warn(f"{where}.roles: nonstandard roles {unknown} (allowed: {sorted(PATH_ROLES)})")


def check_findings(data: dict | None) -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    if data is None:
        return by_id
    check_format(data, "findings.json")
    findings = data.get("findings")
    if not isinstance(findings, list):
        err("findings.json: 'findings' must be an array (use [] when none)")
        return by_id
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            err(f"findings[{i}]: must be an object")
            continue
        fid = f.get("id")
        if not fid or not isinstance(fid, str):
            err(f"findings[{i}]: missing string 'id'")
            continue
        if fid in by_id:
            err(f"findings: duplicate id {fid!r}")
        by_id[fid] = f
        if not f.get("title"):
            err(f"{fid}: missing 'title'")
        sev = f.get("severity")
        if sev not in SEVERITIES:
            err(f"{fid}: severity must be one of {sorted(SEVERITIES)} (got {sev!r})")
        conf = f.get("confidence")
        if conf not in CONFIDENCES:
            err(f"{fid}: confidence must be one of {sorted(CONFIDENCES)} (got {conf!r})")
        locs = f.get("locations") or f.get("affected_locations")
        if not isinstance(locs, list) or not locs:
            err(f"{fid}: needs non-empty 'locations'")
        else:
            for j, loc in enumerate(locs):
                check_location(loc, fid, j)
        if not f.get("evidence"):
            err(f"{fid}: needs 'evidence' (source-backed quotes/observations)")
        if not f.get("remediation"):
            err(f"{fid}: needs 'remediation'")
        for req in ("impact", "weakness"):
            if not f.get(req) and not f.get("root_cause"):
                warn(f"{fid}: missing '{req}' — required for a complete static assessment")
        reportable = f.get("reportable")
        if reportable is not None and not isinstance(reportable, bool):
            err(f"{fid}: 'reportable' must be a boolean when present")
        if reportable is False:
            err(f"{fid}: reportable=false must not live in findings[] — move to coverage suppressed/deferred")
        status = f.get("status")
        if status is not None and status not in (
            "reportable", "reportable_with_gate", "informational", "defense_in_depth"
        ):
            warn(f"{fid}: unknown status {status!r}")
        gates = f.get("gates")
        if gates is not None:
            if not isinstance(gates, list):
                err(f"{fid}.gates: must be an array")
            else:
                for g in gates:
                    if not isinstance(g, dict) or not g.get("gate_id") or not g.get("description"):
                        err(f"{fid}.gates: each gate needs gate_id and description")
        # severity/confidence must be separate keys, not merged
        if isinstance(f.get("severity_confidence"), str):
            warn(f"{fid}: use separate severity and confidence fields")
    return by_id


def path_is_dirty(p: str) -> bool:
    return " (" in p or p.startswith("/") or bool(re.match(r"^[A-Za-z]:[\\/]", p))


def check_coverage(data: dict | None, finding_ids: set[str]) -> None:
    if data is None:
        return
    check_format(data, "coverage.json")
    reviewed = data.get("fully_reviewed_paths") or []
    remaining = data.get("remaining_paths") or []
    supporting = data.get("supporting_paths") or []
    for label, arr in (
        ("fully_reviewed_paths", reviewed),
        ("remaining_paths", remaining),
        ("supporting_paths", supporting),
    ):
        if not isinstance(arr, list):
            err(f"coverage.json: '{label}' must be an array")
            return
        for p in arr:
            if not isinstance(p, str) or not p.strip():
                err(f"coverage.json.{label}: entries must be non-empty strings")
            elif path_is_dirty(p):
                warn(f"coverage.json.{label}: dirty path string {p!r} — use clean repo-relative paths for dedup")

    rset = set(x for x in reviewed if isinstance(x, str))
    mset = set(x for x in remaining if isinstance(x, str))
    both = rset & mset
    if both:
        err(f"coverage.json: paths both fully_reviewed and remaining: {sorted(both)[:5]}")

    complete = data.get("complete")
    if not isinstance(complete, bool):
        err("coverage.json: 'complete' must be a boolean")
    elif complete and mset:
        err("coverage.json: complete=true but remaining_paths is non-empty")
    elif complete is False and not mset and not data.get("deferred"):
        warn("coverage.json: complete=false with empty remaining_paths and no deferred — explain the gap")

    # candidates
    seen_cand: set[str] = set()
    for key in ("suppressed_candidates", "deferred"):
        arr = data.get(key) or []
        if not isinstance(arr, list):
            err(f"coverage.json: '{key}' must be an array")
            continue
        for c in arr:
            if not isinstance(c, dict):
                err(f"coverage.json.{key}: entries must be objects")
                continue
            cid = c.get("id")
            if not cid:
                err(f"coverage.json.{key}: entry missing 'id'")
                continue
            if cid in seen_cand:
                err(f"coverage.json: duplicate candidate id {cid!r}")
            seen_cand.add(cid)
            if cid in finding_ids:
                err(f"coverage.json: candidate {cid!r} is also a findings[] id — outcomes must be disjoint")
            if key == "suppressed_candidates":
                outcome = c.get("outcome")
                if outcome not in NOT_REPORTABLE:
                    err(f"coverage.json.{key}[{cid}]: outcome must be one of {sorted(NOT_REPORTABLE)} (got {outcome!r})")
                if not c.get("reason") and not c.get("counterevidence"):
                    err(f"coverage.json.{key}[{cid}]: needs 'reason' or counterevidence")
            else:
                if not c.get("how_to_resolve"):
                    err(f"coverage.json.deferred[{cid}]: needs 'how_to_resolve'")
                if not c.get("why"):
                    warn(f"coverage.json.deferred[{cid}]: missing 'why'")

    # every suppressed candidate id must not appear as reportable in report.md — checked in check_report


def extract_finding_ids_from_report(text: str) -> tuple[set[str], set[str]]:
    """Return (presented_as_findings, other_F_ids_in_prose).

    An id is 'presented as a finding' when it heads a section or is the first
    cell of a table row — the two shapes used for real findings. Bare mentions
    in prose (e.g. 'was drafted as F2') are not presentations.
    """
    presented = set(re.findall(r"(?m)^#{2,4}\s+(F\d+)\b", text))
    presented |= set(re.findall(r"(?m)^\|\s*(F\d+)\s*\|", text))
    all_f = set(re.findall(r"\bF\d+\b", text))
    other = all_f - presented
    return presented, other



def check_report(report_path: Path | None, finding_ids: set[str], coverage: dict | None) -> None:
    if report_path is None:
        return
    if not report_path.is_file():
        err(f"report.md: missing file {report_path}")
        return
    text = report_path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        err("report.md: empty")
        return

    mentioned, prose_fids = extract_finding_ids_from_report(text)

    # every findings.json id must appear in the report
    missing = finding_ids - mentioned
    if missing:
        err(f"report.md: findings.json ids not presented as findings: {sorted(missing)}")

    # report must not invent finding ids
    invented = mentioned - finding_ids
    if invented:
        err(
            f"report.md: presents finding ids not in findings.json: {sorted(invented)} "
            "— disproven/draft candidates must never appear as findings"
        )

    # resurrected candidates: coverage says this F-id was superseded/disproven
    if coverage:
        superseded: dict[str, str] = {}
        for c in (coverage.get("suppressed_candidates") or []):
            if not isinstance(c, dict):
                continue
            blob = " ".join(str(c.get(k, "")) for k in ("id", "title", "reason", "was_drafted_as"))
            was = c.get("was_drafted_as")
            if isinstance(was, str) and was.startswith("F"):
                superseded[was] = str(c.get("id"))
            for old in re.findall(r"\bF(\d+)\b", blob):
                superseded.setdefault(f"F{old}", str(c.get("id")))
        for old_id, cand in superseded.items():
            if old_id in mentioned and old_id not in finding_ids:
                err(
                    f"report.md: resurrects {old_id} which coverage marks superseded/disproven "
                    f"(candidate {cand!r})"
                )
            elif old_id in prose_fids and old_id not in finding_ids:
                # prose reference is acceptable only as historical context
                pass

    # basic required sections
    for heading in ("Summary", "Coverage"):
        pat = r"(?mi)^#{1,3}\s+.*\b" + re.escape(heading) + r"\b"
        if not re.search(pat, text):
            warn(f"report.md: missing '{heading}' section heading")
    if not re.search(r"(?mi)^#{1,3}\s+.*\b(Suppressed|Disproven)\b", text):
        # not fatal — some reports put suppressed candidates only in coverage.json
        pass


def check_manifest(data: dict | None, artifact_names: set[str]) -> None:
    if data is None:
        return
    check_format(data, "scan-manifest.json")
    scan = data.get("scan")
    if not isinstance(scan, dict):
        err("scan-manifest.json: missing 'scan' object")
    else:
        planned = scan.get("passes_planned")
        executed = scan.get("passes_executed")
        if not isinstance(planned, int) or planned < 1:
            err("scan-manifest.json: scan.passes_planned must be a positive integer")
        if not isinstance(executed, int) or executed < 0:
            err("scan-manifest.json: scan.passes_executed must be a non-negative integer")
        elif isinstance(planned, int) and executed > planned:
            err("scan-manifest.json: passes_executed > passes_planned")
        if scan.get("pass_independence") is True and scan.get("pass_independence_note") is None:
            warn("scan-manifest.json: pass_independence=true needs a note explaining the isolation mechanism")
        if scan.get("pass_independence") is False and not scan.get("pass_independence_note"):
            warn("scan-manifest.json: pass_independence=false should state that passes shared a context")
    if not data.get("target"):
        err("scan-manifest.json: missing 'target'")
    arts = data.get("artifacts")
    if isinstance(arts, list):
        listed = {a for a in arts if isinstance(a, str)}
        # only require the core five to be listed if present on disk
        core = {"scan-manifest.json", "threatmodel.md", "findings.json", "coverage.json", "report.md"}
        on_disk_core = core & artifact_names
        missing_list = on_disk_core - listed
        if missing_list:
            warn(f"scan-manifest.json: artifacts[] missing on-disk files {sorted(missing_list)}")
    else:
        warn("scan-manifest.json: no 'artifacts' list")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("output_dir", nargs="?", help="directory containing the five artifacts")
    ap.add_argument("--findings", type=Path)
    ap.add_argument("--coverage", type=Path)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--report", type=Path)
    ap.add_argument("--threatmodel", type=Path)
    args = ap.parse_args()

    if not args.output_dir and not (args.findings or args.coverage or args.manifest or args.report):
        ap.print_usage()
        return 2

    base = Path(args.output_dir).resolve() if args.output_dir else None
    if base and not base.is_dir():
        print(f"ERROR: not a directory: {base}", file=sys.stderr)
        return 2

    findings_path = args.findings or (base / "findings.json" if base else None)
    coverage_path = args.coverage or (base / "coverage.json" if base else None)
    manifest_path = args.manifest or (base / "scan-manifest.json" if base else None)
    report_path = args.report or (base / "report.md" if base else None)
    threat_path = args.threatmodel or (base / "threatmodel.md" if base else None)

    artifact_names: set[str] = set()
    if base:
        artifact_names = {p.name for p in base.iterdir() if p.is_file()}
        for req in ("scan-manifest.json", "threatmodel.md", "findings.json", "coverage.json", "report.md"):
            if req not in artifact_names:
                # threatmodel may be optional for partial; still an error for complete delivery
                if req == "threatmodel.md":
                    warn(f"missing artifact: {req}")
                else:
                    err(f"missing artifact: {req}")

    if threat_path and not threat_path.is_file() and base:
        pass  # already warned

    findings = load_json(findings_path, "findings.json") if findings_path else None
    coverage = load_json(coverage_path, "coverage.json") if coverage_path else None
    manifest = load_json(manifest_path, "scan-manifest.json") if manifest_path else None

    by_id = check_findings(findings)
    check_coverage(coverage, set(by_id))
    check_report(report_path, set(by_id), coverage)
    check_manifest(manifest, artifact_names)

    # was_drafted_as must not still be a live finding
    if coverage:
        for c in (coverage.get("suppressed_candidates") or []):
            if not isinstance(c, dict):
                continue
            was = c.get("was_drafted_as")
            if isinstance(was, str) and was in by_id:
                err(
                    f"coverage.json: candidate {c.get('id')!r} has was_drafted_as={was!r} "
                    f"but {was} is still in findings[] — remove the draft or the candidate"
                )

    # summary cross-check
    if findings and isinstance(findings.get("summary"), dict):
        total = findings["summary"].get("total_findings")
        if isinstance(total, int) and total != len(by_id):
            err(f"findings.json.summary.total_findings={total} but findings[] has {len(by_id)}")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\nFAIL  {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS  0 errors, {len(warnings)} warning(s). Factual correctness was not tested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
