from __future__ import annotations

import os


def ponytail_enabled() -> bool:
    return os.getenv("RSPS_PONYTAIL_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


def ponytail_mode() -> str:
    mode = os.getenv("PONYTAIL_DEFAULT_MODE", "full").strip().lower()
    return mode if mode in {"off", "lite", "full", "ultra"} else "full"


def ponytail_policy() -> str:
    if not ponytail_enabled() or ponytail_mode() == "off":
        return "Ponytail mode is off."

    base = (
        "Ponytail policy: act like a lazy senior developer. Lazy means efficient, not careless. "
        "Before adding code, check whether the work can be skipped, handled by the standard library, "
        "handled by the platform/RSPS engine, handled by an installed dependency, or reduced to a "
        "small data/config change. Prefer deletion over addition. Do not add abstractions, services, "
        "dependencies, generated boilerplate, or broad rewrites unless the work order explicitly needs them. "
        "Do not weaken trust-boundary validation, auth, permissions, persistence safety, economy safety, "
        "accessibility, or tests. Mark intentional shortcuts with a `ponytail:` comment that names the "
        "ceiling and upgrade path. Non-trivial logic needs one small runnable check."
    )

    mode = ponytail_mode()
    if mode == "lite":
        return (
            "Ponytail policy: prefer the smallest correct solution. Use existing platform, stdlib, "
            "config, or installed dependencies before writing new code. No unrequested abstractions."
        )
    if mode == "ultra":
        return base + (
            " Ultra mode: aggressively challenge scope. If a work order asks for a large subsystem, "
            "produce the smallest useful vertical slice first and list what was intentionally deferred."
        )
    return base
