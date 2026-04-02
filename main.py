from preflight import preflight
from climb import climb
from fly import fly
from land import land


def main():
    # Inicia o fluxo do padrão modo-avião
    # Cada fase recebe e retorna o dicionário de contexto
    context = preflight()
    context = climb(context)
    context = fly(context)
    land(
        context['land_errlvl'],
        context['land_caller'],
        context['land_msg'],
        context['land_errmsg']
    )  # Encerra o programa com os valores finais do contexto


if __name__ == "__main__":
    main()
