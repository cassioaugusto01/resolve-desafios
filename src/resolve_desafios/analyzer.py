import json
from dataclasses import asdict
from typing import Any, Dict, Optional

from . import __version__
from .config import get_settings
from .db import insert_analysis, insert_challenge
from .llm_chain import run_structured_analysis
from .schemas import AnalysisOutput
from .taxonomy import load_taxonomy, summarize_taxonomy_for_prompt


class Analyzer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.taxonomy = load_taxonomy()
        self.taxonomy_summary = summarize_taxonomy_for_prompt(self.taxonomy)

    def analyze(
        self,
        *,
        title: str,
        description: str,
        objectives: Optional[str] = None,
        constraints: Optional[str] = None,
        language: str = "pt-BR",
        persist: bool = True,
    ) -> Dict[str, Any]:
        structured: AnalysisOutput = run_structured_analysis(
            title=title,
            description=description,
            objectives=objectives or "",
            constraints=constraints or "",
            taxonomy_summary=self.taxonomy_summary,
        )

        result_json: Dict[str, Any] = json.loads(structured.model_dump_json())

        if persist:
            challenge_id = insert_challenge(
                title=title,
                description=description,
                objectives=objectives,
                constraints=constraints,
                language=language,
            )
            insert_analysis(
                challenge_id=challenge_id,
                difficulty=structured.difficulty.value,
                categories=structured.categories,
                summary=structured.summary,
                recommended_approach=structured.recommended_approach,
                approaches=[json.loads(a.model_dump_json()) for a in structured.approaches],
                complexity_time=structured.complexity_time,
                complexity_space=structured.complexity_space,
                assumptions=structured.assumptions,
                references=structured.references,
                model=self.settings.openai_model,
                raw=result_json,
            )

        return result_json


