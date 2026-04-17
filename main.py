from exceptions import TmgitError
from preflight import preflight
from climb import climb
from fly import fly
from land import land


def main():
    """Orquestra as quatro fases do padrão modo-avião: preflight → climb → fly → land.

    **Fluxo em SUCESSO:**
    1. preflight() valida ambiente e retorna contexto inicial
    2. climb() prepara repositório e atualiza contexto
    3. fly() executa lógica principal e atualiza contexto
    4. land() exibe mensagens e encerra com código 0

    **Fluxo em ERRO:**
    Qualquer fase pode lançar TmgitError, que é capturada e passada ao land()
    com código de erro 1. O main garante que SEMPRE land() é chamado.

    **Contexto compartilhado (dicionário):**
    - Preenchido inicialmente por preflight()
    - Modificado por climb() e fly()
    - Lido por land() ao final
    - Contém: tmgit_tree, tmgit_dir, commit_date, branch_name,
             command, land_errlvl, land_caller, land_msg, land_errmsg

    **Garantias:**
    - As quatro fases sempre executam em ordem (nunca desviar antes de fly)
    - land() é SEMPRE chamada, em sucesso ou erro
    - Exceções TmgitError são capturadas e convertidas a pouso de emergência
    """
    # Inicia o fluxo do padrão modo-avião
    # Cada fase recebe e retorna o dicionário de contexto
    try:
        # Fase 1: validações pré-voo
        context = preflight()
        # Fase 2: preparação do repositório
        context = climb(context)
        # Fase 3: lógica principal (commit, tag, push)
        context = fly(context)
        # Pouso bem-sucedido — encerrando com dados finais
        land(
            context['land_errlvl'],
            context['land_caller'],
            context['land_msg'],
            context['land_errmsg']
        )
    except TmgitError as e:
        # Pouso de emergência — alguma fase reportou erro
        land(1, e.caller, e.message, e.error_message)

if __name__ == "__main__":
    main()
