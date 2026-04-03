# SESSION.md — Resumo de sessão tmgit-py

> Atualizado em: 2026-04-03
> Próxima sessão: feature/tests-preflight-commands ou feature/integration-test

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

> **Nota:** `v0.3.0` e `v0.2.1` estão fora de ordem semântica — aprendizado de git flow: não reescrever tags já publicadas no remoto.

### Branches
```
master    ← v0.4.0 ✅
develop   ← alinhada com master
```

### Arquivos implementados
| Arquivo | Status |
|---|---|
| `land.py` | ✅ Completo + 10 testes |
| `preflight.py` | ✅ Completo + detecção de comandos + 14 testes |
| `climb.py` | ✅ Completo + 10 testes |
| `fly.py` | ✅ Completo + add_file/del_file + 17 testes |
| `main.py` | ✅ Completo |
| `tests/test_land.py` | ✅ 10/10 |
| `tests/test_preflight.py` | ✅ 14/14 |
| `tests/test_climb.py` | ✅ 10/10 |
| `tests/test_fly.py` | ✅ 17/17 |

### Suite de testes
```bash
uv run pytest tests/ -v
# 51 passed in 7.07s
```

---

## Próximas ações imediatas

### 1. Testes de integração end-to-end (opcional mas recomendado)
Testar o fluxo completo com add-file e del-file via linha de comando:
```bash
mkdir -p /tmp/teste-tmgit
uv run python main.py /tmp/teste-tmgit add-file ~/.zshrc
uv run python main.py /tmp/teste-tmgit del-file .zshrc
```

### 2. Testes adicionais no test_preflight.py para comandos (v0.4.1)
```bash
git checkout develop
git checkout -b feature/tests-preflight-commands
```

Especificações a cobrir:
```
DADO que add-file é passado sem arquivo alvo
QUANDO preflight() for chamado
ENTÃO deve encerrar com sys.exit(1)

DADO que um comando inválido é passado
QUANDO preflight() for chamado
ENTÃO deve encerrar com sys.exit(1)

DADO que add-file é passado com arquivo alvo
QUANDO preflight() for chamado
ENTÃO context['command'] deve ser 'add-file' e context['command_target'] o arquivo
```

### 3. Próxima feature maior (v0.5.0)
A definir — possíveis candidatos:
- Suporte a `push-remote` com configuração de remotos
- Modo `version-all` (versionar todos os arquivos do diretório)
- Arquivo de configuração `.tmgit.conf`

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

Estado atual: v0.4.0 — add-file e del-file implementados, 51 testes passando.
Próximo passo: testes adicionais no preflight para comandos, ou nova feature.

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
- Merge commits com `--no-ff` e emoji `:twisted_rightwards_arrows:`
- Commits com emojis semânticos
- `[tool.uv] package = false` no pyproject.toml — projeto de scripts, não pacote
- **Metodologia SDD** — especificações DADO/QUANDO/ENTÃO escritas antes do código
- Testes pytest derivam das especificações e ficam em `tests/`
- **Fluxo sempre completo:** `preflight → climb → fly → land` — nunca desviar antes do `fly()`
- O `fly()` decide qual operação executar via `context['command']`
- **Versionamento:** MAJOR.MINOR.PATCH — MINOR para nova feature, PATCH para fix/doc
- `del_file()` verifica rastreamento no index, não existência no disco
