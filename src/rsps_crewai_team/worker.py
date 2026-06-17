from __future__ import annotations

import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from dotenv import load_dotenv

from rsps_crewai_team.runtime.coding_worker import run_coding_worker
from rsps_crewai_team.runtime.git_sync import create_agent_worktree, has_changes, remove_agent_worktree, sync_changes
from rsps_crewai_team.runtime.orchestrator import advance_from_work_order
from rsps_crewai_team.runtime.ponytail import ponytail_policy
from rsps_crewai_team.runtime.run_manifests import create_run_manifest, update_run_manifest
from rsps_crewai_team.runtime.settings import PROJECT_ROOT, bool_env, require_autonomy_enabled, rsps_repo_path
from rsps_crewai_team.runtime.work_orders import create_work_order, move_work_order, next_work_order, validate_workflow_metadata


def _label(prefix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{prefix}"


def enqueue(args: argparse.Namespace) -> None:
    body = args.body or " ".join(args.prompt)
    metadata = validate_workflow_metadata(getattr(args, "workflow_id", None), getattr(args, "workflow_step_id", None))
    path = create_work_order(args.title, body, metadata=metadata or None)
    print(path)


def run_once(_: argparse.Namespace) -> None:
    require_autonomy_enabled()
    rsps_repo_path()
    order = next_work_order(approved_only=bool_env("RSPS_ORCHESTRATION_APPROVAL_REQUIRED", False))
    if order is None:
        print("No work orders in inbox.")
        return
    running_path = move_work_order(order, "running")
    run_id = _label(running_path.stem)
    metadata = order.metadata or {}
    create_run_manifest(
        run_id,
        work_order_file=running_path.name,
        workflow_id=metadata.get("workflow_id"),
        workflow_step_id=metadata.get("workflow_step_id") or metadata.get("step_id"),
        workflow_department=metadata.get("workflow_department") or metadata.get("department"),
        agent_id=os.getenv("RSPS_OPENCLAW_BUILDER_AGENT", "rsps-builder"),
        mode="run_once",
        status="running",
        repo_path=str(rsps_repo_path()),
    )
    prompt = (
        "You are the coding worker for an RSPS development team. Modify the repository "
        "directly to complete this work order. Keep changes focused, run available tests "
        "when configured, and avoid unrelated refactors.\n\n"
        f"{ponytail_policy()}\n\n"
        f"Work order file: {running_path.name}\n\n{order.body}"
    )
    try:
        agent_id = os.getenv("RSPS_OPENCLAW_BUILDER_AGENT", "rsps-builder")
        result = run_coding_worker(prompt, run_id, agent_id=agent_id)
    except Exception as exc:
        failed_order = type(order)(path=running_path, title=order.title, body=order.body)
        move_work_order(failed_order, "failed")
        raise SystemExit(str(exc)) from exc
    finished_order = type(order)(path=running_path, title=order.title, body=order.body)
    final_status = "done" if result.exit_code == 0 else "failed"
    move_work_order(finished_order, final_status)
    update_run_manifest(
        run_id,
        status="done" if result.exit_code == 0 else "failed",
        ended_at=result.ended_at,
        prompt_path=str(result.prompt_path),
        log_path=str(result.log_path),
        repo_path=str(result.repo_path),
        exit_code=result.exit_code,
    )
    advance_from_work_order(metadata, final_status, detail=str(result.log_path), worker_run_id=run_id)
    print(f"exit_code={result.exit_code}")
    print(f"log={result.log_path}")


def _run_reserved_order_with_agent(agent_id: str, role: str, running_path, title: str, body: str, metadata: dict | None) -> tuple[str, int, str]:
    label = f"{agent_id}-{running_path.stem}"
    worktree = None
    from rsps_crewai_team.runtime.work_orders import WorkOrder

    finished_order = WorkOrder(path=running_path, title=title, body=body)
    keep_worktree = False
    run_id = _label(label)
    metadata = metadata or {}
    create_run_manifest(
        run_id,
        work_order_file=running_path.name,
        workflow_id=metadata.get("workflow_id"),
        workflow_step_id=metadata.get("workflow_step_id") or metadata.get("step_id"),
        workflow_department=metadata.get("workflow_department") or metadata.get("department"),
        agent_id=agent_id,
        mode="run_duo",
        status="running",
        repo_path=str(rsps_repo_path()),
    )
    try:
        cwd = rsps_repo_path()
        if os.getenv("RSPS_DUO_USE_WORKTREES", "true").strip().lower() in {"1", "true", "yes", "on"}:
            worktree = create_agent_worktree(agent_id, label)
            cwd = worktree
            update_run_manifest(run_id, worktree_path=str(worktree), repo_path=str(cwd))
        workspace_note = (
            f"Repository root for this run: {cwd}\n"
            "Only edit files under that repository root. If the work order mentions absolute "
            f"paths under {rsps_repo_path()}, translate them to the same relative path under "
            "your repository root before reading or editing. Remove the main-checkout prefix "
            f"entirely; for example, {rsps_repo_path()}/docs/file.md maps to {cwd}/docs/file.md, "
            f"not {cwd}/{rsps_repo_path().name}/docs/file.md. Do not edit the main checkout "
            "when a worktree root is assigned.\n"
        )
        prompt = (
            f"You are {role} in an RSPS coding duo. Modify the repository directly to complete "
            "this queued work order. Keep changes focused, avoid unrelated refactors, and do not "
            "touch secrets. If the task is review-oriented, make concrete fixes when appropriate.\n\n"
            f"{workspace_note}\n"
            f"{ponytail_policy()}\n\n"
            f"Work order file: {running_path.name}\n\n{body}"
        )
        result = run_coding_worker(prompt, _label(label), agent_id=agent_id, cwd=cwd)
        exit_code = result.exit_code
        detail = str(result.log_path)
        update_run_manifest(
            run_id,
            prompt_path=str(result.prompt_path),
            log_path=str(result.log_path),
            repo_path=str(result.repo_path),
            ended_at=result.ended_at,
            exit_code=result.exit_code,
        )
        if (
            exit_code == 0
            and os.getenv("RSPS_REQUIRE_WORKER_CHANGES", "false").strip().lower() in {"1", "true", "yes", "on"}
            and not has_changes(cwd)
        ):
            exit_code = 1
            detail = f"Worker completed without git-visible changes in assigned repository: {cwd}"
            keep_worktree = True
        if exit_code == 0 and os.getenv("RSPS_GIT_COMMIT_AFTER_WORK", "true").strip().lower() in {"1", "true", "yes", "on"}:
            git_result = sync_changes(f"{agent_id}: {title}", cwd)
            update_run_manifest(run_id, git_sync_exit_code=git_result.exit_code, git_sync_summary=git_result.output[-1000:])
            if git_result.exit_code != 0:
                exit_code = git_result.exit_code
                detail = git_result.output
                keep_worktree = True
    except Exception as exc:
        keep_worktree = True
        update_run_manifest(run_id, status="failed", ended_at=datetime.now(timezone.utc).isoformat(), error=str(exc))
        move_work_order(finished_order, "failed")
        return agent_id, 1, str(exc)
    finally:
        if (
            worktree is not None
            and not keep_worktree
            and os.getenv("RSPS_DUO_KEEP_WORKTREES", "false").strip().lower() not in {"1", "true", "yes", "on"}
        ):
            remove_agent_worktree(worktree)
    final_status = "done" if exit_code == 0 else "failed"
    move_work_order(finished_order, final_status)
    update_run_manifest(run_id, status=final_status, ended_at=datetime.now(timezone.utc).isoformat(), exit_code=exit_code)
    advance_from_work_order(metadata, final_status, detail=detail, worker_run_id=run_id)
    return agent_id, exit_code, detail


def run_duo(_: argparse.Namespace) -> None:
    require_autonomy_enabled()
    rsps_repo_path()
    agents = [
        (os.getenv("RSPS_OPENCLAW_BUILDER_AGENT", "rsps-builder"), "the implementation-focused builder"),
        (os.getenv("RSPS_OPENCLAW_REVIEWER_AGENT", "rsps-reviewer"), "the review-focused fixer and hardening partner"),
    ]
    reserved = []
    for agent_id, role in agents:
        order = next_work_order(approved_only=bool_env("RSPS_ORCHESTRATION_APPROVAL_REQUIRED", False))
        if order is None:
            print(f"{agent_id}: exit_code=0 detail=No work order available.")
            continue
        running_path = move_work_order(order, "running")
        reserved.append((agent_id, role, running_path, order.title, order.body, order.metadata or {}))

    if not reserved:
        return

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(_run_reserved_order_with_agent, agent_id, role, running_path, title, body, metadata)
            for agent_id, role, running_path, title, body, metadata in reserved
        ]
        for future in as_completed(futures):
            agent_id, exit_code, detail = future.result()
            print(f"{agent_id}: exit_code={exit_code} detail={detail}")


