import json
from pathlib import Path
from typing import Dict, List

from .config import get_settings


TAXONOMY_META_KEY = "taxonomy"


def _default_taxonomy() -> Dict:
    # Resumo inspirado em: McDowell, Halim, Skiena, EPI, LeetCode.
    return {
        "categories": {
            "Arrays": [
                "Dois ponteiros",
                "Janela deslizante",
                "Prefix sums",
                "Busca binária em resposta",
            ],
            "Strings": [
                "Hashing",
                "Anagramas",
                "KMP",
                "Rabin-Karp",
                "Trie",
            ],
            "Listas Ligadas": [
                "Dois ponteiros (lento/rápido)",
                "Inversão",
                "Detecção de ciclo",
            ],
            "Pilhas e Filas": [
                "Monotonic stack",
                "Deque / BFS",
            ],
            "Árvores": [
                "DFS/Pre/In/Post",
                "BFS",
                "BST",
                "LCA",
                "Segment Tree/Fenwick",
            ],
            "Grafos": [
                "DFS/BFS",
                "Topological sort",
                "Dijkstra",
                "Bellman-Ford",
                "Floyd-Warshall",
                "MST (Kruskal/Prim)",
                "Union-Find",
            ],
            "Programação Dinâmica": [
                "Knapsack",
                "LIS",
                "LCS",
                "Coin Change",
                "Edit Distance",
            ],
            "Guloso": [
                "Interval scheduling",
                "Huffman",
            ],
            "Ordenação e Busca": [
                "Quicksort/Mergesort",
                "Counting/Radix",
                "Busca Binária",
            ],
            "Bitmask": [
                "Bit DP",
                "Manipulação de bits",
            ],
            "Matemática/Teoria dos Números": [
                "Crivo de Eratóstenes",
                "MDC/Mínimo Comum Múltiplo",
                "Exponenciação rápida",
                "Combinatória",
            ],
            "Geometria Computacional": [
                "Produto vetorial",
                "Convex Hull",
                "Varredura linear",
            ],
            "Backtracking": [
                "Permutações/Combinações",
                "N-Queens",
                "Subconjuntos",
            ],
        }
    }


def taxonomy_path() -> Path:
    settings = get_settings()
    # Armazenamos em data/taxonomy.json por padrão
    return settings.db_path.parent / "taxonomy.json"


def load_taxonomy() -> Dict:
    path = taxonomy_path()
    if not path.exists():
        return _default_taxonomy()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _default_taxonomy()


def save_taxonomy(taxonomy: Dict) -> None:
    path = taxonomy_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(taxonomy, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_taxonomy_for_prompt(taxonomy: Dict) -> str:
    lines: List[str] = []
    for cat, algos in taxonomy.get("categories", {}).items():
        lines.append(f"- {cat}: {', '.join(algos)}")
    return "\n".join(lines)


