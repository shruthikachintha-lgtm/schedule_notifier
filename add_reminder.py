"""
Add Reminder Tool
------------------
A simple command-line helper to add a new reminder to config.json without
manually editing JSON. Works for ANY kind of reminder - water, meetings,
food, calls, anything - not just the examples already in config.json.

Usage examples:

  python add_reminder.py --title "Team Meeting" --time "15:00" --message "Join the Zoom call" --days Mon Wed Fri

  python add_reminder.py --title "Doctor Appointment" --time "10:30" --message "Appointment with Dr. Smith today" --days Sat

  python add_reminder.py --title "Water" --time "16:00" --message "Drink water" --days Mon Tue Wed Thu Fri Sat Sun --gemini

If --days is omitted, it defaults to every day.
If --gemini is passed, Gemini will generate the message live (using --message
as the base instruction for what to write about).
"""

import json
import argparse
import os
import re

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

VALID_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def slugify(text):
    """Turn a title into a safe, unique-ish id, e.g. 'Team Meeting' -> 'team_meeting'."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return slug or "reminder"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Add a new reminder to config.json")
    parser.add_argument("--title", required=True, help="Notification title, e.g. 'Team Meeting'")
    parser.add_argument("--time", required=True, help="24-hour time, e.g. '15:00'")
    parser.add_argument("--message", required=True, help="The reminder text (or Gemini prompt topic if --gemini is used)")
    parser.add_argument("--days", nargs="*", default=VALID_DAYS,
                         help="Days it should fire, e.g. --days Mon Wed Fri. Defaults to every day.")
    parser.add_argument("--gemini", action="store_true",
                         help="If set, Gemini generates the message live instead of using --message as-is")
    parser.add_argument("--id", default=None, help="Optional custom id. Auto-generated from title if omitted.")

    args = parser.parse_args()

    # Validate time format
    if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", args.time):
        print(f"ERROR: '{args.time}' is not a valid 24-hour HH:MM time (e.g. 09:00, 15:30).")
        return

    # Validate days
    bad_days = [d for d in args.days if d not in VALID_DAYS]
    if bad_days:
        print(f"ERROR: Invalid day(s) {bad_days}. Valid options: {VALID_DAYS}")
        return

    config = load_config()

    base_id = args.id or slugify(args.title)
    existing_ids = {entry.get("id") for entry in config.get("schedules", [])}
    new_id = base_id
    counter = 2
    while new_id in existing_ids:
        new_id = f"{base_id}_{counter}"
        counter += 1

    new_entry = {
        "id": new_id,
        "time": args.time,
        "days": args.days,
        "title": args.title,
        "message": args.message,
        "use_gemini": args.gemini,
    }
    if args.gemini:
        new_entry["gemini_prompt"] = (
            f"Write one short, friendly one-sentence reminder (max 15 words) about: {args.message}"
        )

    config.setdefault("schedules", []).append(new_entry)
    save_config(config)

    print(f"Added reminder '{new_id}':")
    print(json.dumps(new_entry, indent=2))
    print("\nRestart notifier.py for this to take effect.")


if __name__ == "__main__":
    main()
