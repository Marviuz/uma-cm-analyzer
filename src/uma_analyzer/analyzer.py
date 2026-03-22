from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, variance

from uma_analyzer.models import RaceEntry, Strategy


@dataclass
class SkillImpact:
    name: str
    appearances: int
    avg_rank_with: float
    avg_rank_without: float
    sis: float


@dataclass
class StatCorrelation:
    stat: str
    correlation: float
    p_value: float | None


@dataclass
class StrategyStats:
    strategy: Strategy
    count: int
    avg_rank: float
    top3_rate: float


@dataclass
class SuccessEnvelope:
    min_speed_top3: float
    avg_stamina_finishers: float
    stamina_std: float


class Analyzer:
    def __init__(self, entries: list[RaceEntry]) -> None:
        self.entries = entries

    def calculate_skill_impacts(self) -> list[SkillImpact]:
        skill_ranks_with: dict[str, list[int]] = {}
        skill_ranks_without: dict[str, list[int]] = {}
        all_skills: set[str] = set()

        for entry in self.entries:
            for skill in entry.skills_activated:
                all_skills.add(skill)
                skill_ranks_with.setdefault(skill, []).append(entry.rank)

        for skill in all_skills:
            ranks_without = [
                e.rank for e in self.entries if skill not in e.skills_activated
            ]
            skill_ranks_without[skill] = ranks_without

        impacts = []
        for skill in all_skills:
            ranks_with = skill_ranks_with.get(skill, [])
            ranks_without = skill_ranks_without.get(skill, [])

            if not ranks_with or not ranks_without:
                continue

            avg_with = mean(ranks_with)
            avg_without = mean(ranks_without)
            variance_with = variance(ranks_with) if len(ranks_with) > 1 else 1.0

            sis = (avg_without - avg_with) / variance_with

            impacts.append(
                SkillImpact(
                    name=skill,
                    appearances=len(ranks_with),
                    avg_rank_with=avg_with,
                    avg_rank_without=avg_without,
                    sis=sis,
                )
            )

        return sorted(impacts, key=lambda x: x.sis, reverse=True)

    def calculate_stat_correlations(self) -> list[StatCorrelation]:
        stats = ["Speed", "Stamina", "Power", "Guts", "Wisdom"]
        correlations = []

        for stat in stats:
            stat_values = [getattr(e, stat.lower()) for e in self.entries]
            rank_values = [e.rank for e in self.entries]

            corr = self._pearson_correlation(stat_values, rank_values)
            correlations.append(
                StatCorrelation(stat=stat, correlation=corr, p_value=None)
            )

        return correlations

    def _pearson_correlation(self, x: list[int], y: list[int]) -> float:
        n = len(x)
        if n < 2:
            return 0.0

        mean_x = mean(x)
        mean_y = mean(y)

        numerator = sum(float(xi - mean_x) * float(yi - mean_y) for xi, yi in zip(x, y))
        sum_sq_x = sum(float(xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum(float(yi - mean_y) ** 2 for yi in y)

        denominator = (sum_sq_x * sum_sq_y) ** 0.5

        if denominator == 0:
            return 0.0

        return float(numerator / denominator)

    def calculate_strategy_stats(self) -> list[StrategyStats]:
        strategy_data: dict[Strategy, list[int]] = {s: [] for s in Strategy}

        for entry in self.entries:
            strategy_data[entry.strategy].append(entry.rank)

        stats = []
        for strategy in Strategy:
            ranks = strategy_data[strategy]
            if not ranks:
                continue

            count = len(ranks)
            avg_rank = mean(ranks)
            top3_count = sum(1 for r in ranks if r <= 3)
            top3_rate = top3_count / count

            stats.append(
                StrategyStats(
                    strategy=strategy,
                    count=count,
                    avg_rank=avg_rank,
                    top3_rate=top3_rate,
                )
            )

        return sorted(stats, key=lambda x: x.top3_rate, reverse=True)

    def calculate_success_envelope(self) -> SuccessEnvelope:
        top3_entries = [e for e in self.entries if e.rank <= 3]
        finisher_entries = [e for e in self.entries if e.rank <= 5]

        min_speed_top3 = (
            min(e.speed for e in top3_entries) if top3_entries else 0
        )

        if finisher_entries:
            stamina_values = [e.stamina for e in finisher_entries]
            avg_stamina: float = mean(stamina_values)
            stamina_std = (variance(stamina_values) ** 0.5) if len(stamina_values) > 1 else 0.0
        else:
            avg_stamina = 0.0
            stamina_std = 0.0

        return SuccessEnvelope(
            min_speed_top3=min_speed_top3,
            avg_stamina_finishers=avg_stamina,
            stamina_std=stamina_std,
        )

    def get_meta_analysis(self) -> dict[str, Strategy]:
        strategy_stats = self.calculate_strategy_stats()
        if not strategy_stats:
            return {}

        winning_strategy = strategy_stats[0].strategy
        return {"overperforming": winning_strategy}
