# lambda_handler.py
from interface.user_controller import create_user_controller
from infra.logging.logger import ContextLogger, with_correlation

logger = ContextLogger()

@with_correlation
def lambda_handler(event, context):
    # Handler principal da AWS Lambda
    # Recebe eventos e contextos da AWS
    logger.info("Lambda recebeu a requisição")
    body = event.get("body", {})
    try:
        response = create_user_controller(body)
        logger.info("Lambda recebeu a resposta do controller")
    except (ValueError, PermissionError) as e:
        # Retorna diretamente o erro tratado do controller
        if isinstance(e, ValueError):
            logger.warning(f"Erro de validação: {str(e)}")
            response = {
                "statusCode": 400,
                "body": {"error": str(e)}
            }
        else:
            logger.warning(f"Erro de autenticação: {str(e)}")
            response = {
                "statusCode": 401,
                "body": {"error": str(e)}
            }
    except Exception as e:
        logger.error(f"Erro inesperado no Lambda: {str(e)}")
        response = {
            "statusCode": 500,
            "body": {"error": "Erro interno do servidor"}
        }
    
    # Adiciona o correlation_id na resposta
    if isinstance(response.get('body'), dict):
        response['body']['correlation_id'] = logger.correlation_id
    
    return response