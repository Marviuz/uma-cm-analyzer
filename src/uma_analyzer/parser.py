import csv
import re
from pathlib import Path

from uma_analyzer.models import RaceEntry, Strategy

UMA_NAME_VARIANTS: dict[str, str] = {
    "kitasan black (new year)": "Kitasan Black",
    "kitasan black (ny)": "Kitasan Black",
    "kitasan black new year": "Kitasan Black",
    "grass wonder (new year)": "Grass Wonder",
    "grass wonder ny": "Grass Wonder",
    "sirius black": "Sirius Black",
    "tokai teio (new year)": "Tokai Teio",
    "tokai teio ny": "Tokai Teio",
}


class ValidationError:
    def __init__(self, message: str, row: int | None = None) -> None:
        self.message = message
        self.row = row


class ParseResult:
    def __init__(self) -> None:
        self.entries: list[RaceEntry] = []
        self.duplicate_race_ids: set[str] = set()
        self.missing_skill_warnings: list[str] = []
        self.validation_errors: list[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        return len(self.validation_errors) == 0


def normalize_uma_name(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", name.strip().lower())
    return UMA_NAME_VARIANTS.get(cleaned, name.strip())


def parse_bool(value: str) -> bool:
    return value in ("1", "true", "True", "yes", "Yes")


def parse_int(value: str, field: str, row: int) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def parse_csv(path: Path) -> ParseResult:
    result = ParseResult()
    seen_race_ids: dict[str, int] = {}

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_fields = [
            "Race_ID",
            "Uma_Name",
            "Strategy",
            "Speed",
            "Stamina",
            "Power",
            "Guts",
            "Wisdom",
            "Dist_S",
            "Surface_S",
            "Track_S",
            "Skills_Activated",
            "Rank",
            "Distance_Diff",
        ]
        if reader.fieldnames:
            missing = set(required_fields) - set(reader.fieldnames)
            if missing:
                result.validation_errors.append(
                    ValidationError(f"Missing columns: {missing}")
                )
                return result

        for row_num, row in enumerate(reader, start=2):
            race_id = row.get("Race_ID", "").strip()
            if not race_id:
                result.validation_errors.append(
                    ValidationError("Missing Race_ID", row_num)
                )
                continue

            if race_id in seen_race_ids:
                result.duplicate_race_ids.add(race_id)
            seen_race_ids[race_id] = row_num

            uma_name_raw = row.get("Uma_Name", "").strip()
            uma_name = normalize_uma_name(uma_name_raw)

            strategy_raw = row.get("Strategy", "").strip()
            try:
                strategy = Strategy.from_string(strategy_raw)
            except ValueError:
                result.validation_errors.append(
                    ValidationError(f"Invalid strategy: {strategy_raw}", row_num)
                )
                continue

            stats: dict[str, str] = {
                "Speed": row.get("Speed", ""),
                "Stamina": row.get("Stamina", ""),
                "Power": row.get("Power", ""),
                "Guts": row.get("Guts", ""),
                "Wisdom": row.get("Wisdom", ""),
            }
            for stat_name, stat_value in stats.items():
                if not stat_value or not stat_value.isdigit():
                    result.validation_errors.append(
                        ValidationError(
                            f"Invalid {stat_name}: {stat_value}", row_num
                        )
                    )

            skills_raw = row.get("Skills_Activated", "").strip()
            if not skills_raw or skills_raw.lower() in ("n/a", "none", "-"):
                skills: list[str] = []
                result.missing_skill_warnings.append(
                    f"Row {row_num}: Missing skills for {uma_name}"
                )
            else:
                skills = [s.strip() for s in skills_raw.split(";") if s.strip()]

            rank_raw = row.get("Rank", "").strip()
            if not rank_raw.isdigit():
                result.validation_errors.append(
                    ValidationError(f"Invalid rank: {rank_raw}", row_num)
                )
                continue
            rank = int(rank_raw)

            dist_diff_raw = row.get("Distance_Diff", "0").strip()
            try:
                distance_diff = float(dist_diff_raw)
            except ValueError:
                distance_diff = 0.0

            entry = RaceEntry(
                race_id=race_id,
                uma_name=uma_name,
                strategy=strategy,
                speed=int(stats["Speed"]),
                stamina=int(stats["Stamina"]),
                power=int(stats["Power"]),
                guts=int(stats["Guts"]),
                wisdom=int(stats["Wisdom"]),
                dist_s=parse_bool(row.get("Dist_S", "0")),
                surface_s=parse_bool(row.get("Surface_S", "0")),
                track_s=parse_bool(row.get("Track_S", "0")),
                skills_activated=skills,
                rank=rank,
                distance_diff=distance_diff,
            )
            result.entries.append(entry)

    return result
