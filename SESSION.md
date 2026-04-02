# SESSION.md — Resumo de sessão tmgit-py

> Atualizado em: 2026-03-28
> Próxima sessão: iniciar feature/climb-py

---

## Estado atual do projeto

### Branches
```
master    ← estável, 4 commits
develop   ← feature/land-py e feature/preflight-py mergeadas
feature/climb-py ← próxima a criar
```

### Arquivos implementados
| Arquivo | Status | Branch de origem |
|---|---|---|
| `land.py` | ✅ Completo, mergeado na develop | feature/land-py |
| `preflight.py` | ✅ Completo, mergeado na develop | feature/preflight-py |
| `climb.py` | ✅ Completo, aguarda commit e merge | feature/climb-py |
| `fly.py` | ✅ Completo, aguarda commit e merge | feature/fly-py |
| `main.py` | ⚠️ Mínimo (só print), precisa orquestrar as fases | — |

---

## Próximas ações imediatas

### 1. Commitar e mergear fly.py
```bash
cp ~/Downloads/SESSION.md ~/git/github/elisboa/tmgit-py/SESSION.md
git add fly.py SESSION.md
git commit -m ":sparkles: Implementa fase fly (commit, tag, push)"
git push origin feature/fly-py
git checkout develop
git merge feature/fly-py
git push origin develop
```

### 2. Atualizar main.py
```bash
git checkout -b feature/main-py
```

O `main.py` atual tem apenas um print. Precisará importar e orquestrar:
```python
from preflight import preflight
from climb import climb
from fly import fly
from land import land

def main():
    context = preflight()
    context = climb(context)
    context = fly(context)
    land(context['land_errlvl'], context['land_caller'],
         context['land_msg'], context['land_errmsg'])

if __name__ == "__main__":
    main()
```

### 3. Teste de integração básico
Após o main.py, testar o fluxo completo:
```bash
uv run python tmgit.py ~/tmp/teste-tmgit
```

### 4. Criar pasta tests/ e escrever testes pytest
Derivar testes das especificações DADO/QUANDO/ENTÃO do CONTEXT.md.

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
