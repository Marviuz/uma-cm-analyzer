from dataclasses import dataclass
from enum import Enum


class Strategy(Enum):
    FRONT_RUNNER = 1
    PACE_CHASER = 2
    LATE_SURGER = 3
    END_CLOSER = 4

    @classmethod
    def from_string(cls, value: str) -> "Strategy":
        normalized = value.lower().replace("-", "_").replace(" ", "_")
        mapping = {
            "front_runner": cls.FRONT_RUNNER,
            "pace_chaser": cls.PACE_CHASER,
            "late_surger": cls.LATE_SURGER,
            "end_closer": cls.END_CLOSER,
        }
        if normalized in mapping:
            return mapping[normalized]
        if value.isdigit():
            num = int(value)
            if 1 <= num <= 4:
                return cls(num)
        raise ValueError(f"Invalid strategy: {value}")


@dataclass
class RaceEntry:
    race_id: str
    uma_name: str
    strategy: Strategy
    speed: int
    stamina: int
    power: int
    guts: int
    wisdom: int
    dist_s: bool
    surface_s: bool
    track_s: bool
    skills_activated: list[str]
    rank: int
    distance_diff: float

    @property
    def has_s_aptitude(self) -> bool:
        return self.dist_s or self.surface_s or self.track_s

    @property
    def total_stats(self) -> int:
        return self.speed + self.stamina + self.power + self.guts + self.wisdom
