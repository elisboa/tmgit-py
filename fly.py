"""Fase 3 - voo de cruzeiro (fly) para tmgit-py.
Este módulo contém a lógica principal: commit, tag, push.
"""

import os
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


def add_file(repo, filepath: str, tmgit_tree: str) -> None:
    """Adiciona um arquivo ao índice (forçando rastreamento)."""

    # Resolver caminho absoluto
    if os.path.isabs(filepath):
        filepath_abs = filepath
    else:
        filepath_abs = os.path.join(tmgit_tree, filepath)

    if not os.path.exists(filepath_abs):
        raise Exception(f"Arquivo para add-file não encontrado: {filepath_abs}")

    # Índice trabalha com paths relativos à work tree. Garantir que é relativo
    rel_path = os.path.relpath(filepath_abs, tmgit_tree)
    repo.index.add([rel_path])


def del_file(repo, filepath: str, tmgit_tree: str) -> None:
    """Remove o arquivo do índice (untrack)."""

    if os.path.isabs(filepath):
        filepath_abs = filepath
    else:
        filepath_abs = os.path.join(tmgit_tree, filepath)

    rel_path = os.path.relpath(filepath_abs, tmgit_tree)

    if rel_path not in [path for path, _ in repo.index.entries.keys()]:
        raise Exception(f"Arquivo não rastreado: {rel_path}")

    repo.index.remove([rel_path])


def fly(context: dict) -> dict:
    """Executa a lógica principal: commit, tag e push ou comando específico."""

    tmgit_tree = context['tmgit_tree']
    commit_date = context['commit_date']
    push_remote_requested = context.get('push_remote_requested', False)
    command = context.get('command')
    command_target = context.get('command_target')

    try:
        repo = Repo(tmgit_tree)

        if command == 'add-file':
            if not command_target:
                raise Exception('add-file requer argumento command_target')
            add_file(repo, command_target, tmgit_tree)

            context['land_caller'] = 'fly'
            context['land_msg'] = f"add-file {command_target} concluído"
            context['land_errlvl'] = 0
            return context

        if command == 'del-file':
            if not command_target:
                raise Exception('del-file requer argumento command_target')
            del_file(repo, command_target, tmgit_tree)

            context['land_caller'] = 'fly'
            context['land_msg'] = f"del-file {command_target} concluído"
            context['land_errlvl'] = 0
            return context

        if command == 'push-remote':
            push_remote(repo)

            context['land_caller'] = 'fly'
            context['land_msg'] = 'push-remote concluído'
            context['land_errlvl'] = 0
            return context

        # Fluxo normal (sem comando ou command == None)
        commit_done = commit_files(repo, commit_date)

        if commit_done:
            tag_commit(repo, commit_date)

        if push_remote_requested:
            push_remote(repo)

        context['land_caller'] = 'fly'
        context['land_msg'] = 'Fly concluído com sucesso'
        context['land_errlvl'] = 0

        return context

    except Exception as e:
        land(1, 'fly', f'Erro ao executar voo em {tmgit_tree}',
             f'Detalhes: {str(e)}')
