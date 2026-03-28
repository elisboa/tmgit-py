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

## Instruções para o modelo (aider/LLM)

- Sempre seguir o padrão modo-avião: cada fase em seu arquivo
- Usar `gitpython` para todas as operações git — nunca `subprocess` para chamar git
- Variáveis de contexto (LAND_*) devem ser passadas entre funções, não como globais
- Tratar erros sempre na função `land()`, nunca inline
- Código em português (comentários e mensagens), nomes de variáveis e funções em inglês
- Commits pequenos por função implementada
- Não implementar tudo de uma vez — uma função por sessão
