# infra/db/repository.py
from infra.db.db import Database
from infra.logging.logger import ContextLogger, with_correlation

logger = ContextLogger()

class TaskRepository:
    # Repositório de tarefas
    def __init__(self, username: str = None, password: str = None):
        # Inicializa a conexão com o banco de dados
        logger.info("Iniciando Repository")
        # Autenticação no banco de dados
        # Se a autenticação falhar, uma PermissionError será levantada
        # Conexão com o banco de dados
        self.db = Database(username=username, password=password)

    @with_correlation
    # Salva a tarefa no banco de dados
    def save(self, task):
        # Valida a tarefa antes de salvar
        logger.info("Repository iniciando operação de save")
        result = self.db.insert(task.to_dict())
        logger.info(f"Repository finalizou operação de save: {result}")
        return result
