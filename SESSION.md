# SESSION.md — Resumo de sessão tmgit-py

> Atualizado em: 2026-03-28
> Próxima sessão: continuar a partir da feature/preflight-py

---

## Estado atual do projeto

### Branches
```
master    ← estável, 4 commits
develop   ← alinhada com master + feature/land-py mergeada
feature/preflight-py ← branch ativa, preflight.py pendente de ajuste e commit
```

### Arquivos implementados
| Arquivo | Status | Branch de origem |
|---|---|---|
| `land.py` | ✅ Completo, mergeado na develop | feature/land-py |
| `preflight.py` | ⚠️ Gerado, aguarda ajuste e commit | feature/preflight-py |
| `climb.py` | ❌ Não iniciado | — |
| `fly.py` | ❌ Não iniciado | — |
| `main.py` | ⚠️ Mínimo (só print), precisa orquestrar as fases | — |

---

## Próximas ações imediatas

### 1. Ajustar preflight.py (pendente)
Levar este prompt ao Copilot Chat:

```
No preflight.py, ajuste a construção do caminho do lock_file para usar
a variável tmgit_dir já calculada, em vez de reconstruir o caminho completo:

# Antes
lock_file = os.path.join(tmgit_tree, '.tmgit', '.git', 'index.lock')

# Depois
lock_file = os.path.join(tmgit_dir, 'index.lock')

Motivo: tmgit_dir já contém o caminho completo até .tmgit/.git — reusá-lo
garante consistência. Se tmgit_dir mudar no futuro, lock_file acompanha
automaticamente sem precisar de outra alteração.
```

Após o ajuste:
```bash
git add preflight.py CONTEXT.md
git commit -m ":sparkles: Implementa fase preflight e atualiza CONTEXT.md"
git push origin feature/preflight-py
```

### 2. Merge da feature/preflight-py na develop
```bash
git checkout develop
git merge feature/preflight-py
git push origin develop
```

### 3. Criar feature/climb-py
```bash
git checkout -b feature/climb-py
```

Prompt sugerido para o Copilot:
```
Crie o arquivo climb.py para o projeto tmgit-py seguindo o padrão modo-avião.

Este arquivo é a fase 2 — preparação do ambiente (climbing). Responsabilidades:
- A função principal deve se chamar climb()
- Receber o dicionário de contexto retornado pelo preflight()
- Verificar se o repositório já existe (tmgit_dir)
- Se não existir, criar o diretório e inicializar com git init
- Verificar e criar o .gitignore com * como conteúdo padrão
- Verificar e criar/trocar para a branch do dia (branch_name)
- Em caso de erro, chamar land() importado de land.py
- Retornar o dicionário de contexto atualizado

Usar gitpython para todas as operações git — nunca subprocess.
Comentários em português, nomes de variáveis e funções em inglês.
Seguir a mesma estrutura do fm_climb.sh do projeto tmgit em shell.
```

### 4. Criar feature/fly-py (após climb)
```bash
git checkout -b feature/fly-py
```

### 5. Atualizar main.py (após todas as fases)
O `main.py` atual tem apenas um print. Precisará importar e orquestrar:
```python
from preflight import preflight
from climb import climb
from fly import fly
from land import land

def main():
    context = preflight()
    context = climb(context)
    fly(context)

if __name__ == "__main__":
    main()
```

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
<<<<<<< HEAD
=======
- **Metodologia SDD** — especificações DADO/QUANDO/ENTÃO escritas antes do código
- Testes pytest derivam das especificações e ficam em `tests/`
>>>>>>> ac533e1 (:memo: Adiciona metodologia SDD e especificações ao CONTEXT.md)
