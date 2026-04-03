# SESSION.md — Resumo de sessão tmgit-py

> Atualizado em: 2026-04-03
> Próxima sessão: uso real no $HOME ou nova feature

---

## Estado atual do projeto

### Histórico de versões

| Tag | O que representa |
|---|---|
| `v0.1.0` | Primeiro MVP funcional — quatro fases implementadas |
| `v0.2.0` | Suite completa de testes — 45/45 passando |
| `v0.2.1` | Fix docs — CONTEXT.md substituído por copilot-instructions.md |
| `v0.3.0` | Fix docs — referência ao modo-aviao@v1.2 (criado no MacBook Air) |
| `v0.3.1` | Fix docs — corrige referências e histórico de versões |
| `v0.4.0` | Feature — add-file e del-file implementados |
| `v0.4.1` | Qualidade — cobertura de testes 100%, 68 testes |
| `v0.5.0` | Arquitetura — exceções customizadas, main como piloto único |

> **Nota:** `v0.3.0` e `v0.2.1` estão fora de ordem semântica — aprendizado de git flow.

### Branches
```
master    ← v0.5.0 ✅
develop   ← alinhada com master
```

### Arquivos implementados
| Arquivo | Cobertura | Testes |
|---|---|---|
| `exceptions.py` | 100% | — |
| `land.py` | 100% | 10/10 |
| `preflight.py` | 100% | 20/20 |
| `climb.py` | 100% | 11/11 |
| `fly.py` | 100% | 24/24 |
| `main.py` | 100% | 4/4 |

### Suite de testes
```bash
uv run pytest tests/ --cov=. --cov-report=term-missing
# 69 passed — 100% coverage
```

---

## Arquitetura atual (v0.5.0)

```
main.py (piloto)
├── try:
│   ├── context = preflight()   → lança PreflightError em erro
│   ├── context = climb(context) → lança ClimbError em erro
│   ├── context = fly(context)   → lança FlyError em erro
│   └── land(0, ...)             → pouso bem-sucedido
└── except TmgitError as e:
    └── land(1, e.caller, e.message, e.error_message)  → pouso de emergência
```

Todas as exceções herdam de `TmgitError(Exception)` definida em `exceptions.py`.

---

## Próximas ações imediatas

### 1. Uso real no $HOME
```bash
mkdir -p ~
uv run python ~/git/github/elisboa/tmgit-py/main.py ~
uv run python ~/git/github/elisboa/tmgit-py/main.py ~ add-file .zshrc
uv run python ~/git/github/elisboa/tmgit-py/main.py ~ add-file .gitconfig

# Via cron (a cada hora)
0 * * * * cd ~/git/github/elisboa/tmgit-py && uv run python main.py ~
```

### 2. Possíveis próximas features (v0.6.0)
- `--version` flag para exibir versão atual
- Modo `version-all` — versionar todos os arquivos do diretório
- Arquivo de configuração `.tmgit.conf`
- Suporte a múltiplos diretórios em uma única chamada

---

## Setup do ambiente (caso precise reconfigurar)

```bash
git clone https://github.com/elisboa/tmgit-py
cd tmgit-py
uv sync
uv run pytest tests/ --cov=. --cov-report=term-missing
# Esperado: 69 passed, 100% coverage

ollama pull qwen2.5-coder:7b   # aider no terminal
ollama pull qwen2.5-coder:3b   # Continue.dev chat
ollama pull opencoder:1.5b     # Continue.dev autocomplete

aider .github/copilot-instructions.md SESSION.md
```

---

## Como iniciar uma nova sessão no Claude

```
Olá! Estou retomando o projeto tmgit-py, uma reescrita em Python de um
shell script que versiona seletivamente um diretório usando git (máquina
do tempo). O projeto segue o padrão arquitetural "modo-avião" com quatro
fases: preflight, climb, fly e land.

Você está atuando como Project Manager — decisões de arquitetura,
revisão de código gerado pelo Copilot e atualização do
.github/copilot-instructions.md. O Copilot Chat no VS Code cuida da
geração técnica do código.

Estado atual: v0.5.0 — 69 testes, 100% cobertura, exceções customizadas,
main como piloto único do fluxo.
Próximo passo: uso real no $HOME ou nova feature.

Repositórios de referência:
- linux-time-machine.sh (original em shell)
- tmgit (reescrita em shell com padrão modo-avião)
- modo-aviao (guia de boas práticas, tag modo-aviao@v1.2)
- tmgit-py (projeto ativo em Python)
```

---

## Decisões arquiteturais tomadas

- Usar `gitpython` — nunca `subprocess` para git
- Funções principais nomeadas igual à fase: `land()`, `preflight()`, `climb()`, `fly()`
- Contexto passado entre fases via dicionário Python
- Sempre reutilizar variáveis de caminho já calculadas
- Documentação unificada em `.github/copilot-instructions.md`
- Git flow incremental: feature → develop → master
- Merge commits com `--no-ff` e emoji `:twisted_rightwards_arrows:`
- Commits com emojis semânticos
- `[tool.uv] package = false` no pyproject.toml
- **Metodologia SDD** — especificações DADO/QUANDO/ENTÃO antes do código
- Testes pytest derivam das especificações e ficam em `tests/`
- **Fluxo sempre completo:** `preflight → climb → fly → land`
- O `fly()` decide qual operação executar via `context['command']`
- **Versionamento:** MAJOR.MINOR.PATCH
- `del_file()` verifica rastreamento no index, não existência no disco
- `if __name__ == "__main__":` excluído da cobertura via `pyproject.toml`
- Atributos read-only do gitpython testados via `unittest.mock.MagicMock`
- **Exceções customizadas:** cada fase lança sua exceção (`PreflightError`,
  `ClimbError`, `FlyError`), todas herdando de `TmgitError`
- **main.py é o piloto único:** único ponto que chama `land()`, captura
  `TmgitError` e decide o pouso
