"""Testes para a função preflight() do módulo preflight.py.
Seguindo a metodologia SDD — cada teste deriva de uma especificação DADO/QUANDO/ENTÃO.
"""

import pytest
import sys
import os
import shutil
from datetime import datetime
from preflight import preflight
from exceptions import PreflightError, ClimbError, FlyError, TmgitError


class TestPreflightErrorConditions:
    """Testes para condições de erro que causam encerramento via land()."""

    def test_preflight_exits_when_no_arguments(self, monkeypatch):
        """DADO que nenhum argumento foi passado (sys.argv sem argumentos)
        QUANDO preflight() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        # Simular sys.argv sem argumentos (apenas o nome do script)
        monkeypatch.setattr(sys, 'argv', ['tmgit.py'])

        with pytest.raises(PreflightError):
            preflight()

    def test_preflight_exits_when_directory_does_not_exist(self, monkeypatch):
        """DADO que o diretório passado não existe
        QUANDO preflight() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        # Simular sys.argv com um diretório que não existe
        nonexistent_dir = '/this/path/definitely/does/not/exist/tmgit-test'
        monkeypatch.setattr(sys, 'argv', ['tmgit.py', nonexistent_dir])

        with pytest.raises(PreflightError):
            preflight()

    def test_preflight_exits_when_directory_not_writable(self, monkeypatch, tmp_path):
        """DADO que o diretório existe mas não tem permissão de escrita
        QUANDO preflight() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        import os
        if os.getuid() == 0:
            pytest.skip("Teste não aplicável rodando como root")
        # Criar um diretório temporário sem permissão de escrita
        test_dir = tmp_path / "readonly"
        test_dir.mkdir()
        test_dir.chmod(0o555)  # Apenas leitura

        try:
            monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

            with pytest.raises(PreflightError):
                preflight()
        finally:
            # Restaurar permissões para cleanup
            test_dir.chmod(0o755)

    def test_preflight_exits_when_git_not_installed(self, monkeypatch, tmp_path):
        """DADO que o git não está instalado (shutil.which retorna None)
        QUANDO preflight() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        test_dir = tmp_path / "with_git"
        test_dir.mkdir()

        # Simular git não encontrado
        monkeypatch.setattr(shutil, 'which', lambda x: None)
        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        with pytest.raises(PreflightError):
            preflight()

    def test_preflight_exits_when_lock_file_exists(self, monkeypatch, tmp_path):
        """DADO que existe um arquivo index.lock em tmgit_dir
        QUANDO preflight() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        test_dir = tmp_path / "with_lock"
        test_dir.mkdir()

        # Criar a estrutura de diretórios e o arquivo de lock
        tmgit_subdir = test_dir / '.tmgit' / '.git'
        tmgit_subdir.mkdir(parents=True, exist_ok=True)
        lock_file = tmgit_subdir / 'index.lock'
        lock_file.write_text('lock')

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        with pytest.raises(PreflightError):
            preflight()


class TestPreflightSuccessful:
    """Testes para fluxo bem-sucedido com todos os requisitos satisfeitos."""

    def test_preflight_returns_context_dict(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO deve retornar dicionário com as chaves esperadas:
        tmgit_tree, tmgit_dir, commit_date, branch_name,
        land_errlvl, land_caller, land_msg, land_errmsg
        """
        test_dir = tmp_path / "success"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        # Verificar que é um dicionário
        assert isinstance(context, dict)

        # Verificar que todas as chaves obrigatórias estão presentes
        expected_keys = {
            'tmgit_tree',
            'tmgit_dir',
            'commit_date',
            'branch_name',
            'land_errlvl',
            'land_caller',
            'land_msg',
            'land_errmsg',
            'command',
            'command_target'
        }
        assert set(context.keys()) == expected_keys


