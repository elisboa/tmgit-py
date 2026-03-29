# CONTEXT.md — tmgit-py

## O que é este projeto

`tmgit-py` é uma reescrita em Python do projeto `tmgit` (shell script), que por sua vez é uma reescrita do `linux-time-machine.sh`.

O objetivo é criar uma "máquina do tempo" que versiona seletivamente um diretório (geralmente $HOME) usando git, criando uma branch por dia automaticamente. O usuário controla quais arquivos são versionados via `.gitignore` com `*` como padrão — ou seja, nenhum arquivo é versionado por padrão, e cada arquivo deve ser adicionado forçosamente.

Este é um projeto "Build to Learn": o objetivo principal é aprender Python e git flow, não apenas entregar funcionalidade.

---

## Arquitetura: padrão modo-avião

Todo o código segue o guia de boas práticas "modo-avião". As quatro fases são obrigatórias e cada uma tem responsabilidade exclusiva:

| Fase | Arquivo | Responsabilidade |
|---|---|---|
| `preflight` | `preflight.py` | Validações, inicialização de variáveis. Nenhuma alteração no ambiente. |
| `climb` | `climb.py` | Prepara o repositório: git init, branch, gitignore |
| `fly` | `fly.py` | Lógica principal: git add, commit, tag, push |
| `land` | `land.py` | Tratamento de erros, logs, encerramento |

**Regra fundamental:** nenhuma lógica de negócio fora da fase `fly`. Nenhum encerramento fora da fase `land`.

---

## Estrutura de arquivos

```
tmgit-py/
├── tmgit.py          # entry point — importa e orquestra as quatro fases
├── preflight.py      # fase 1: validações e variáveis
├── climb.py          # fase 2: prepara repositório
├── fly.py            # fase 3: commit, tag, push
├── land.py           # fase 4: erros e encerramento
├── CONTEXT.md        # este arquivo
└── pyproject.toml    # dependências gerenciadas pelo uv
```

---

## Dependências

- `gitpython` — interação com git (substitui chamadas shell ao git)
- Python 3.14 (já instalado via Homebrew)
- `uv` para gerenciamento de ambiente virtual e dependências

---

## Variáveis principais

| Variável | Descrição |
|---|---|
| `TMGIT_TREE` | Diretório a ser versionado (obrigatório, ex: /home/user) |
| `TMGIT_DIR` | Diretório do repositório git (padrão: `TMGIT_TREE/.tmgit/.git`) |
| `COMMIT_DATE` | Data/hora do commit no formato `AAAA.MM.DD-HH.MM` |
| `BRANCH_NAME` | Nome da branch no formato `AAAA.MM.DD` |
| `LAND_ERRLVL` | Nível de erro acumulado (0 = sucesso) |
| `LAND_CALLER` | Rastreio da cadeia de funções chamadoras |
| `LAND_MSG` | Mensagem de encerramento |
| `LAND_ERRMSG` | Mensagem de erro detalhada |

---

## Comportamento esperado

### Fluxo normal
1. Recebe o diretório a ser versionado como argumento
2. Valida ambiente e argumentos (`preflight`)
3. Verifica/cria repositório e branch do dia (`climb`)
4. Commita alterações nos arquivos já rastreados (`fly`)
5. Encerra com status e mensagens (`land`)

### Comandos suportados
- `tmgit.py [diretorio]` — executa o fluxo completo
- `tmgit.py [diretorio] add-file [arquivo]` — adiciona arquivo ao rastreamento
- `tmgit.py [diretorio] del-file [arquivo]` — remove arquivo do rastreamento
- `tmgit.py [diretorio] push-remote` — push para repositórios remotos
- `tmgit.py --version` — exibe versão

### Regras de negócio importantes
- O `.gitignore` sempre começa com `*` — nada é versionado por padrão
- Arquivos são adicionados com `git add -f` (forçado, ignorando .gitignore)
- Uma branch por dia no formato `AAAA.MM.DD`
- O diretório `.tmgit/.git` fica dentro do diretório versionado
- O programa **sempre** encerra pela função `land()`

---

## Comparativo com ferramentas similares

### etckeeper

O `etckeeper` é a ferramenta mais próxima conceitualmente — versiona diretórios usando git de forma automática. Porém as filosofias são opostas e os casos de uso são distintos:

| Aspecto | etckeeper | tmgit-py |
|---|---|---|
| Diretório alvo | Fixo: `/etc` | Qualquer diretório, tipicamente `$HOME` |
| Integração com pacotes | Sim (apt, dnf, pacman) | Não |
| Filosofia do gitignore | Versiona tudo por padrão | Ignora tudo por padrão (`*`) |
| Preserva permissões unix | Sim, é foco central | Não |
| Branch por data | Não | Sim |
| Multiplataforma | Linux principalmente | Linux e macOS |
| Público-alvo | Administração de sistema | Uso pessoal / dotfiles |

