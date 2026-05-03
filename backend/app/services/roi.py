AVG_MINUTES_MANUAL = 4.0
HOURLY_RATE_DEFAULT = 100.0


def calculate_roi(entries_count: int, hourly_rate: float = HOURLY_RATE_DEFAULT) -> dict:
    hours_saved = round(entries_count * AVG_MINUTES_MANUAL / 60, 2)
    cost_saved = round(hours_saved * hourly_rate, 2)
    return {
        "hours_saved": hours_saved,
        "cost_saved": cost_saved,
        "avg_minutes_per_entry_manual": AVG_MINUTES_MANUAL,
    }
