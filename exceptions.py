"""Exceções customizadas do projeto tmgit-py.

Define uma hierarquia de exceções que permite que cada fase
(preflight, climb, fly) comunique erros ao main.py, possibilitando
chamadas apropriadas a land() com as informações de contexto corretas.
"""


class TmgitError(Exception):
    """Exceção base do projeto tmgit-py.

    Carrega as informações necessárias para que o main.py possa chamar land()
    com os dados corretos. Define a hierarquia de exceções que conecta as quatro
    fases do padrão modo-avião com o encerramento centralizado.

    **Semântica das variáveis:**

    - `message`: Descrição da **ação/intenção** que foi tentada (resumida, nível alto).
      Preenchida DURANTE a execução, descreve o que estava sendo feito.
      Exemplo: "Verificando diretório /home/user"

    - `error_message`: Descrição **detalhada do resultado** (resultado da ação executada).
      Preenchida APÓS a execução, pode ser sucesso ou erro específico.
      Exemplo: "Diretório não existe" (erro) ou "Diretório OK" (sucesso)

    - `caller`: Identificação da função que lançou o erro (rastreio de stack).
      Exemplo: "preflight", "climb", "fly"

    **Padrão de preenchimento:**

    ```python
    # Em ERRO:
    raise PreflightError(
        message="Verificando diretório /home/user",  # O que tentava fazer
        caller="preflight",                          # Quem lançou
        error_message="Diretório não existe")        # O que aconteceu

    # Em SUCESSO (preenchido em land()):
    context['land_msg'] = "Preflight concluído com sucesso"
    context['land_errlvl'] = 0
    # error_message deixada vazia (não é preenchida em sucessos)
    ```

    **Nota histórica:** Esta estrutura é herdada do projeto shell original (tmgit)
    onde LAND_MSG e LAND_ERRMSG SEMPRE descrevem estado.
    Apesar do nome "error_message", ela significa "detalhes do resultado",
    não "exclusivamente erros".

    Atributos:
        message (str): Descrição da ação/intenção sendo tentada.
        caller (str): Nome da fase/função que lançou a exceção.
        error_message (str): Detalhes específicos do resultado (erro ou sucesso).
    """

    def __init__(self, message: str, caller: str, error_message: str = ""):
        """Inicializa exceção TmgitError.

        Args:
            message (str): Descrição da ação que foi tentada (ex: "Validando argumentos").
            caller (str): Nome da fase/função que lançou a exceção (ex: "preflight").
            error_message (str, optional): Detalhe específico do resultado ou erro.
                                          Padrão: "" (vazio).
        """
        self.message = message
        self.caller = caller
        self.error_message = error_message
        super().__init__(message)


class PreflightError(TmgitError):
    """Erro ocorrido na fase preflight.

    Lançada quando a validação de pré-voo falha: argumentos inválidos,
    diretório inexistente, git não instalado, ou lock file presente.
    """
    pass


class ClimbError(TmgitError):
    """Erro ocorrido na fase climb.

    Lançada quando a preparação do repositório falha: não é possível
    criar o diretório .tmgit, inicializar git, criar branch ou gitignore.
    """
    pass


class FlyError(TmgitError):
    """Erro ocorrido na fase fly.

    Lançada quando as operações principales falham: commit, tag,
    push para remotos, ou comandos específicos como add-file/del-file.
    """
    pass
