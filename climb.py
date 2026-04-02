"""Fase 2 - preparação do ambiente (climb) para tmgit-py.
Este módulo prepara o repositório: git init, branch, gitignore.
"""

import os
from git import Repo
from git.exc import InvalidGitRepositoryError
from land import land


def climb(context: dict) -> dict:
    """Prepara o repositório git para versionamento.

    Recebe o dicionário de contexto do preflight(), verifica/cria o repositório,
    .gitignore e branch do dia. Em caso de erro, chama land().

    Args:
        context (dict): Dicionário com variáveis inicializadas pelo preflight().

    Returns:
        dict: Dicionário de contexto atualizado.
    """

    # Extrair variáveis do contexto
    tmgit_tree = context['tmgit_tree']
    tmgit_dir = context['tmgit_dir']
    branch_name = context['branch_name']

    try:
        # 1. Verificar se o repositório git já existe
        try:
            repo = Repo(tmgit_tree)
        except InvalidGitRepositoryError:
            # Repositório não existe — criar com separate_git_dir
            os.makedirs(tmgit_dir, exist_ok=True)
            repo = Repo.init(tmgit_tree, separate_git_dir=tmgit_dir)

        # 2. Verificar e criar .gitignore se não existir
        gitignore_path = os.path.join(tmgit_tree, '.gitignore')

        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w') as f:
                f.write('*\n')

        # 3. Verificar se o repositório tem commits — se vazio, criar commit inicial
        if not repo.heads:
            repo.index.commit(":tada: Inicializando repositório tmgit")

        # 4. Verificar e criar/trocar para a branch do dia
        # Obter todas as branches remotas e locais
        existing_branches = [head.name for head in repo.heads]

        if branch_name in existing_branches:
            # Branch já existe — trocar para ela
            repo.heads[branch_name].checkout()
        else:
            # Branch não existe — criar a partir da branch atual
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()

        # Atualizar contexto
        context['land_caller'] = 'climb'
        context['land_msg'] = 'Climb concluído com sucesso'
        context['land_errlvl'] = 0

        return context

    except Exception as e:
        # Tratar erros passando para a fase land
        land(1, "climb", f"Erro ao preparar repositório em {tmgit_dir}",
             f"Detalhes: {str(e)}")
