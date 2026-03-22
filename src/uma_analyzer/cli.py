from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from uma_analyzer.analyzer import Analyzer
from uma_analyzer.parser import parse_csv

app = typer.Typer()
console = Console()


@app.command()
def analyze(
    input: Path = typer.Option(..., "--input", "-i", help="Path to CSV file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show all warnings"),
) -> None:
    if not input.exists():
        console.print(f"[red]Error: File not found: {input}[/red]")
        raise typer.Exit(1)

    result = parse_csv(input)

    if result.validation_errors:
        console.print("[red]Validation Errors:[/red]")
        for error in result.validation_errors:
            location = f" (row {error.row})" if error.row else ""
            console.print(f"  [red]•[/red] {error.message}{location}")
        if not result.entries:
            raise typer.Exit(1)

    if result.duplicate_race_ids:
        console.print(
            f"[yellow]Warning: Found {len(result.duplicate_race_ids)} duplicate Race_IDs[/yellow]"
        )
        if verbose:
            console.print(f"  Duplicate IDs: {result.duplicate_race_ids}")

    if result.missing_skill_warnings and verbose:
        console.print("[yellow]Missing Skill Warnings:[/yellow]")
        for warning in result.missing_skill_warnings[:10]:
            console.print(f"  [yellow]•[/yellow] {warning}")
        if len(result.missing_skill_warnings) > 10:
            console.print(
                f"  [yellow]... and {len(result.missing_skill_warnings) - 10} more[/yellow]"
            )

    console.print(f"\n[green]Loaded {len(result.entries)} race entries[/green]")

    analyzer = Analyzer(result.entries)

    console.print("\n[bold cyan]=== Strategy Performance ===[/bold cyan]")
    strategy_stats = analyzer.calculate_strategy_stats()
    strategy_table = Table()
    strategy_table.add_column("Strategy")
    strategy_table.add_column("Count", justify="right")
    strategy_table.add_column("Avg Rank", justify="right")
    strategy_table.add_column("Top 3 Rate", justify="right")

    for stat in strategy_stats:
        strategy_table.add_row(
            stat.strategy.name.replace("_", " ").title(),
            str(stat.count),
            f"{stat.avg_rank:.2f}",
            f"{stat.top3_rate * 100:.1f}%",
        )
    console.print(strategy_table)

    console.print("\n[bold cyan]=== Stat Correlations (Pearson) ===[/bold cyan]")
    stat_corrs = analyzer.calculate_stat_correlations()
    corr_table = Table()
    corr_table.add_column("Stat", style="cyan")
    corr_table.add_column("Correlation", justify="right")

    for sc in stat_corrs:
        color = "green" if sc.correlation < 0 else "red"
        corr_table.add_row(sc.stat, f"[{color}]{sc.correlation:.3f}[/{color}]")
    console.print(corr_table)

    console.print("\n[bold cyan]=== Skill Impact Score (Top 10) ===[/bold cyan]")
    skill_impacts = analyzer.calculate_skill_impacts()
    skill_table = Table()
    skill_table.add_column("Skill", style="magenta")
    skill_table.add_column("Appearances", justify="right")
    skill_table.add_column("Avg Rank (With)", justify="right")
    skill_table.add_column("SIS", justify="right")

    for si in skill_impacts[:10]:
        sis_color = "green" if si.sis > 0 else "red"
        skill_table.add_row(
            si.name,
            str(si.appearances),
            f"{si.avg_rank_with:.2f}",
            f"[{sis_color}]{si.sis:.3f}[/{sis_color}]",
        )
    console.print(skill_table)

    if len(skill_impacts) > 10:
        console.print(f"[dim]... and {len(skill_impacts) - 10} more skills[/dim]")

    trap_skills = [si for si in skill_impacts if si.sis < -0.1]
    if trap_skills:
        console.print("\n[bold red]=== Potential Trap Skills (Negative SIS) ===[/bold red]")
        for si in trap_skills[:5]:
            console.print(
                f"  [red]•[/red] {si.name}: SIS={si.sis:.3f} (may waste SP)"
            )

    envelope = analyzer.calculate_success_envelope()
    console.print("\n[bold cyan]=== Success Envelope ===[/bold cyan]")
    console.print(
        f"  Min Speed for Top 3: [green]{envelope.min_speed_top3}[/green]"
    )
    console.print(
        f"  Avg Stamina for Finishers: [green]{envelope.avg_stamina_finishers:.0f} "
        f"± {envelope.stamina_std:.0f}[/green]"
    )


def main() -> None:
    app()
