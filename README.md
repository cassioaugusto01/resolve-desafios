## Resolve Desafios (CLI)

Aplicação em Python (CLI) para ajudar estudantes e desenvolvedores a se prepararem para desafios de algoritmos e estruturas de dados em entrevistas técnicas e competições de programação.

- **Objetivo**: Classificar desafios por categoria e dificuldade, listar abordagens possíveis e recomendar a(s) mais eficiente(s) conforme objetivos e restrições do problema.
- **Métrica de eficiência**: análise assintótica usando notação Big O.
- **IA**: LLMs via OpenAI API orquestrados com LangChain.
- **Base de conhecimento**: taxonomia de categorias/algoritmos baseada em McDowell (2015, 2025), Halim (2020), Skiena (2020), EPI e fontes online (LeetCode/competitions).
- **Persistência**: SQLite.
- **Idioma**: PT-BR (aceita enunciados em português; textos de saída são em PT-BR).

### Requisitos

- Python 3.10+
- `pip` e acesso à internet
- Uma chave de API da OpenAI (`OPENAI_API_KEY`)

### Instalação

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edite .env e defina OPENAI_API_KEY
```

### Executando

Formas de uso (após ativar o ambiente):

```bash
# 1) Passando o enunciado diretamente
python app.py analyze --title "Two Sum" --lang pt "Dado um array de inteiros, ..."

# 2) Lendo de um arquivo
python app.py analyze --title "Anagramas" --file exemplos/anagrama.txt

# 3) Lendo do stdin (Ctrl+D para finalizar)
cat exemplos/two_sum.txt | python app.py analyze --title "Two Sum"

# Listar análises gravadas
python app.py list --limit 10

# Ver detalhe de uma análise
python app.py show 1

# Exportar para JSON
python app.py export --id 1 --out export/analysis_1.json

# Popular/atualizar a taxonomia no banco
python app.py seed
```

### Estrutura (resumo)

```
data/
  taxonomy.json
src/
  resolve_desafios/
    cli.py           # CLI Typer
    analyzer.py      # Orquestração da análise
    llm_chain.py     # Cadeia LangChain + OpenAI
    taxonomy.py      # Leitura/uso da taxonomia
    schemas.py       # Modelos Pydantic
    db.py            # Persistência SQLite
    config.py        # Configuração e .env
app.py               # Entrada da CLI
```

### Banco de Dados

- Arquivo SQLite padrão: `data/resolve_desafios.db` (configurável via `RESOLVE_DB_PATH`).
- Tabelas principais: `challenges`, `analyses` e `metadata` (taxonomia e outras informações de suporte).

### Fontes e Referências

- McDowell, G. L. (2015, 2025). Cracking the Coding Interview.
- Halim, S.; Halim, F. (2020). Competitive Programming 4.
- Skiena, S. (2020). The Algorithm Design Manual.
- Aziz, A.; Prakash, A.; Lee, T. (EPI). Elements of Programming Interviews.
- Repositórios e juízes online de competições (incl. LeetCode) para taxonomia e benchmarking.

### Observações

- A saída é sempre em PT-BR e inclui classiﬁcação, análise Big O e recomendação.
- A qualidade pode variar conforme clareza do enunciado e restrições fornecidas.
- Este projeto usa a API da OpenAI; custos podem ser incorridos pelo uso.


