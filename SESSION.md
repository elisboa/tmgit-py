# SESSION.md — Resumo de sessão tmgit-py

> Atualizado em: 2026-04-03
> Próxima sessão: feature/add-del-file → tag v0.4.0

---

## Estado atual do projeto

### Histórico de versões

| Tag | O que representa |
|---|---|
| `v0.1.0` | Primeiro MVP funcional — quatro fases implementadas |
| `v0.2.0` | Suite completa de testes — 45/45 passando |
| `v0.2.1` | Fix docs — CONTEXT.md substituído por copilot-instructions.md |
| `v0.3.0` | Fix docs — referência ao modo-aviao@v1.2 (criado no MacBook Air) |

> **Nota:** `v0.3.0` e `v0.2.1` estão fora de ordem semântica no histórico git — o `v0.3.0` foi criado antes do `v0.2.1`. Isso é um aprendizado de git flow: não reescrever tags já publicadas no remoto. A próxima feature real recebe `v0.4.0`.

### Branches
```
master    ← v0.2.1 mais recente no histórico linear
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

### 1. Iniciar feature/add-del-file (→ v0.4.0)
```bash
git checkout develop
git checkout -b feature/add-del-file
```

### 2. Escrever especificações SDD antes de codar

As especificações já estão em `.github/copilot-instructions.md` na seção `add_file() e del_file()`. Revisar com o Claude antes de gerar o prompt para o Copilot.

### 3. Implementar add-file e del-file

Mudanças necessárias em dois arquivos:

**`preflight.py`** — detectar argumentos extras:
```python
context['command'] = args[1] if len(args) > 1 else None
context['command_target'] = args[2] if len(args) > 2 else None
```

**`fly.py`** — implementar e chamar antes do commit:
```python
def add_file(repo, filepath): ...
def del_file(repo, filepath): ...
```

### 4. Escrever testes para add-file e del-file

Derivar de especificações DADO/QUANDO/ENTÃO já documentadas.

### 5. Merge na develop e master com tag v0.4.0

```bash
git checkout develop
git merge feature/add-del-file
git checkout master
git merge develop
git tag -a v0.4.0 -m ":label: Implementa add-file e del-file"
git push origin master --follow-tags
```

---

## Setup do ambiente (caso precise reconfigurar)

```bash
# Clonar e instalar
git clone https://github.com/elisboa/tmgit-py
cd tmgit-py
uv sync

# Validar
uv run pytest tests/ -v

# Modelos Ollama
ollama pull qwen2.5-coder:7b   # aider no terminal
ollama pull qwen2.5-coder:3b   # Continue.dev chat
ollama pull opencoder:1.5b     # Continue.dev autocomplete

# Iniciar aider com contexto do projeto
cd ~/git/github/elisboa/tmgit-py
aider .github/copilot-instructions.md SESSION.md
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
revisão de código gerado pelo Copilot e atualização do
.github/copilot-instructions.md. O Copilot Chat no VS Code cuida da
geração técnica do código.

Estado atual: MVP v0.2.0 funcional com 45 testes passando.
Documentação unificada em .github/copilot-instructions.md (v0.2.1/v0.3.0).
Próximo passo: feature/add-del-file → tag v0.4.0.

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
- Documentação unificada em `.github/copilot-instructions.md` — não existe mais `CONTEXT.md`
- Git flow incremental: feature → develop → master
- Commits com emojis semânticos
- `[tool.uv] package = false` no pyproject.toml — projeto de scripts, não pacote
- **Metodologia SDD** — especificações DADO/QUANDO/ENTÃO escritas antes do código
- Testes pytest derivam das especificações e ficam em `tests/`
- **Fluxo sempre completo:** as quatro fases `preflight → climb → fly → land` são sempre executadas em ordem, sem desvio. O `fly()` decide internamente qual operação executar via `context['command']` — nunca desviar o fluxo antes do `fly()`
- **Versionamento:** MAJOR.MINOR.PATCH — MINOR para nova feature, PATCH para fix/doc
- **Próxima tag:** `v0.4.0` para a feature add-file/del-file
