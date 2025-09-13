"""
Taxonomy Adapter - Implementação para carregar taxonomia de algoritmos
"""

import json
from pathlib import Path
from typing import Dict, Any


class FileTaxonomyAdapter:
    """Adapter para carregar taxonomia de arquivo JSON"""

    def __init__(self):
        self.taxonomy_path = Path(__file__).parent.parent.parent / "data" / "taxonomy.json"
        self._taxonomy = None

    def load_taxonomy(self) -> Dict[str, Any]:
        """Load taxonomy from JSON file"""
        if self._taxonomy is None:
            try:
                with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
                    self._taxonomy = json.load(f)
            except FileNotFoundError:
                # Fallback taxonomy if file doesn't exist
                self._taxonomy = {
                    "categories": [
                        "Arrays", "Strings", "Hash Table", "Two Pointers", 
                        "Binary Search", "Sorting", "Greedy", "Dynamic Programming",
                        "Graph", "Tree", "Stack", "Queue", "Heap", "Backtracking"
                    ],
                    "difficulties": ["FACIL", "MEDIO", "DIFICIL"],
                    "algorithms": [
                        "Binary Search", "Two Pointers", "Hash Map", "Sliding Window",
                        "BFS", "DFS", "Dijkstra", "Union Find", "Topological Sort"
                    ]
                }
        return self._taxonomy

    def summarize_taxonomy_for_prompt(self) -> str:
        """Summarize taxonomy for LLM prompt"""
        taxonomy = self.load_taxonomy()
        
        categories = ", ".join(taxonomy.get("categories", []))
        algorithms = ", ".join(taxonomy.get("algorithms", []))
        difficulties = ", ".join(taxonomy.get("difficulties", []))
        
        return f"""
Categorias disponíveis: {categories}
Algoritmos comuns: {algorithms}
Níveis de dificuldade: {difficulties}
"""
