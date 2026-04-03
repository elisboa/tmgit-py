"""Testes para o módulo main.py.
Seguindo metodologia SDD com cenários DADO/QUANDO/ENTÃO.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock, call
from main import main


class TestMainSuccessFlow:
    """Testes para o fluxo normal de main()."""

    def test_main_calls_phases_in_order_with_context_flow(self):
        """DADO todas fases bem-sucedidas
        QUANDO main() for chamado
        ENTÃO preflight(), climb(), fly() e land() são invocados em ordem
        """
        mock_context = {
            'land_errlvl': 0,
            'land_caller': 'fly',
            'land_msg': 'Fly concluído com sucesso',
            'land_errmsg': ''
        }

        with patch('main.preflight') as mock_preflight, \
             patch('main.climb') as mock_climb, \
             patch('main.fly') as mock_fly, \
             patch('main.land') as mock_land:

            mock_preflight.return_value = mock_context
            mock_climb.return_value = mock_context
            mock_fly.return_value = mock_context
            mock_land.side_effect = SystemExit(0)

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
            mock_preflight.assert_called_once()
            mock_climb.assert_called_once_with(mock_context)
            mock_fly.assert_called_once_with(mock_context)
            mock_land.assert_called_once_with(
                mock_context['land_errlvl'],
                mock_context['land_caller'],
                mock_context['land_msg'],
                mock_context['land_errmsg']
            )

    def test_main_exits_zero_on_success(self):
        """DADO todas fases bem-sucedidas
        QUANDO main() for chamado
        ENTÃO deve encerrar com sys.exit(0)
        """
        mock_context = {
            'land_errlvl': 0,
            'land_caller': 'fly',
            'land_msg': 'Fly concluído com sucesso',
            'land_errmsg': ''
        }

        with patch('main.preflight') as mock_preflight, \
             patch('main.climb') as mock_climb, \
             patch('main.fly') as mock_fly, \
             patch('main.land') as mock_land:

            mock_preflight.return_value = mock_context
            mock_climb.return_value = mock_context
            mock_fly.return_value = mock_context
            mock_land.side_effect = SystemExit(0)

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0


class TestMainErrorFlow:
    """Testes para fluxo de erro de main()."""

    def test_main_land_called_with_error_level_from_preflight(self):
        """DADO preflight retorna land_errlvl=1
        QUANDO main() for chamado
        ENTÃO land() é chamado com error_level=1
        """
        mock_context = {
            'land_errlvl': 1,
            'land_caller': 'preflight',
            'land_msg': 'Pré-voo falhou',
            'land_errmsg': 'erro precoce'
        }

        with patch('main.preflight') as mock_preflight, \
             patch('main.climb') as mock_climb, \
             patch('main.fly') as mock_fly, \
             patch('main.land') as mock_land:

            mock_preflight.return_value = mock_context
            mock_climb.return_value = mock_context
            mock_fly.return_value = mock_context
            mock_land.side_effect = SystemExit(1)

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            mock_land.assert_called_once_with(
                1,
                'preflight',
                'Pré-voo falhou',
                'erro precoce'
            )
