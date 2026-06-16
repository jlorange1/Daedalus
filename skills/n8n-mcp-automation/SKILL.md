---
name: n8n-mcp-automation
description: Design safe n8n/MCP-style automation contracts for Daedalus. Use when defining workflow specs, node/action contracts, tool-call boundaries, preconditions, dry-run behavior, review gates, or secret-safe automation plans before implementation or execution.
---

# n8n MCP Automation

Use this skill to design reviewable automation contracts before building or running Daedalus workflows.

## Contract Shape

Specify every workflow as a plain, reviewable spec before implementation:

- **Purpose**: State the user-facing outcome and why automation is appropriate.
- **Trigger**: Name the manual, scheduled, webhook, or MCP-triggered entry point.
- **Nodes/actions**: List each node or action explicitly, in execution order.
- **Inputs**: Define required fields, accepted formats, and rejected values.
- **Preconditions**: State what must be true before any side effect occurs.
- **Outputs**: Define artifacts, messages, records, or state changes produced.
- **Failure behavior**: Define retries, stop conditions, rollback limits, and human escalation.
- **Review gate**: Identify who or what must approve live execution.

## Safety Rules

- Default every workflow to dry-run-first. The first executable version must report intended actions without performing side effects.
- Separate read-only discovery steps from write, send, delete, purchase, publish, deploy, or permission-changing steps.
- Require explicit user approval before live side effects, external communication, irreversible edits, or cross-system synchronization.
- Keep credentials, tokens, cookies, API keys, and personal secrets out of specs, logs, prompts, examples, screenshots, and committed files.
- Reference secrets only by environment variable or secret-manager key name.
- Bound each workflow by allowed systems, allowed actions, maximum record counts, time windows, and rate limits.
- Prefer idempotent actions. Include dedupe keys, correlation IDs, or prior-state checks where repeated execution could cause harm.
- Treat MCP tools as capability boundaries: name the exact tool, action, required arguments, and denied arguments.

## Workflow Review Checklist

Before implementation or execution, verify:

- The workflow can be understood from the spec without hidden context.
- Each node/action has a clear input, output, and failure mode.
- Preconditions block unsafe execution when required data or approval is missing.
- Dry-run output is specific enough to review the planned side effects.
- Logs redact secrets and avoid exposing sensitive user, customer, or system data.
- The live-run path differs from dry-run only at the final approved side-effect step.
- Rollback or remediation is documented for every meaningful side effect.

## Output Pattern

When asked to design an automation, return:

1. A concise workflow spec.
2. A dry-run plan showing exactly what would happen.
3. Safety boundaries and approval requirements.
4. Open questions only where missing information affects safety or correctness.
