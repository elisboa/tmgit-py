# SESSION.md — Resumo de sessão tmgit-py

> Atualizado em: 2026-04-02
> Próxima sessão: feature/tests ou feature/add-del-file

---

## Estado atual do projeto

### Branches
```
master    ← v0.1.0 — primeiro MVP funcional ✅
develop   ← alinhada com master
```

### Arquivos implementados
| Arquivo | Status | Branch de origem |
|---|---|---|
| `land.py` | ✅ Completo | feature/land-py |
| `preflight.py` | ✅ Completo | feature/preflight-py |
| `climb.py` | ✅ Completo | feature/climb-py |
| `fly.py` | ✅ Completo | feature/fly-py |
| `main.py` | ✅ Completo | feature/main-py |

### MVP validado
Teste de integração executado com sucesso:
```bash
uv run python main.py /tmp/teste-tmgit
# Saída:
# Iniciando aterrissagem chamada por fly
# Encerramento: Fly concluído com sucesso
# Codigo de erro: 0
```
Repositório criado corretamente em `/tmp/teste-tmgit`:
- `.git` — ponteiro para separate_git_dir
- `.tmgit/.git` — repositório git real
- `.gitignore` com `*`

---

## Próximas ações imediatas

### 1. Commitar e mergear main.py
```bash
cp ~/Downloads/SESSION.md ~/git/github/elisboa/tmgit-py/SESSION.md
git add main.py SESSION.md
git commit -m ":sparkles: Implementa main.py orquestrando as quatro fases"
git push origin feature/main-py
git checkout develop
git merge feature/main-py
git push origin develop
```

### 2. Teste de integração básico
Após o merge, testar o fluxo completo com um diretório temporário:
```bash
mkdir -p /tmp/teste-tmgit
uv run python main.py /tmp/teste-tmgit
```

### 3. Merge da develop na master (primeiro MVP)
Se o teste passar:
```bash
git checkout master
git merge develop
git tag -a v0.1.0 -m ":label: Primeiro MVP funcional"
git push origin master --follow-tags
```

### 4. Criar pasta tests/ e escrever testes pytest
Derivar testes das especificações DADO/QUANDO/ENTÃO do CONTEXT.md:
```bash
git checkout develop
git checkout -b feature/tests
mkdir tests
```

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