def status(_: argparse.Namespace) -> None:
    repo = "not configured"
    try:
        repo = str(rsps_repo_path())
    except Exception:
        pass
    print(f"project={PROJECT_ROOT}")
    print(f"rsps_repo={repo}")
    for name in ("inbox", "running", "done", "failed"):
        count = len(list((PROJECT_ROOT / "work_orders" / name).glob("*.md")))
        print(f"{name}={count}")


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = argparse.ArgumentParser(description="RSPS coding worker.")
    subparsers = parser.add_subparsers(required=True)

    enqueue_parser = subparsers.add_parser("enqueue", help="Create a work order.")
    enqueue_parser.add_argument("title")
    enqueue_parser.add_argument("prompt", nargs="*")
    enqueue_parser.add_argument("--body")
    enqueue_parser.add_argument("--workflow-id")
    enqueue_parser.add_argument("--workflow-step-id")
    enqueue_parser.set_defaults(func=enqueue)

    run_parser = subparsers.add_parser("run-once", help="Run one queued work order.")
    run_parser.set_defaults(func=run_once)

    duo_parser = subparsers.add_parser("run-duo", help="Run up to two queued work orders in parallel with OpenClaw agents.")
    duo_parser.set_defaults(func=run_duo)

    status_parser = subparsers.add_parser("status", help="Show queue status.")
    status_parser.set_defaults(func=status)

    args = parser.parse_args()
    try:
        args.func(args)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
