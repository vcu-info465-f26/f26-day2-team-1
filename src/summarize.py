
# This file calculates earthquake statistics and uses Groq to summarize them.

from pathlib import Path
from groq import Groq
from data_queries import load_earthquake_data

# Sets the location where the generated summary will be saved.
SUMMARY_PATH = Path(__file__).resolve().parent.parent / "data" / "summary.md"

def calculate_statistics():
    """Calculate statistics from the earthquake database."""

    # Loads earthquake data from project.db.
    data = load_earthquake_data()

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
    client = Groq()

    # Asks Groq to summarize the actual earthquake data.
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": (
                    "Write a short, clear summary of these earthquake statistics. "
                    "Compare the average magnitude and significance of shallow "
                    "and deep earthquakes. Use only the numbers provided, "
                    "and include the date range. Do not invent any data.\n\n"
                    f"{statistics}"
                ),
            }
        ],
    )

    # Saves the generated summary only after Groq succeeds.
    summary = response.choices[0].message.content
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(generate_summary())