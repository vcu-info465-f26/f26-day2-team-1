
# This file calculates earthquake statistics and uses Groq to summarize them.

import os
import re
from pathlib import Path
from openai import OpenAI
from build_db import main as rebuild_database
from data_queries import load_earthquake_data

# Sets the location where the generated summary will be saved.
SUMMARY_PATH = Path(__file__).resolve().parent.parent / "data" / "summary.md"

# Keeps the model name in one place.
MODEL = "openai/gpt-oss-120b"


def format_summary_markdown(summary):
    """Keep older and newly generated summaries in the same format."""
    lines = []
    for line in summary.splitlines():
        if re.fullmatch(
            r"\s*(?:#{1,6}\s+)?(?:\*\*)?Earthquake(?: Statistics)? Summary"
            r"(?:\s*\([^)]*\))?(?:\*\*)?\s*:?\s*",
            line,
            flags=re.IGNORECASE,
        ):
            continue

        if line.startswith("**Data covered:**"):
            line = re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b", r"\2-\3-\1", line)

        lines.append(line)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def calculate_statistics():
    """Calculate statistics from the earthquake database."""

    # Rebuilds the database to include the latest snapshots.
    rebuild_database()

    # Loads earthquake data from project.db.
    data = load_earthquake_data()

    if data.empty:
        raise ValueError("No earthquake data is available to summarize.")

    # Gets the date range covered by the data.
    start_date = data["event_time"].min().strftime("%Y-%m-%d")
    end_date = data["event_time"].max().strftime("%Y-%m-%d")

    # Calculates the averages for shallow and deep earthquakes.
    averages = data.groupby("depth_group")[["magnitude", "significance"]].mean().round(2)

    # Returns the statistics that Groq will use to write the summary.
    return {
        "total": len(data),
        "start_date": start_date,
        "end_date": end_date,
        "averages": averages.to_string(),
    }

def generate_summary():
    """Use Groq to explain the earthquake statistics."""

    # Gets the statistics calculated from project.db.
    statistics = calculate_statistics()

    # Connects to Groq using the API key stored in Codespaces.
    # GitHub Actions supplies the same key through a repository secret.
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=os.environ["GROQ_API_KEY"],
    )

    # Asks Groq to summarize the actual earthquake data.
    response = client.chat.completions.create(
        model=MODEL,
        reasoning_effort="low",
        messages=[
            {
                "role": "user",
                "content": (
                    "Write a short, clear summary of these earthquake statistics. "
                    "Compare the average magnitude and significance of shallow "
                    "and deep earthquakes. Use only the numbers provided. "
                    "Do not add a title or repeat the date range; the dashboard adds it. "
                    "Do not invent any data.\n\n"
                    f"{statistics}"
                ),
            }
        ],
    )

    # Rejects missing, incomplete, or empty responses before changing the file.
    if not response.choices or response.choices[0].finish_reason != "stop":
        raise ValueError("Groq did not return a complete summary.")

    content = response.choices[0].message.content
    summary = format_summary_markdown(content) if isinstance(content, str) else ""
    if not summary:
        raise ValueError("Groq returned an empty summary.")

    # Displays the source dates without relying on the AI to repeat them.
    summary = format_summary_markdown(
        f"**Data covered:** {statistics['start_date']} to "
        f"{statistics['end_date']} (UTC).\n\n"
        f"{summary}"
    ) + "\n"

    # Saves the generated summary only after Groq succeeds.
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(generate_summary())
