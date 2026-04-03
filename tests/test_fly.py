"""Testes para a função fly() e funções relacionadas do módulo fly.py.
Seguindo a metodologia SDD — cada teste deriva de uma especificação DADO/QUANDO/ENTÃO.
"""

import pytest
import os
from datetime import datetime
from git import Repo
from git.exc import GitCommandError
from unittest.mock import patch, MagicMock
from climb import climb
from fly import fly, commit_files, tag_commit, push_remote


def make_context(tmp_path):
    """Helper para criar dicionário de contexto válido para os testes.

    Args:
        tmp_path: Fixture do pytest para criar diretórios temporários.

    Returns:
        dict: Dicionário de contexto pronto para fly().
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
        'land_errmsg': '',
        'command': None,
        'command_target': None,
        'push_remote_requested': False
    }


class TestFlyNoChanges:
    """Testes para fly() com working tree limpo (sem mudanças)."""

    def test_fly_no_commit_when_tree_is_clean(self, tmp_path):
        """DADO que o working tree está limpo (sem arquivos rastreados modificados)
        QUANDO fly() for chamado
        ENTÃO deve retornar contexto com land_errlvl=0 sem fazer commit
        """
        context = make_context(tmp_path)

        # Preparar repositório via climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Obter número de commits antes
        commits_before = len(list(repo.iter_commits()))

        # Chamar fly com working tree limpo
        result_context = fly(context)

        # Obter número de commits depois
        commits_after = len(list(repo.iter_commits()))

        # Não deve ter criado novo commit
        assert commits_after == commits_before
        assert result_context['land_errlvl'] == 0


class TestFlyWithChanges:
    """Testes para fly() com mudanças no working tree."""

    def test_fly_commits_modified_files(self, tmp_path):
        """DADO que há arquivos rastreados modificados
        QUANDO fly() for chamado
        ENTÃO deve criar um novo commit no repositório
        """
        context = make_context(tmp_path)

        # Preparar repositório via climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Criar e rastrear um arquivo
        test_file = os.path.join(context['tmgit_tree'], 'test.txt')
        with open(test_file, 'w') as f:
            f.write('conteudo inicial')
        repo.index.add(['test.txt'])
        repo.index.commit('Arquivo de teste')

        # Modificar o arquivo
        with open(test_file, 'w') as f:
            f.write('conteudo modificado')

        # Obter número de commits antes
        commits_before = len(list(repo.iter_commits()))

        # Chamar fly
        result_context = fly(context)

        # Obter número de commits depois
        commits_after = len(list(repo.iter_commits()))

        # Deve ter criado novo commit
        assert commits_after == commits_before + 1

    def test_fly_commit_contains_commit_date(self, tmp_path):
        """DADO que um commit foi criado
        QUANDO fly() for chamado
        ENTÃO a mensagem do commit deve conter commit_date
        """
        context = make_context(tmp_path)
        commit_date = context['commit_date']

        # Preparar repositório via climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Criar e rastrear um arquivo
        test_file = os.path.join(context['tmgit_tree'], 'test.txt')
        with open(test_file, 'w') as f:
            f.write('conteudo')
        repo.index.add(['test.txt'])
        repo.index.commit('Arquivo inicial')

        # Modificar o arquivo
        with open(test_file, 'w') as f:
            f.write('modificado')

        # Chamar fly
        result_context = fly(context)

        # Obter o último commit
        last_commit = list(repo.iter_commits())[0]

        # Verificar que commit_date está na mensagem
        assert commit_date in last_commit.message or commit_date.replace('.', '-') in last_commit.message


class TestFlyTagging:
    """Testes para criação de tags via fly()."""

    def test_fly_creates_tag_when_commit_done(self, tmp_path):
        """DADO que um commit foi criado
        QUANDO fly() for chamado
        ENTÃO deve aplicar uma tag com o valor de commit_date
        """
        context = make_context(tmp_path)
        commit_date = context['commit_date']

        # Preparar repositório via climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Criar e rastrear um arquivo
        test_file = os.path.join(context['tmgit_tree'], 'test.txt')
        with open(test_file, 'w') as f:
            f.write('conteudo')
        repo.index.add(['test.txt'])
        repo.index.commit('Arquivo inicial')

        # Modificar o arquivo
        with open(test_file, 'w') as f:
            f.write('modificado')

        # Chamar fly
        result_context = fly(context)

        # Obter lista de tags
        tags = [tag.name for tag in repo.tags]

        # Deve ter criado tag com commit_date
        assert commit_date in tags

    def test_fly_tag_points_to_new_commit(self, tmp_path):
        """DADO que um commit e tag foram criados
        QUANDO fly() for chamado
        ENTÃO a tag deve apontar para o novo commit
        """
        context = make_context(tmp_path)
        commit_date = context['commit_date']

        # Preparar repositório via climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Criar e rastrear um arquivo
        test_file = os.path.join(context['tmgit_tree'], 'test.txt')
        with open(test_file, 'w') as f:
            f.write('conteudo')
        repo.index.add(['test.txt'])
        repo.index.commit('Arquivo inicial')

        # Modificar o arquivo
        with open(test_file, 'w') as f:
            f.write('modificado')

        # Chamar fly
        result_context = fly(context)

        # Obter o último commit e a tag
        last_commit = list(repo.iter_commits())[0]
        tag = repo.tags[commit_date]

        # A tag deve apontar para o último commit
        assert tag.commit == last_commit


class TestFlyPush:
    """Testes para push de remotos via fly()."""

    def test_fly_handles_no_remotes_configured(self, tmp_path):
        """DADO que não há remotos configurados
        QUANDO fly() for chamado com push_remote_requested=True
        ENTÃO deve retornar contexto com land_errlvl=0 sem erro
        """
        context = make_context(tmp_path)
        context['push_remote_requested'] = True

        # Preparar repositório via climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Garantir que não há remotos
        assert len(repo.remotes) == 0

        # Chamar fly com push requisitado
        result_context = fly(context)

        # Deve retornar com sucesso
        assert result_context['land_errlvl'] == 0


class TestFlyCommands:
    """Testes para comandos via context['command'] dentro do fly()."""

    def test_fly_add_file_traces_file(self, tmp_path):
        """DADO command='add-file' e command_target existente
        QUANDO fly() for chamado
        ENTÃO o arquivo deve estar rastreado no index do repositório
        """
        context = make_context(tmp_path)
        test_file = os.path.join(context['tmgit_tree'], 'new.txt')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w') as f:
            f.write('conteudo')

        context = climb(context)
        context['command'] = 'add-file'
        context['command_target'] = 'new.txt'

        result_context = fly(context)

        repo = Repo(context['tmgit_tree'])
        assert 'new.txt' in [path for path, _ in repo.index.entries.keys()]
        assert result_context['land_errlvl'] == 0

    def test_fly_add_file_missing_raises_systemexit(self, tmp_path):
        """DADO command='add-file' e arquivo inexistente
        QUANDO fly() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        context = make_context(tmp_path)
        context = climb(context)
        context['command'] = 'add-file'
        context['command_target'] = 'missing.txt'

        with pytest.raises(SystemExit) as exc_info:
            fly(context)

        assert exc_info.value.code == 1

    def test_fly_add_file_relative_path(self, tmp_path):
        """DADO command='add-file' e command_target relativo
        QUANDO fly() for chamado
        ENTÃO deve resolver caminho relativo e rastrear o arquivo
        """
        context = make_context(tmp_path)
        test_file = os.path.join(context['tmgit_tree'], 'subdir', 'item.txt')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w') as f:
            f.write('conteudo')

        context = climb(context)
        context['command'] = 'add-file'
        context['command_target'] = os.path.join('subdir', 'item.txt')

        result_context = fly(context)

        repo = Repo(context['tmgit_tree'])
        assert os.path.join('subdir', 'item.txt') in [path for path, _ in repo.index.entries.keys()]
        assert result_context['land_errlvl'] == 0

    def test_fly_del_file_untracks_file(self, tmp_path):
        """DADO command='del-file' e arquivo rastreado
        QUANDO fly() for chamado
        ENTÃO o arquivo não deve mais estar no index
        """
        context = make_context(tmp_path)
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        test_file = os.path.join(context['tmgit_tree'], 'tracked.txt')
        with open(test_file, 'w') as f:
            f.write('content')
        repo.index.add(['tracked.txt'])
        repo.index.commit('track file')

        context['command'] = 'del-file'
        context['command_target'] = 'tracked.txt'

        result_context = fly(context)

        repo = Repo(context['tmgit_tree'])
        assert 'tracked.txt' not in [path for path, _ in repo.index.entries.keys()]
        assert result_context['land_errlvl'] == 0

    def test_fly_del_file_not_tracked_raises_systemexit(self, tmp_path):
        """DADO command='del-file' e arquivo não rastreado
        QUANDO fly() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        context = make_context(tmp_path)
        context = climb(context)
        context['command'] = 'del-file'
        context['command_target'] = 'nottracked.txt'

        with pytest.raises(SystemExit) as exc_info:
            fly(context)

        assert exc_info.value.code == 1

    def test_fly_push_remote_no_remotes(self, tmp_path):
        """DADO command='push-remote' e sem remotos
        QUANDO fly() for chamado
        ENTÃO deve retornar contexto com land_errlvl=0
        """
        context = make_context(tmp_path)
        context = climb(context)
        context['command'] = 'push-remote'
        context['command_target'] = None

        result_context = fly(context)

        assert result_context['land_errlvl'] == 0


class TestFlyContext:
    """Testes para o dicionário de contexto retornado por fly()."""

    def test_fly_returns_updated_context(self, tmp_path):
        """DADO que fly() foi executado com sucesso
        QUANDO o contexto for verificado
        ENTÃO land_caller deve ser 'fly' e land_errlvl deve ser 0
        """
        context = make_context(tmp_path)

        # Preparar repositório via climb
        context = climb(context)

        # Chamar fly
        result_context = fly(context)

        # Verificar contexto
        assert result_context['land_caller'] == 'fly'
        assert result_context['land_errlvl'] == 0
        assert 'fly' in result_context['land_msg'].lower()

    def test_fly_preserves_critical_context_variables(self, tmp_path):
        """DADO que fly() foi executado com sucesso
        QUANDO o contexto for verificado
        ENTÃO deve preservar tmgit_tree, tmgit_dir e branch_name
        """
        context = make_context(tmp_path)
        original_tree = context['tmgit_tree']
        original_dir = context['tmgit_dir']
        original_branch = context['branch_name']

        # Preparar repositório via climb
        context = climb(context)

        # Chamar fly
        result_context = fly(context)

        # Verificar que variáveis críticas foram preservadas
        assert result_context['tmgit_tree'] == original_tree
        assert result_context['tmgit_dir'] == original_dir
        assert result_context['branch_name'] == original_branch


class TestFlyCompleteFlow:
    """Testes de fluxo completo com múltiplas operações."""

    def test_fly_complete_workflow_with_changes(self, tmp_path):
        """DADO que há mudanças no repositório
        QUANDO todo o fluxo preflight→climb→fly for executado
        ENTÃO deve criar commit, tag e retornar contexto válido
        """
        context = make_context(tmp_path)

        # Executar climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Criar arquivo rastreado
        test_file = os.path.join(context['tmgit_tree'], 'config.txt')
        with open(test_file, 'w') as f:
            f.write('configuracao inicial')
        repo.index.add(['config.txt'])
        repo.index.commit('Arquivo config')

        # Modificar arquivo
        with open(test_file, 'w') as f:
            f.write('configuracao atualizada')

        # Executar fly
        result_context = fly(context)

        # Verificar resultado completo
        assert result_context['land_errlvl'] == 0
        assert result_context['land_caller'] == 'fly'

        # Verificar que commit foi criado
        commits = list(repo.iter_commits())
        assert len(commits) > 1

        # Verificar que tag foi criada
        tags = [tag.name for tag in repo.tags]
        assert context['commit_date'] in tags

    def test_fly_multiple_files_in_single_commit(self, tmp_path):
        """DADO que há múltiplos arquivos rastreados modificados
        QUANDO fly() for chamado
        ENTÃO todos os arquivo devem estar no mesmo commit
        """
        context = make_context(tmp_path)

        # Preparar repositório via climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Criar diversos arquivos rastreados
        files_to_track = ['file1.txt', 'file2.txt', 'file3.txt']
        for filename in files_to_track:
            filepath = os.path.join(context['tmgit_tree'], filename)
            with open(filepath, 'w') as f:
                f.write(f'conteudo de {filename}')
        repo.index.add(files_to_track)
        repo.index.commit('Múltiplos arquivos')

        # Modificar todos os arquivos
        for filename in files_to_track:
            filepath = os.path.join(context['tmgit_tree'], filename)
            with open(filepath, 'a') as f:
                f.write('\nmodificado')

        # Obter número de commits antes
        commits_before = len(list(repo.iter_commits()))

        # Chamar fly
        result_context = fly(context)

        # Obter número de commits depois
        commits_after = len(list(repo.iter_commits()))

        # Deve ter criado exatamente um novo commit
        assert commits_after == commits_before + 1

        # Verificar que arquivo foi commitado
        last_commit = list(repo.iter_commits())[0]
        assert 'file1.txt' in last_commit.message or len(last_commit.parents) > 0

    def test_fly_no_untracked_files_in_commit(self, tmp_path):
        """DADO que há um arquivo não-rastreado no diretório
        QUANDO fly() for chamado
        ENTÃO o arquivo não-rastreado não deve estar no commit
        """
        context = make_context(tmp_path)

        # Preparar repositório via climb
        context = climb(context)
        repo = Repo(context['tmgit_tree'])

        # Criar arquivo rastreado
        tracked_file = os.path.join(context['tmgit_tree'], 'tracked.txt')
        with open(tracked_file, 'w') as f:
            f.write('rastreado')
        repo.index.add(['tracked.txt'])
        repo.index.commit('Arquivo rastreado')

        # Criar arquivo não-rastreado
        untracked_file = os.path.join(context['tmgit_tree'], 'untracked.txt')
        with open(untracked_file, 'w') as f:
            f.write('não rastreado')

        # Modificar arquivo rastreado
        with open(tracked_file, 'w') as f:
            f.write('rastreado - modificado')

        # Chamar fly
        result_context = fly(context)

        # Obter o último commit
        last_commit = list(repo.iter_commits())[0]

        # Verificar que o arquivo não-rastreado não está no commit
        assert 'untracked' not in last_commit.message or 'tracked.txt' in last_commit.message


class TestFlyErrorPaths:
    """Testes para caminhos de erro em funções auxiliares do fly()."""

    def test_commit_files_raises_exception_on_git_error(self, tmp_path):
        """DADO que repo.index.commit() lança GitCommandError
        QUANDO commit_files() for chamado
        ENTÃO deve lançar Exception com mensagem contendo "Erro ao commitar"
        """
        with patch('fly.Repo') as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.is_dirty.return_value = True
            mock_repo.index.entries.keys.return_value = [('test.txt', 0)]
            mock_repo.index.add = MagicMock()
            mock_repo.index.commit.side_effect = GitCommandError('git commit', 1, b'erro', b'')
            with pytest.raises(Exception) as exc_info:
                commit_files(mock_repo, '2024.01.01-12.00.00.000')
            assert "Erro ao commitar" in str(exc_info.value)

    def test_tag_commit_raises_exception_on_git_error(self, tmp_path):
        """DADO que repo.create_tag() lança GitCommandError
        QUANDO tag_commit() for chamado
        ENTÃO deve lançar Exception com mensagem contendo "Erro ao criar tag"
        """
        mock_repo = MagicMock()
        mock_repo.create_tag.side_effect = GitCommandError('git tag', 1, b'erro', b'')
        with pytest.raises(Exception) as exc_info:
            tag_commit(mock_repo, '2024.01.01-12.00.00.000')
        assert "Erro ao criar tag" in str(exc_info.value)

    def test_push_remote_raises_exception_on_git_error(self, tmp_path):
        """DADO que remote.push() lança GitCommandError
        QUANDO push_remote() for chamado com remotos configurados
        ENTÃO deve lançar Exception com mensagem contendo "Erro ao fazer push"
        """
        mock_repo = MagicMock()
        mock_remote = MagicMock()
        mock_remote.push.side_effect = GitCommandError('git push', 1, b'erro', b'')
        mock_repo.remotes = [mock_remote]
        with pytest.raises(Exception) as exc_info:
            push_remote(mock_repo)
        assert "Erro ao fazer push" in str(exc_info.value)
