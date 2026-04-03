"""Fase 1 - verificações pré-voo (preflight) para tmgit-py.
Este módulo contém validações e inicialização de variáveis.
Nenhuma alteração no ambiente é feita aqui.
"""

import sys
import os
import shutil
import datetime
from land import land


def preflight():
    """Executa verificações pré-voo e inicializa variáveis de contexto.

    Recebe argumentos da linha de comando, valida o diretório e git,
    verifica arquivo de lock e retorna dicionário de contexto.

    Returns:
        dict: Dicionário com variáveis de contexto inicializadas.
    """

    # Obter argumentos passados via linha de comando
    args = sys.argv[1:]

    # Verificar se pelo menos um argumento foi passado
    if len(args) < 1:
        land(1, "preflight", f"Número de parâmetros passados: {len(args)}",
             "Uso: tmgit.py [diretório a ser versionado]")

    tmgit_tree = args[0]

    # Inicializar tmgit_dir
    tmgit_dir = os.path.join(tmgit_tree, '.tmgit', '.git')

    # Verificar se o diretório existe
    if not os.path.exists(tmgit_tree):
        land(1, "preflight", f"Verificando diretório {tmgit_tree}",
             "Diretório não existe")

    # Verificar se o diretório é acessível (leitura e escrita)
    if not os.access(tmgit_tree, os.R_OK | os.W_OK):
        land(1, "preflight", f"Verificando acesso ao diretório {tmgit_tree}",
             "Diretório não acessível")

    # Verificar se o binário do git está disponível
    git_path = shutil.which('git')
    if not git_path:
        land(1, "preflight", "Verificação do executável do git",
             "Arquivo executável do git não encontrado")

    # Verificar se existe arquivo de lock
    lock_file = os.path.join(tmgit_dir, 'index.lock')
    if os.path.exists(lock_file):
        land(1, "preflight", "Verificando se o arquivo de lock existe",
             "Arquivo de lock já existe")

    # Inicializar variáveis de contexto
    # tmgit_dir já foi inicializado acima

    # Obter data e hora atual para commit e branch
    now = datetime.datetime.now()
    commit_date = now.strftime('%Y.%m.%d-%H.%M.%S') + f".{now.microsecond // 1000:03d}"
    branch_name = now.strftime('%Y.%m.%d')

    # Variáveis de encerramento
    land_errlvl = 0
    land_caller = "preflight"
    land_msg = "Preflight concluído com sucesso"
    land_errmsg = ""

    # Detectar argumento opcional de comando e alvo
    valid_commands = ['add-file', 'del-file', 'push-remote']

    command_detected = None
    command_target_detected = None

    if len(args) > 1:
        command = args[1]
        target = args[2] if len(args) > 2 else None

        # Validar comando
        if command not in valid_commands:
            land(1, "preflight", f"Comando inválido: {command}",
                 "Comandos válidos: add-file, del-file, push-remote")

        # Verificar comando que requer target
        if command in ['add-file', 'del-file'] and len(args) == 2:
            land(1, "preflight", f"Comando {command} requer arquivo alvo",
                 "Uso: tmgit.py [diretório] add-file <arquivo> | del-file <arquivo>")

        command_detected = command
        command_target_detected = target
    else:
        command_detected = None
        command_target_detected = None

    # Retornar dicionário de contexto
    context = {
        'tmgit_tree': tmgit_tree,
        'tmgit_dir': tmgit_dir,
        'commit_date': commit_date,
        'branch_name': branch_name,
        'land_errlvl': land_errlvl,
        'land_caller': land_caller,
        'land_msg': land_msg,
        'land_errmsg': land_errmsg,
        'command': command_detected,
        'command_target': command_target_detected
    }

    return context