**Diferença filosófica central:** o etckeeper versiona tudo e você exclui o que não quer. O tmgit-py ignora tudo e você inclui explicitamente o que quer — comportamento mais seguro para o `$HOME`, onde existem dados sensíveis e arquivos temporários.

**Para um SRE, as duas ferramentas são complementares:** o etckeeper cuida da camada de infraestrutura (`/etc`), o tmgit-py cuida da camada pessoal (`$HOME`). Não competem.

---

## Referências

- Projeto original: `linux-time-machine.sh`
- Reescrita em shell: `tmgit`
- Guia de boas práticas: modo-avião
- Autor: Eduardo Lisboa <eduardo.lisboa@gmail.com>

---

## Git flow

O projeto usa um fluxo baseado em branches, mesmo sendo desenvolvimento solo. O objetivo é aprender git flow na prática e manter histórico legível.

### Estrutura de branches

```
master          # código estável — só recebe merges vindos da develop
└── develop     # integração contínua do desenvolvimento
    ├── feature/land-py
    ├── feature/preflight-py
    ├── feature/climb-py
    └── feature/fly-py
```

### Regras obrigatórias

- **Nunca** commitar direto na `master`
- **Nunca** commitar direto na `develop`
- Cada arquivo do padrão modo-avião vira uma branch `feature/`
- Ao terminar uma feature → merge na `develop`
- Quando `develop` estiver estável → merge na `master` com tag de versão

### Ciclo de uma feature

```bash
# Criar branch a partir da develop
git checkout develop
git checkout -b feature/nome-da-feature

# Desenvolver e commitar
git add arquivo.py
git commit -m ":sparkles: Descrição do que foi feito"

# Ao terminar, merge na develop
git checkout develop
git merge feature/nome-da-feature
git branch -d feature/nome-da-feature
```

### Convenção de mensagens de commit

Usar emojis semânticos no início da mensagem:

| Emoji | Código | Uso |
|---|---|---|
| 🎉 | `:tada:` | Início de projeto |
| ✨ | `:sparkles:` | Nova feature |
| 🐛 | `:bug:` | Correção de bug |
| ♻️ | `:recycle:` | Refatoração |
| 🔧 | `:wrench:` | Configuração |
| 🙈 | `:see_no_evil:` | Ajuste de .gitignore |
| 📝 | `:memo:` | Documentação |
| 🏷️ | `:label:` | Nova versão/tag |

---

## Instruções para o modelo (aider/LLM)

- Sempre seguir o padrão modo-avião: cada fase em seu arquivo
- Usar `gitpython` para todas as operações git — nunca `subprocess` para chamar git
- Variáveis de contexto (LAND_*) devem ser passadas entre funções, não como globais
- Tratar erros sempre na função `land()`, nunca inline
- Código em português (comentários e mensagens), nomes de variáveis e funções em inglês
- Commits pequenos por função implementada
- Não implementar tudo de uma vez — uma função por sessão
- A função principal de cada fase deve ter o mesmo nome da fase: `preflight()`, `climb()`, `fly()`, `land()`
- O fluxo completo legível no main.py deve ser: `preflight() → climb() → fly() → land()`
- **Consistência de caminhos:** sempre reutilizar variáveis de caminho já calculadas. Exemplo: usar `os.path.join(tmgit_dir, 'index.lock')` em vez de reconstruir `os.path.join(tmgit_tree, '.tmgit', '.git', 'index.lock')`. Se uma variável de caminho já existe, usá-la como base para caminhos derivados.

### Sobre o SESSION.md

O projeto mantém um arquivo `SESSION.md` que registra o estado atual do desenvolvimento: branch ativa, arquivos implementados, próximas ações e decisões tomadas.

**O SESSION.md deve ser atualizado:**
- Após cada commit relevante
- Ao iniciar ou encerrar uma feature branch
- Sempre que uma decisão arquitetural for tomada
- Ao final de cada sessão de trabalho

O `SESSION.md` é o ponto de entrada para retomar o projeto em uma nova sessão — qualquer agente ou desenvolvedor deve consultá-lo antes de qualquer ação.

### Como usar este arquivo no Copilot Chat

O Copilot Chat **não injeta o CONTEXT.md automaticamente**. Para garantir que o agente tenha contexto do projeto, sempre inicie uma nova sessão com:

```
@CONTEXT.md Vamos trabalhar no tmgit-py. [sua instrução aqui]
```
