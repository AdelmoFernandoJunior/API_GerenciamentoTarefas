# interface/user_controller.py
from usecase.addtask import CreateUserUseCase
from infra.logging.logger import ContextLogger, with_correlation

logger = ContextLogger()

@with_correlation
# Controller para criação de usuário
def create_user_controller(request_data: dict):
    logger.info("Iniciando processamento no Controller")
    # Extrair dados da requisição
    name = request_data.get("name")
    description = request_data.get("description")
    db_username = request_data.get("db_username")
    db_password = request_data.get("db_password")
    
    # Validar campos obrigatórios
    if not name or not description:
        logger.warning("Campos obrigatórios faltando")
        return {
            "statusCode": 400,
            "body": {"error": "Nome e descrição são campos obrigatórios"}
        }
    
    logger.info("Criando instância do UseCase")
    # UseCase para criação de usuárioS
    use_case = CreateUserUseCase(db_username=db_username, db_password=db_password)

    try:
        # Executa a lógica de criação de usuário
        result = use_case.execute(name, description)
        logger.info("Controller recebeu resultado do UseCase com sucesso")
        return {
            "statusCode": 200,
            "body": result
        }
    except ValueError as e:
        logger.warning(f"Erro de validação no Controller: {str(e)}")
        return {
            "statusCode": 400,
            "body": {"error": str(e)}
        }
    except PermissionError as e:
        logger.warning(f"Erro de autenticação no Controller: {str(e)}")
        return {
            "statusCode": 401,
            "body": {"error": str(e)}
        }
    except Exception as e:
        logger.error(f"Erro inesperado no Controller: {str(e)}")
        return {
            "statusCode": 500,
            "body": {"error": "Erro interno do servidor"}
        }
