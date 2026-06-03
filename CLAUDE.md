# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Python proof-of-concept for a multi-agent "swarm" using Anthropic's Managed Agents API. It models a services firm's deal desk: one coordinator agent orchestrates four domain-specialist sub-agents to respond to an enterprise RFP and produce a branded Word document.

## Setup

Copy `.env` and add your key — all scripts load it automatically via `python-dotenv`:

```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
uv sync
uv run python setup_environment.py   # One-time: provisions cloud Environment, writes .environment_id
```

Never export the key manually or commit `.env` — it is in `.gitignore`.

## Build Sequence (must run in order on first setup)

```bash
python create_specialists.py       # Creates 4 specialist agents → .specialist_ids.json
python create_coordinator.py       # Creates coordinator agent → .coordinator_id
python upload_skills.py            # Uploads skills/, attaches to specialists → .skill_ids.json
python run_deal_desk.py            # Runs the swarm → outputs/
```

After the first setup, only `run_deal_desk.py` needs to be re-run to test prompt or data changes — it reuses the IDs saved in the dot-files.

## Utility Scripts

```bash
python download_deliverable.py [session_id]   # Re-fetch files from a past session
python stretch_critic_subagent.py             # Stretch goal: add a Critic review agent
```

## Architecture

Three-tier pattern:

**Coordinator** (`create_coordinator.py`) — Reads the RFP, fans out to all four specialists in parallel (single message, not sequential), synthesizes results, produces final deliverable. Uses `claude-opus-4-7`.

**Specialists** (`create_specialists.py`) — Four agents, each with a narrow domain system prompt:
- Pricing Specialist (`claude-sonnet-4-6`) — discount bands, payment terms, red-lines
- Legal Reviewer (`claude-sonnet-4-6`) — contract clause review against 10-item checklist
- Technical Fit Specialist (`claude-sonnet-4-6`) — capability fit matrix against RFP requirements
- Competitive Intel Analyst (`claude-haiku-4-5-20251001`) — competitor ID and positioning

**Skills** (`upload_skills.py` + `skills/`) — Structured Markdown knowledge bases (pricing playbook, legal checklist, competitive battlecards) uploaded via Skills API and attached to the matching specialist. Specialists read and reason over these, not the coordinator.

## Key Files

| File | Purpose |
|------|---------|
| `run_deal_desk.py` | Main entry point; loads RFP, streams session events, saves outputs |
| `create_specialists.py` | Agent definitions (system prompts, models, tool config) |
| `create_coordinator.py` | Coordinator definition + multiagent config linking specialist IDs |
| `upload_skills.py` | Skill upload + agent attachment logic |
| `skills/*/SKILL.md` | Domain knowledge bases (pricing, legal, competitive) |
| `synthetic-data/` | Test inputs: RFP, past deals JSON, product overview |

## State Files (generated, not committed)

`.specialist_ids.json`, `.coordinator_id`, `.skill_ids.json`, `.environment_id`, `.last_session_id` — created by the build sequence. Delete and re-run the relevant script to reprovision.

## API Usage

Uses the Managed Agents beta: `anthropic-beta: managed-agents-2026-04-01`. The `Anthropic` client is initialized with this header in each script. Session events streamed include `session.thread_created`, `session.thread_status_running`, `agent.thread_message_received`, `agent.tool_use`.

Outputs (docx, transcript) are fetched from the Files API after the session completes.

## Extending the System

`scenario-cards.md` documents two additional scenario templates (M&A Diligence, Hire-to-Onboard) that follow the same coordinator+specialists pattern.

`stretch-goals.md` documents 10 extension points across four tiers: firm voice skill, Critic sub-agent (already implemented in `stretch_critic_subagent.py`), memory tool integration, parallel fan-out events, CRM MCP, Slack notifications, PPTX output, model escalation for high-value deals, voting pattern, and recursive investigation.
