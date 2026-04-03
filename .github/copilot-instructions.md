# .github/copilot-instructions.md — tmgit-py

## O que é este projeto

`tmgit-py` é uma reescrita em Python do projeto `tmgit` (shell script), que por sua vez é uma reescrita do `linux-time-machine.sh`.

O objetivo é criar uma "máquina do tempo" que versiona seletivamente um diretório (geralmente $HOME) usando git, criando uma branch por dia automaticamente. O usuário controla quais arquivos são versionados via `.gitignore` com `*` como padrão — ou seja, nenhum arquivo é versionado por padrão, e cada arquivo deve ser adicionado forçosamente.

Este é um projeto "Build to Learn": o objetivo principal é aprender Python e git flow, não apenas entregar funcionalidade.

---

## Arquitetura: padrão modo-avião

> Atualização de 2026-04-02: o guia "modo-aviao" foi refinado para ser mais objetivo, mantendo as quatro fases com responsabilidades bem definidas (tag de referência: `modo-aviao@v1.2`).

Todo o código segue o guia de boas práticas "modo-avião". As quatro fases são obrigatórias e cada uma tem responsabilidade exclusiva:

| Fase | Arquivo | Responsabilidade |
|---|---|---|
| `preflight` | `preflight.py` | Validações, inicialização de variáveis. Nenhuma alteração no ambiente. |
| `climb` | `climb.py` | Prepara o repositório: git init, branch, gitignore |
| `fly` | `fly.py` | Lógica principal: git add, commit, tag, push |
| `land` | `land.py` | Tratamento de erros, logs, encerramento |

**Regra fundamental:** nenhuma lógica de negócio fora da fase `fly`. Nenhum encerramento fora da fase `land`.

**Regra de fluxo obrigatória:** as quatro fases são sempre executadas em ordem, sem exceção. Nunca desviar o fluxo antes do `fly()`. O `fly()` decide internamente qual operação executar com base no contexto:

```
Sempre: preflight() → climb() → fly() → land()
```

O `fly()` lê `context['command']` e decide:
- `None` → fluxo normal: commit + tag
- `'add-file'` → adiciona arquivo ao rastreamento
- `'del-file'` → remove arquivo do rastreamento
- `'push-remote'` → push para remotos

---

## Estrutura de arquivos

```
tmgit-py/
├── main.py           # entry point — importa e orquestra as quatro fases
├── preflight.py      # fase 1: validações e variáveis
├── climb.py          # fase 2: prepara repositório
├── fly.py            # fase 3: commit, tag, push
├── land.py           # fase 4: erros e encerramento
├── .github/
│   └── copilot-instructions.md  # este arquivo — contexto do projeto
├── SESSION.md        # estado atual da sessão de desenvolvimento
└── pyproject.toml    # dependências gerenciadas pelo uv
```

---

## Dependências

- `gitpython` — interação com git (substitui chamadas shell ao git)
- Python 3.14 (já instalado via Homebrew)
- `uv` para gerenciamento de ambiente virtual e dependências
- `pytest` — testes automatizados (dependência de desenvolvimento)

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

- `main.py [diretorio]` — executa o fluxo completo
- `main.py [diretorio] add-file [arquivo]` — adiciona arquivo ao rastreamento
- `main.py [diretorio] del-file [arquivo]` — remove arquivo do rastreamento
- `main.py [diretorio] push-remote` — push para repositórios remotos
- `main.py --version` — exibe versão

### Modos de uso

O tmgit-py opera em dois modos distintos:

**Modo automático (cron):**
Executado periodicamente sem argumentos extras. Detecta alterações
nos arquivos já indexados e os versiona automaticamente.
main.py [diretorio]
Fluxo: preflight → climb → fly (commit + tag) → land

**Modo manual (terminal):**
Executado pelo usuário para gerenciar quais arquivos são rastreados.
Não realiza commit — apenas modifica o índice git.
main.py [diretorio] add-file [arquivo]
main.py [diretorio] del-file [arquivo]
Fluxo: preflight → climb → fly (indexa/desindexia) → land

O arquivo indexado via add-file será commitado automaticamente
na próxima execução do modo automático (cron).

Este comportamento é intencional — add-file e del-file são
operações de configuração do índice, não de versionamento.

### Regras de negócio importantes
- O `.gitignore` sempre começa com `*` — nada é versionado por padrão
- Arquivos são adicionados com `git add -f` (forçado, ignorando .gitignore)
- Uma branch por dia no formato `AAAA.MM.DD`
- O diretório `.tmgit/.git` fica dentro do diretório versionado
- O programa **sempre** encerra pela função `land()`

---

## Metodologia: Specification Driven Development (SDD)

O projeto adota SDD como metodologia de desenvolvimento. A especificação do comportamento esperado é escrita **antes** do código — o código é escrito para satisfazê-la.

### Fonte de especificações

As especificações derivam de três fontes já existentes no projeto:
1. Este `.github/copilot-instructions.md` — comportamento esperado de cada fase
2. Os scripts shell de referência (`fm_preflight.sh`, `fm_climb.sh` etc.) — especificações vivas
3. O guia modo-avião — contratos entre as fases

### Formato de especificação

