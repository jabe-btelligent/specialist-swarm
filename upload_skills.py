"""
No-op for the AAPL stock-ranking POC.

This POC intentionally does not use custom skills. Each specialist has one
narrow prompt and receives local saved data from local-data/stocks/AAPL/.

Usage:
    uv run python upload_skills.py
"""


def main() -> None:
    print("No skills to upload for the AAPL stock-ranking POC.")
    print("Next: uv run python create_coordinator.py")


if __name__ == "__main__":
    main()
