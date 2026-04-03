"""Exceções customizadas do projeto tmgit-py.

Define uma hierarquia de exceções que permite que cada fase
(preflight, climb, fly) comunique erros ao main.py, possibilitando
chamadas apropriadas a land() com as informações de contexto corretas.
"""


class TmgitError(Exception):
    """Exceção base do projeto tmgit-py.

    Carrega as informações necessárias para que o main.py
    possa chamar land() com os dados corretos: message (mensagem
    da fase), caller (função que lançou o erro) e error_message
    (detalhes do erro).

    Atributos:
        message (str): Mensagem de status da fase.
        caller (str): Nome da função que lançou o erro.
        error_message (str): Detalhes específicos do erro.
    """

    def __init__(self, message: str, caller: str, error_message: str = ""):
        """Inicializa exceção TmgitError.

        Args:
            message (str): Mensagem descritiva do erro.
            caller (str): Nome da fase/função que lançou o erro.
            error_message (str, optional): Detalhes técnicos do erro. Padrão: "".
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
