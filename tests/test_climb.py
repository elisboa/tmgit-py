"""Testes para a função climb() do módulo climb.py.
Seguindo a metodologia SDD — cada teste deriva de uma especificação DADO/QUANDO/ENTÃO.
"""

import pytest
import os
from datetime import datetime
from git import Repo
from unittest.mock import patch
from climb import climb


def make_context(tmp_path):
    """Helper para criar dicionário de contexto válido para os testes.

    Args:
        tmp_path: Fixture do pytest para criar diretórios temporários.

    Returns:
        dict: Dicionário de contexto pronto para climb().
    """
    tmgit_tree = str(tmp_path / "repo")
    os.makedirs(tmgit_tree)
    return {
        'tmgit_tree': tmgit_tree,
        'tmgit_dir': os.path.join(tmgit_tree, '.tmgit', '.git'),
        'branch_name': datetime.now().strftime('%Y.%m.%d'),
        'commit_date': datetime.now().strftime('%Y.%m.%d-%H.%M.%S') + '.000',
        'land_errlvl': 0,
        'land_caller': 'preflight',
        'land_msg': 'Preflight concluído com sucesso',
        'land_errmsg': ''
    }


class TestClimbRepositoryCreation:
    """Testes para criação do repositório git."""

    def test_climb_creates_tmgit_dir_when_not_exists(self, tmp_path):
        """DADO que o repositório não existe
        QUANDO climb() for chamado
        ENTÃO deve criar tmgit_dir
        """
        context = make_context(tmp_path)

        # Verificar que tmgit_dir não existe antes
        assert not os.path.exists(context['tmgit_dir'])

        # Chamar climb
        result_context = climb(context)

        # Verificar que tmgit_dir foi criado
        assert os.path.exists(context['tmgit_dir'])
        assert os.path.isdir(context['tmgit_dir'])

    def test_climb_creates_valid_git_repository(self, tmp_path):
        """DADO que o repositório não existe
        QUANDO climb() for chamado
        ENTÃO tmgit_dir deve ser um repositório git válido
        """
        context = make_context(tmp_path)

        # Chamar climb
        result_context = climb(context)

        # Verificar que é um repositório git válido
        repo = Repo(context['tmgit_tree'])
        assert repo.bare is False

        # Verificar que o git_dir está no local correto
        assert os.path.samefile(repo.git_dir, context['tmgit_dir'])


class TestClimbGitignore:
    """Testes para criação e manipulação do .gitignore."""

    def test_climb_creates_gitignore_when_not_exists(self, tmp_path):
        """DADO que o .gitignore não existe
        QUANDO climb() for chamado
        ENTÃO deve criar .gitignore em tmgit_tree com * como conteúdo
        """
        context = make_context(tmp_path)
        gitignore_path = os.path.join(context['tmgit_tree'], '.gitignore')

        # Verificar que .gitignore não existe antes
        assert not os.path.exists(gitignore_path)

        # Chamar climb
        result_context = climb(context)

        # Verificar que .gitignore foi criado
        assert os.path.exists(gitignore_path)

        # Verificar que contém *
        with open(gitignore_path, 'r') as f:
            content = f.read()
        assert '*' in content

    def test_climb_preserves_existing_gitignore(self, tmp_path):
        """DADO que o .gitignore já existe com conteúdo diferente
        QUANDO climb() for chamado
        ENTÃO não deve sobrescrever o .gitignore existente
        """
        context = make_context(tmp_path)
        gitignore_path = os.path.join(context['tmgit_tree'], '.gitignore')

        # Criar .gitignore com conteúdo customizado
        original_content = "# Custom gitignore\n*.log\n*.tmp\n"
        with open(gitignore_path, 'w') as f:
            f.write(original_content)

        # Chamar climb
        result_context = climb(context)

        # Verificar que .gitignore não foi sobrescrito
        with open(gitignore_path, 'r') as f:
            content = f.read()
        assert content == original_content