Cada fase deve ter suas especificações escritas no formato DADO/QUANDO/ENTÃO antes da implementação:

```
DADO que [condição inicial]
QUANDO [ação executada]
ENTÃO [resultado esperado]
```

### Especificações por fase

#### land()
```
DADO error_level=0, caller="preflight", message="ok", error_message=""
QUANDO land() for chamado
ENTÃO deve exibir caller e message e encerrar com sys.exit(0)

DADO error_level=1, caller="preflight", message="erro", error_message="git não encontrado"
QUANDO land() for chamado
ENTÃO deve exibir caller, message e error_message e encerrar com sys.exit(1)
```

#### preflight()
```
DADO que nenhum argumento foi passado
QUANDO preflight() for chamado
ENTÃO deve chamar land() com error_level=1 e mensagem de uso

DADO que o diretório passado não existe
QUANDO preflight() for chamado
ENTÃO deve chamar land() com error_level=1 e mensagem de diretório inválido

DADO que o git não está instalado
QUANDO preflight() for chamado
ENTÃO deve chamar land() com error_level=1 e mensagem de git não encontrado

DADO que existe um arquivo index.lock no tmgit_dir
QUANDO preflight() for chamado
ENTÃO deve chamar land() com error_level=1 e mensagem de lock existente

DADO que todos os requisitos estão satisfeitos
QUANDO preflight() for chamado
ENTÃO deve retornar dicionário de contexto com todas as variáveis inicializadas
```

#### climb()
```
DADO que o repositório não existe
QUANDO climb() for chamado
ENTÃO deve criar tmgit_dir e inicializar git

DADO que o .gitignore não existe
QUANDO climb() for chamado
ENTÃO deve criar .gitignore com * como conteúdo

DADO que a branch do dia não existe
QUANDO climb() for chamado
ENTÃO deve criar a branch no formato AAAA.MM.DD

DADO que a branch do dia já existe
QUANDO climb() for chamado
ENTÃO deve apenas trocar para ela sem recriar
```

#### fly()
```
DADO que há arquivos modificados rastreados
QUANDO fly() for chamado
ENTÃO deve commitar com mensagem contendo commit_date

DADO que o working tree está limpo
QUANDO fly() for chamado
ENTÃO deve encerrar sem erro sem tentar commitar

DADO que push-remote foi solicitado
QUANDO fly() for chamado
ENTÃO deve fazer push para todos os remotos configurados
```

#### add_file() e del_file() — especificações para v0.4.0
```
DADO que add-file é passado como argumento com um caminho válido
QUANDO fly() for chamado
ENTÃO deve executar git add -f no arquivo informado antes do commit

DADO que del-file é passado como argumento com um arquivo rastreado
QUANDO fly() for chamado
ENTÃO deve executar git rm --cached no arquivo informado

DADO que o arquivo passado para add-file não existe
QUANDO fly() for chamado
ENTÃO deve chamar land() com error_level=1 e mensagem de arquivo não encontrado

DADO que o arquivo passado para del-file não está rastreado
QUANDO fly() for chamado
ENTÃO deve chamar land() com error_level=1 e mensagem de arquivo não rastreado
```

### Ciclo SDD por feature

```
1. Escrever especificações DADO/QUANDO/ENTÃO
2. Revisar especificações com o Claude (Project Manager)
3. Gerar prompt para o Copilot baseado nas especificações
4. Revisar código gerado contra as especificações
5. Escrever testes pytest derivados das especificações
6. Commitar especificações, código e testes juntos
```

### Testes

Os testes ficam em `tests/` e derivam diretamente das especificações:

```
tmgit-py/
└── tests/
    ├── test_land.py
    ├── test_preflight.py
    ├── test_climb.py
    └── test_fly.py
```

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
- Guia de boas práticas: modo-avião (tag de referência: `modo-aviao@v1.2`)
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
- **Consistência de caminhos:** sempre reutilizar variáveis de caminho já calculadas. Exemplo: usar `os.path.join(tmgit_dir, 'index.lock')` em vez de reconstruir o caminho completo.
- **Propriedades do gitpython:** usar `repo.bare` (não `repo.bare()`), `repo.is_dirty()` (este sim é método). Sempre verificar se é propriedade ou método antes de usar.

### Sobre o SESSION.md

O projeto mantém um arquivo `SESSION.md` que registra o estado atual do desenvolvimento: branch ativa, arquivos implementados, próximas ações e decisões tomadas.

**O SESSION.md deve ser atualizado:**
- Após cada commit relevante
- Ao iniciar ou encerrar uma feature branch
- Sempre que uma decisão arquitetural for tomada
- Ao final de cada sessão de trabalho

O `SESSION.md` é o ponto de entrada para retomar o projeto em uma nova sessão — qualquer agente ou desenvolvedor deve consultá-lo antes de qualquer ação.

### Como usar este arquivo no Copilot Chat

O Copilot Chat injeta `.github/copilot-instructions.md` automaticamente em todas as sessões do workspace. Não é necessário referenciar manualmente.

Para o aider no terminal, referencie explicitamente ao iniciar a sessão:
```bash
aider .github/copilot-instructions.md SESSION.md
```
