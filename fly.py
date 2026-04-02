"""Fase 3 - voo de cruzeiro (fly) para tmgit-py.
Este módulo contém a lógica principal: commit, tag, push.
"""

from git import Repo
from git.exc import GitCommandError
from land import land


def commit_files(repo, commit_date: str) -> bool:
    """Verifica mudanças e commita arquivos rastreados.

    Args:
        repo: Objeto Repo do gitpython.
        commit_date (str): Data/hora do commit no formato AAAA.MM.DD-HH.MM.SS.mmm

    Returns:
        bool: True se houve commit, False se working tree estava limpo.
    """

    # Verificar se há mudanças no working tree
    if not repo.is_dirty(untracked_files=False):
        # Working tree limpo — nenhum commit necessário
        return False

    # Obter lista de arquivos rastreados no index
    tracked_files = [path for path, _ in repo.index.entries.keys()]

    # Preparar mensagem de commit
    commit_message = f"{', '.join(tracked_files) if tracked_files else 'Arquivos rastreados'}\n\nCommit automático realizado às {commit_date}"

    try:
        # Fazer git add nos arquivos rastreados
        repo.index.add(tracked_files)
        # Commitar com a mensagem
        repo.index.commit(commit_message)
        return True
    except GitCommandError as e:
        raise Exception(f"Erro ao commitar: {str(e)}")


def tag_commit(repo, commit_date: str) -> None:
    """Aplica tag leve com o valor de commit_date.

    Args:
        repo: Objeto Repo do gitpython.
        commit_date (str): Data/hora do commit no formato AAAA.MM.DD-HH.MM.SS.mmm
    """

    try:
        # Aplicar tag leve (lightweight tag) no commit atual
        repo.create_tag(commit_date)
    except GitCommandError as e:
        raise Exception(f"Erro ao criar tag: {str(e)}")


def push_remote(repo) -> None:
    """Faz push para todos os remotos configurados com --follow-tags.

    Args:
        repo: Objeto Repo do gitpython.
    """

    if not repo.remotes:
        # Nenhum remoto configurado — sem erro
        return

    try:
        for remote in repo.remotes:
            # Fazer push para o remoto com --follow-tags e timeout
            remote.push(follow_tags=True, kill_after_timeout=30)
    except GitCommandError as e:
        raise Exception(f"Erro ao fazer push: {str(e)}")


def fly(context: dict) -> dict:
    """Executa a lógica principal: commit, tag e push.

    Recebe o dicionário de contexto do climb(), verifica mudanças,
    commita arquivos rastreados, aplica tag e faz push. Em caso de erro,
    chama land().

    Args:
        context (dict): Dicionário com variáveis inicializadas pelo climb().

    Returns:
        dict: Dicionário de contexto atualizado.
    """

    tmgit_tree = context['tmgit_tree']
    commit_date = context['commit_date']
    push_remote_requested = context.get('push_remote_requested', False)

    try:
        # Abrir o repositório pelo work_tree
        repo = Repo(tmgit_tree)

        # Tentar commitar arquivos modificados
        commit_done = commit_files(repo, commit_date)

        # Se houve commit, aplicar tag
        if commit_done:
            tag_commit(repo, commit_date)

        # Se push foi solicitado, fazer push para os remotos
        if push_remote_requested:
            push_remote(repo)

        # Atualizar contexto
        context['land_caller'] = 'fly'
        context['land_msg'] = 'Fly concluído com sucesso'
        context['land_errlvl'] = 0

        return context

    except Exception as e:
        # Tratar erros passando para a fase land
        land(1, "fly", f"Erro ao executar voo em {tmgit_tree}",
             f"Detalhes: {str(e)}")
