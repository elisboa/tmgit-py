# SESSION.md — Resumo de sessão tmgit-py

> Atualizado em: 2026-04-02
> Próxima sessão: feature/add-del-file (v0.3.0)

---

## Estado atual do projeto

> Nota: contexto revisto com base na documentação atualizada do guia modo-aviao (2026-04-02), enfatizando as quatro fases e contratos claros preflight, climb, fly, land (tag de referência: `modo-aviao@v1.2`).

### Versões
- `v0.1.0` — primeiro MVP funcional
- `v0.2.0` — suite completa de testes (45/45 passando)

### Branches
```
master    ← v0.2.0 — MVP com testes completos ✅
develop   ← alinhada com master
```

### Arquivos implementados
| Arquivo | Status |
|---|---|
| `land.py` | ✅ Completo + 10 testes |
| `preflight.py` | ✅ Completo + 14 testes |
| `climb.py` | ✅ Completo + 10 testes |
| `fly.py` | ✅ Completo + 11 testes |
| `main.py` | ✅ Completo |
| `tests/test_land.py` | ✅ 10/10 |
| `tests/test_preflight.py` | ✅ 14/14 |
| `tests/test_climb.py` | ✅ 10/10 |
| `tests/test_fly.py` | ✅ 11/11 |

### Suite de testes
```bash
uv run pytest tests/ -v
# 45 passed in 4.45s
```

---

## Próximas ações imediatas

### 1. Iniciar feature/add-del-file (v0.3.0)
```bash
git checkout develop
git checkout -b feature/add-del-file
```

### 2. Escrever especificações SDD no CONTEXT.md antes de codar

### 3. Implementar add-file e del-file
Mudanças necessárias:
- `preflight.py` — detectar argumentos extras:
  `context['command']` e `context['command_target']`
- `fly.py` — implementar `add_file()` e `del_file()`

### 4. Escrever testes para add-file e del-file

### 5. Merge na develop e master com tag v0.3.0

### 5. Feature: add-file e del-file (v0.2.0)
```bash
git checkout develop
git checkout -b feature/add-del-file
```

Implementar suporte aos comandos opcionais:
- `main.py /diretorio add-file /caminho/arquivo`
- `main.py /diretorio del-file /caminho/arquivo`

Mudanças necessárias:
- `preflight.py` — detectar argumentos extras e adicionar ao contexto:
  `context['command']` e `context['command_target']`
- `fly.py` — implementar `add_file()` e `del_file()` e executar
  antes do commit quando comando estiver no contexto

Especificações SDD a escrever no CONTEXT.md antes de codar.

---

## Setup do ambiente (caso precise reconfigurar)

```bash
# Modelos Ollama disponíveis
ollama list
# qwen2.5-coder:7b  → aider no terminal
# qwen2.5-coder:3b  → Continue.dev chat
# opencoder:1.5b    → Continue.dev autocomplete

# Iniciar aider na pasta do projeto
cd ~/git/github/elisboa/tmgit-py
aider

# Ativar ambiente virtual
source .venv/bin/activate

# Validar dependências
uv sync
uv run python -c "import git; print(git.__version__)"
```

---

## Como iniciar uma nova sessão no Claude

Cole este bloco no início da conversa:

```
Olá! Estou retomando o projeto tmgit-py, uma reescrita em Python de um
shell script que versiona seletivamente um diretório usando git (máquina
do tempo). O projeto segue o padrão arquitetural "modo-avião" com quatro
fases: preflight, climb, fly e land.

Você está atuando como Project Manager — decisões de arquitetura,
revisão de código gerado pelo Copilot e atualização do CONTEXT.md.
O Copilot Chat no VS Code cuida da geração técnica do código.

Estado atual: land.py completo e mergeado na develop. preflight.py
gerado mas com um ajuste pendente (ver SESSION.md no projeto).
Próximo passo: ajustar preflight.py, mergear na develop e iniciar climb.py.

Repositórios de referência:
- linux-time-machine.sh (original em shell)
- tmgit (reescrita em shell com padrão modo-avião)
- modo-aviao (guia de boas práticas)
- tmgit-py (projeto ativo em Python)
```

---

## Decisões arquiteturais tomadas

- Usar `gitpython` — nunca `subprocess` para git
- Funções principais nomeadas igual à fase: `land()`, `preflight()`, `climb()`, `fly()`
- Contexto passado entre fases via dicionário Python
- Sempre reutilizar variáveis de caminho já calculadas
- `copilot-instructions.md` é hardlink do `CONTEXT.md` — editar apenas o `CONTEXT.md`
- Git flow incremental: feature → develop → master
- Commits com emojis semânticos
- `[tool.uv] package = false` no pyproject.toml — projeto de scripts, não pacote
- **Metodologia SDD** — especificações DADO/QUANDO/ENTÃO escritas antes do código
- Testes pytest derivam das especificações e ficam em `tests/`
