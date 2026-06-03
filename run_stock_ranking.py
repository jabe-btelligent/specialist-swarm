"""
Run the AAPL stock-ranking swarm from local saved data.

This does not fetch market, financial, or sentiment data. It reads whatever is
saved under local-data/stocks/AAPL/ and sends that context to the coordinator.

Usage:
    uv run python run_stock_ranking.py
"""

import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


TICKER = "AAPL"
DATA_ROOT = Path("local-data/stocks") / TICKER
DATA_FILES = [
    DATA_ROOT / "manifest.json",
    DATA_ROOT / "kurstrend" / "metadata.json",
    DATA_ROOT / "kurstrend" / "data.json",
    DATA_ROOT / "financial_report" / "metadata.json",
    DATA_ROOT / "financial_report" / "latest_quarterly_report.md",
    DATA_ROOT / "sentiment" / "metadata.json",
    DATA_ROOT / "sentiment" / "data.json",
]
OUTPUT_DIR = Path("outputs")


def load_local_context() -> str:
    blocks: list[str] = []

    for path in DATA_FILES:
        if not path.exists():
            print(f"  WARNING: {path} missing - skipping")
            continue
        print(f"  including {path}")
        blocks.append(f"===== LOCAL FILE: {path} =====\n{path.read_text()}")

    return "\n\n".join(blocks)


def main() -> None:
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    if not Path(".coordinator_id").exists() or not Path(".environment_id").exists():
        raise SystemExit(
            "Missing .coordinator_id or .environment_id. Run setup_environment.py, "
            "create_specialists.py, then create_coordinator.py first."
        )

    coordinator_id = Path(".coordinator_id").read_text().strip()
    environment_id = Path(".environment_id").read_text().strip()

    client = Anthropic()

    print(f"Loading local {TICKER} context...")
    context = load_local_context()

    print(f"\nStarting session against coordinator {coordinator_id}...")
    session = client.beta.sessions.create(
        agent=coordinator_id,
        environment_id=environment_id,
        title=f"{TICKER} Stock Ranking POC",
    )
    Path(".last_session_id").write_text(session.id)

    user_message = (
        f"Rank {TICKER} using the stock-ranking POC process.\n\n"
        "Rules:\n"
        "1. Use only the local context below.\n"
        "2. Delegate to all three specialists in parallel.\n"
        "3. Return a concise final ranking with scores, reasons, risks, and confidence.\n"
        "4. If the files are still templates, do not invent market facts. Explain which "
        "files need to be filled.\n\n"
        f"{context}"
    )

    print("\n=== EVENT STREAM ===\n")
    final_text_parts: list[str] = []

    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": user_message}],
                }
            ],
        )
        for event in stream:
            t = event.type
            if t == "session.thread_created":
                print(f"  [thread spawned]   {event.agent_name}", flush=True)
            elif t == "session.thread_status_running":
                name = getattr(event, "agent_name", "?")
                print(f"  [thread running]   {name}", flush=True)
            elif t == "agent.thread_message_received":
                print(f"  [reply <-]         {event.from_agent_name}", flush=True)
            elif t == "agent.thread_message_sent":
                print(f"  [delegate ->]      {event.to_agent_name}", flush=True)
            elif t == "agent.message":
                for block in event.content:
                    if getattr(block, "type", None) == "text":
                        final_text_parts.append(block.text)
                        print(block.text, end="", flush=True)
            elif t == "session.status_idle":
                print("\n\n[stock ranking finished]")
                break

    OUTPUT_DIR.mkdir(exist_ok=True)
    transcript_path = OUTPUT_DIR / "stock-ranking-transcript.txt"
    transcript_path.write_text("".join(final_text_parts))
    print(f"\nCoordinator transcript saved to {transcript_path}")
    print(f"\nView the full session at:")
    print(f"  https://platform.claude.com/sessions/{session.id}")


if __name__ == "__main__":
    main()