class TestPreflightContextVariables:
    """Testes para validação das variáveis de contexto retornadas."""

    def test_preflight_tmgit_dir_path_format(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO tmgit_dir deve ser tmgit_tree + '/.tmgit/.git'
        """
        test_dir = tmp_path / "path_test"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        expected_tmgit_dir = os.path.join(str(test_dir), '.tmgit', '.git')
        assert context['tmgit_dir'] == expected_tmgit_dir

    def test_preflight_tmgit_tree_matches_argument(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO tmgit_tree deve ser exatamente o argumento passado
        """
        test_dir = tmp_path / "tree_test"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        assert context['tmgit_tree'] == str(test_dir)

    def test_preflight_land_errlvl_is_zero_on_success(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO land_errlvl deve ser 0
        """
        test_dir = tmp_path / "errlvl_test"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        assert context['land_errlvl'] == 0

    def test_preflight_land_caller_is_preflight(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO land_caller deve ser "preflight"
        """
        test_dir = tmp_path / "caller_test"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        assert context['land_caller'] == "preflight"

    def test_preflight_land_errmsg_is_empty_on_success(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO land_errmsg deve estar vazio
        """
        test_dir = tmp_path / "errmsg_test"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        assert context['land_errmsg'] == ""


class TestPreflightDateFormat:
    """Testes para validação dos formatos de data e hora."""

    def test_preflight_branch_name_format_is_yyyymmdd(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO branch_name deve estar no formato AAAA.MM.DD (YYYY.MM.DD)
        """
        test_dir = tmp_path / "branch_format_test"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        # Validar formato YYYY.MM.DD
        branch_name = context['branch_name']
        parts = branch_name.split('.')
        assert len(parts) == 3, f"branch_name deve ter 3 partes separadas por '.', got: {branch_name}"

        year, month, day = parts
        assert len(year) == 4 and year.isdigit(), f"Ano inválido: {year}"
        assert len(month) == 2 and month.isdigit() and 1 <= int(month) <= 12, f"Mês inválido: {month}"
        assert len(day) == 2 and day.isdigit() and 1 <= int(day) <= 31, f"Dia inválido: {day}"

    def test_preflight_commit_date_format_is_yyyymmdd_hhmmss(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO commit_date deve estar no formato AAAA.MM.DD-HH.MM.SS.mmm
        """
        test_dir = tmp_path / "commit_date_format_test"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        # Validar formato YYYY.MM.DD-HH.MM.SS.mmm
        commit_date = context['commit_date']

        # Deve conter hífen separando data e hora
        assert '-' in commit_date, f"commit_date deve conter '-': {commit_date}"

        date_part, time_part = commit_date.split('-')

        # Validar data: YYYY.MM.DD
        date_parts = date_part.split('.')
        assert len(date_parts) == 3, f"Data deve ter 3 partes: {date_part}"

        # Validar hora: HH.MM.SS.mmm
        time_parts = time_part.split('.')
        assert len(time_parts) == 4, f"Hora deve ter 4 partes (HH.MM.SS.mmm): {time_part}"

        # Validar que todos são numéricos e têm tamanho correto
        year, month, day = date_parts
        assert year.isdigit() and len(year) == 4
        assert month.isdigit() and len(month) == 2
        assert day.isdigit() and len(day) == 2

        hour, minute, second, millis = time_parts
        assert hour.isdigit() and len(hour) == 2
        assert minute.isdigit() and len(minute) == 2
        assert second.isdigit() and len(second) == 2
        assert millis.isdigit() and len(millis) == 3

    def test_preflight_dates_are_current(self, monkeypatch, tmp_path):
        """DADO que todos os requisitos estão satisfeitos
        QUANDO preflight() for chamado
        ENTÃO as datas devem corresponder ao momento atual (com tolerância)
        """
        test_dir = tmp_path / "current_date_test"
        test_dir.mkdir()

        # Capturar tempo antes da execução
        before = datetime.now()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        # Capturar tempo após a execução
        after = datetime.now()

        # Verificar que branch_name corresponde a uma data entre before e after
        branch_name = context['branch_name']
        branch_date = datetime.strptime(branch_name, '%Y.%m.%d')

        # A data deve ser hoje
        assert branch_date.date() >= before.date()
        assert branch_date.date() <= after.date()


class TestPreflightCommands:
    """Testes para detecção de comandos opcionais em preflight()."""

    def test_preflight_exits_on_invalid_command(self, monkeypatch, tmp_path):
        """DADO que um comando inválido é passado (ex: 'version-all')
        QUANDO preflight() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        test_dir = tmp_path / "invalid_command"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir), 'version-all'])

        with pytest.raises(PreflightError):
            preflight()

    def test_preflight_exits_on_add_file_without_target(self, monkeypatch, tmp_path):
        """DADO que 'add-file' é passado sem arquivo alvo (apenas dois argumentos)
        QUANDO preflight() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        test_dir = tmp_path / "add_file_no_target"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir), 'add-file'])

        with pytest.raises(PreflightError):
            preflight()

    def test_preflight_exits_on_del_file_without_target(self, monkeypatch, tmp_path):
        """DADO que 'del-file' é passado sem arquivo alvo (apenas dois argumentos)
        QUANDO preflight() for chamado
        ENTÃO deve encerrar com sys.exit(1)
        """
        test_dir = tmp_path / "del_file_no_target"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir), 'del-file'])

        with pytest.raises(PreflightError):
            preflight()

    def test_preflight_sets_command_add_file_with_target(self, monkeypatch, tmp_path):
        """DADO que 'add-file' é passado com arquivo alvo
        QUANDO preflight() for chamado
        ENTÃO context['command'] deve ser 'add-file'
        E context['command_target'] deve ser o arquivo passado
        """
        test_dir = tmp_path / "add_file_with_target"
        test_dir.mkdir()
        target_file = "example.txt"

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir), 'add-file', target_file])

        context = preflight()

        assert context['command'] == 'add-file'
        assert context['command_target'] == target_file

    def test_preflight_sets_command_push_remote_without_target(self, monkeypatch, tmp_path):
        """DADO que 'push-remote' é passado (sem arquivo alvo)
        QUANDO preflight() for chamado
        ENTÃO context['command'] deve ser 'push-remote'
        E context['command_target'] deve ser None
        """
        test_dir = tmp_path / "push_remote"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir), 'push-remote'])

        context = preflight()

        assert context['command'] == 'push-remote'
        assert context['command_target'] is None

    def test_preflight_sets_command_none_when_no_command(self, monkeypatch, tmp_path):
        """DADO que nenhum comando é passado
        QUANDO preflight() for chamado
        ENTÃO context['command'] deve ser None
        E context['command_target'] deve ser None
        """
        test_dir = tmp_path / "no_command"
        test_dir.mkdir()

        monkeypatch.setattr(sys, 'argv', ['tmgit.py', str(test_dir)])

        context = preflight()

        assert context['command'] is None
        assert context['command_target'] is None
