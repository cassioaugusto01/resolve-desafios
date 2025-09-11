import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from .analyzer import Analyzer
from .config import get_settings
from .db import get_analysis, init_db, list_analyses, upsert_metadata
from .taxonomy import load_taxonomy, save_taxonomy


app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


@app.callback()
def _init() -> None:
    init_db()


@app.command()
def seed() -> None:
    """Popular/atualizar a taxonomia no banco e arquivo em data/taxonomy.json."""
    taxonomy = load_taxonomy()
    save_taxonomy(taxonomy)
    upsert_metadata("taxonomy", taxonomy)
    console.print("Taxonomia salva em [bold]data/taxonomy.json[/] e no banco de dados.")


def _read_input_text(file: Optional[Path], text_arg: Optional[str]) -> str:
    if file:
        return Path(file).read_text(encoding="utf-8")
    if text_arg:
        return text_arg
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise typer.BadParameter("Forneça --file, um texto direto, ou conteúdo via stdin.")


@app.command()
def analyze(
    title: str = typer.Option(..., "--title", help="Título curto do desafio"),
    text: Optional[str] = typer.Argument(None, help="Enunciado do desafio (ou use --file ou stdin)"),
    file: Optional[Path] = typer.Option(None, "--file", exists=True, file_okay=True, dir_okay=False, help="Caminho para arquivo com o enunciado"),
    objectives: Optional[str] = typer.Option(None, "--objectives", help="Objetivos/otimizações específicas"),
    constraints: Optional[str] = typer.Option(None, "--constraints", help="Restrições/limites do problema"),
) -> None:
    """Analisar um desafio, classificar e recomendar abordagem."""
    settings = get_settings()
    description = _read_input_text(file, text)

    console.rule("Analisando desafio")
    analyzer = Analyzer()
    result = analyzer.analyze(
        title=title,
        description=description,
        objectives=objectives,
        constraints=constraints,
        language=settings.app_language,
        persist=True,
    )

    table = Table(title="Resultado", box=box.SIMPLE)
    table.add_column("Campo", style="bold cyan", no_wrap=True)
    table.add_column("Valor", style="white")
    table.add_row("Título", result.get("title", title))
    table.add_row("Dificuldade", result.get("difficulty", "-"))
    table.add_row("Categorias", ", ".join(result.get("categories", [])))
    table.add_row("Resumo", result.get("summary", "-"))
    table.add_row("Abordagem Recomendada", result.get("recommended_approach", "-"))
    table.add_row("Complexidade (tempo)", result.get("complexity_time", "-"))
    table.add_row("Complexidade (espaço)", result.get("complexity_space", "-"))
    if result.get("assumptions"):
        table.add_row("Suposições", result.get("assumptions") or "-")
    if result.get("constraints"):
        table.add_row("Restrições", result.get("constraints") or "-")
    console.print(table)


@app.command()
def list(limit: int = typer.Option(10, "--limit", min=1, help="Quantidade de análises")) -> None:  # type: ignore[override]
    """Listar análises mais recentes."""
    rows = list_analyses(limit)
    if not rows:
        console.print("Nenhuma análise encontrada.")
        return
    table = Table(title="Análises", box=box.SIMPLE)
    table.add_column("ID")
    table.add_column("Desafio")
    table.add_column("Dificuldade")
    table.add_column("Categorias")
    table.add_column("Criado em")
    for r in rows:
        table.add_row(
            str(r["analysis_id"]),
            r.get("title", "-"),
            r.get("difficulty", "-"),
            ", ".join(r.get("categories", []) or []),
            r.get("created_at", "-"),
        )
    console.print(table)


@app.command()
def show(analysis_id: int) -> None:
    """Exibir detalhes de uma análise."""
    row = get_analysis(analysis_id)
    if not row:
        console.print(f"Análise {analysis_id} não encontrada.")
        raise typer.Exit(code=1)

    console.rule(f"Análise #{analysis_id}")
    console.print_json(data=row)


@app.command()
def export(id: int = typer.Option(..., "--id"), out: Path = typer.Option(..., "--out")) -> None:
    """Exportar análise para JSON."""
    row = get_analysis(id)
    if not row:
        console.print(f"Análise {id} não encontrada.")
        raise typer.Exit(code=1)
    out.parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f"Exportado para [bold]{out}[/]")


