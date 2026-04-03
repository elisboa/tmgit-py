from exceptions import TmgitError
from preflight import preflight
from climb import climb
from fly import fly
from land import land


def main():
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
