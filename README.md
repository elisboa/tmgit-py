# tmgit-py

Máquina do tempo para o seu `$HOME` — versiona seletivamente um diretório usando git, criando uma branch por dia automaticamente.

Reescrita em Python do projeto [tmgit](https://github.com/elisboa/tmgit), que por sua vez é uma reescrita do [linux-time-machine.sh](https://github.com/elisboa/linux-time-machine.sh).

---

## Como funciona

O `tmgit-py` cria um repositório git oculto dentro do diretório que você quer versionar. Por padrão, **nenhum arquivo é rastreado** — você escolhe explicitamente o que quer versionar. Cada execução automática cria um commit na branch do dia (`2026.04.17`), formando um histórico navegável por data.

A filosofia é oposta ao `etckeeper`: em vez de versionar tudo e excluir o que não quer, o `tmgit-py` ignora tudo e você inclui o que quer. Isso é mais seguro para o `$HOME`, onde existem dados sensíveis e arquivos temporários.

---

## Requisitos

- Python 3.14+
- git instalado e disponível no `PATH`
- [uv](https://github.com/astral-sh/uv) para gerenciamento de ambiente

---

## Instalação

```bash
git clone https://github.com/elisboa/tmgit-py
cd tmgit-py
uv sync
```

---

## Uso

### Modo automático (cron)

Executa o fluxo completo: detecta alterações nos arquivos rastreados e commita.

```bash
uv run main.py /home/usuario
```

Para rodar periodicamente, adicione ao crontab:

```
*/30 * * * * cd /caminho/para/tmgit-py && uv run main.py /home/usuario
```

### Modo manual (terminal)

Gerencia quais arquivos são rastreados. Não realiza commit — apenas modifica o índice git. O arquivo será commitado automaticamente na próxima execução automática.

```bash
# Adicionar um arquivo ao rastreamento
uv run main.py /home/usuario add-file /home/usuario/.bashrc

# Remover um arquivo do rastreamento
uv run main.py /home/usuario del-file /home/usuario/.bashrc

# Fazer push para repositórios remotos configurados
uv run main.py /home/usuario push-remote
```

---

## Estrutura do repositório criado

O repositório fica dentro do diretório versionado, em `.tmgit/.git`. Isso mantém tudo contido e não polui o `$HOME` com um `.git` visível.

```
/home/usuario/
└── .tmgit/
    └── .git/      ← repositório git do tmgit-py
```

Branches criadas automaticamente no formato `AAAA.MM.DD`:

```
2026.04.15
2026.04.16
2026.04.17   ← branch do dia
```

---

## Arquitetura

O projeto segue o padrão **modo-avião**: quatro fases com responsabilidades exclusivas, sempre executadas em ordem.

```
preflight() → climb() → fly() → land()
```

| Fase | Arquivo | Responsabilidade |
|---|---|---|
| `preflight` | `preflight.py` | Valida o ambiente e inicializa variáveis |
| `climb` | `climb.py` | Prepara o repositório (git init, branch, .gitignore) |
| `fly` | `fly.py` | Lógica principal: commit, tag, push, add/del arquivo |
| `land` | `land.py` | Encerramento: exibe resultado e chama sys.exit |

---

## Desenvolvimento

```bash
# Rodar testes com cobertura
uv run pytest tests/ --cov=. --cov-report=term-missing

# Esperado: 71 passed, 99% coverage
```

Este projeto usa **Specification Driven Development (SDD)**: especificações `DADO/QUANDO/ENTÃO` são escritas antes do código. Veja `.github/copilot-instructions.md` para o contexto completo.