class TestClimbBranchManagement:
    """Testes para criação e alternância de branches."""

    def test_climb_creates_branch_when_not_exists(self, tmp_path):
        """DADO que a branch do dia não existe
        QUANDO climb() for chamado
        ENTÃO deve criar a branch no formato AAAA.MM.DD
        """
        context = make_context(tmp_path)
        branch_name = context['branch_name']

        # Chamar climb
        result_context = climb(context)

        # Verificar que a branch foi criada
        repo = Repo(context['tmgit_tree'])
        branch_names = [head.name for head in repo.heads]
        assert branch_name in branch_names

    def test_climb_switches_to_existing_branch(self, tmp_path):
        """DADO que a branch do dia já existe
        QUANDO climb() for chamado
        ENTÃO deve trocar para ela sem recriar
        """
        context = make_context(tmp_path)
        branch_name = context['branch_name']

        # Primeira chamada: criar a branch
        result_context = climb(context)

        # Criar um commit na branch para marcar que ela foi usada
        repo = Repo(context['tmgit_tree'])
        initial_head = repo.head.commit

        # Criar outra branch para mudar para longe
        other_branch = repo.create_head('other-branch')
        other_branch.checkout()

        # Verificar que estamos em outra branch agora
        assert repo.active_branch.name == 'other-branch'

        # Segunda chamada ao climb (with mesmo context)
        result_context = climb(context)

        # Verificar que voltamos para a branch do dia
        assert repo.active_branch.name == branch_name

        # Verificar que não criei duplicata da branch
        branch_names = [head.name for head in repo.heads]
        assert branch_names.count(branch_name) == 1

    def test_climb_returns_updated_context(self, tmp_path):
        """DADO que climb() foi executado com sucesso
        QUANDO o contexto for verificado
        ENTÃO land_caller deve ser 'climb' e land_errlvl deve ser 0
        """
        context = make_context(tmp_path)

        # Chamar climb
        result_context = climb(context)

        # Verificar que são o mesmo dicionário (ou pelo menos contém as chaves)
        assert result_context['land_caller'] == 'climb'
        assert result_context['land_errlvl'] == 0
        assert 'climb' in result_context['land_msg'].lower()


class TestClimbCompleteFlow:
    """Testes de fluxo completo com múltiplas operações."""

    def test_climb_creates_initial_commit(self, tmp_path):
        """DADO que o repositório foi criado vazio
        QUANDO climb() for chamado
        ENTÃO deve criar um commit inicial
        """
        context = make_context(tmp_path)

        # Chamar climb
        result_context = climb(context)

        # Verificar que o repositório tem commits
        repo = Repo(context['tmgit_tree'])
        assert len(repo.heads) > 0
        assert len(list(repo.iter_commits())) > 0

    def test_climb_full_workflow_creates_all_artifacts(self, tmp_path):
        """DADO que climb() é chamado em um diretório novo
        QUANDO climb() completa com sucesso
        ENTÃO deve ter criado: repositório, branch, .gitignore e commit inicial
        """
        context = make_context(tmp_path)
        branch_name = context['branch_name']
        gitignore_path = os.path.join(context['tmgit_tree'], '.gitignore')

        # Chamar climb
        result_context = climb(context)

        # Verificar repositório
        assert os.path.exists(context['tmgit_dir'])
        repo = Repo(context['tmgit_tree'])

        # Verificar branch
        assert branch_name in [head.name for head in repo.heads]
        assert repo.active_branch.name == branch_name

        # Verificar .gitignore
        assert os.path.exists(gitignore_path)
        with open(gitignore_path, 'r') as f:
            assert '*' in f.read()

        # Verificar commit
        assert len(list(repo.iter_commits())) > 0

    def test_climb_multiple_calls_preserve_state(self, tmp_path):
        """DADO que climb() é chamado múltiplas vezes
        QUANDO o repositório já existe
        ENTÃO não deve perder estado nem dados
        """
        context = make_context(tmp_path)

        # Primeira chamada
        result_context1 = climb(context)
        repo = Repo(context['tmgit_tree'])
        commits_after_first = len(list(repo.iter_commits()))

        # Fazer uma mudança no repositório
        test_file = os.path.join(context['tmgit_tree'], 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        # Segunda chamada
        result_context2 = climb(context)
        commits_after_second = len(list(repo.iter_commits()))

        # O número de commits não deve mudarnecessariamente,
        # mas o arquivo que criamos deve estar lá
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            assert f.read() == 'test content'


class TestClimbErrorHandling:
    """Testes para tratamento de erros em climb()."""

    def test_climb_handles_unexpected_error(self, tmp_path):
        """DADO que ocorre um erro inesperado durante climb()
        QUANDO climb() for chamado com tmgit_dir inválido que causa exceção
        ENTÃO deve encerrar com sys.exit(1)
        """
        context = make_context(tmp_path)

        with patch('climb.Repo') as mock_repo:
            mock_repo.side_effect = Exception('erro simulado')
            with pytest.raises(SystemExit) as exc_info:
                climb(context)
            assert exc_info.value.code == 1
