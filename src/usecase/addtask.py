# usecase/addtask.py
from domain.task import Task
from infra.db.repository import TaskRepository
from infra.db.authenticator import DatabaseAuthenticator
from infra.logging.logger import ContextLogger, with_correlation

logger = ContextLogger()

class CreateUserUseCase:
    # UseCase para criação de usuário
    def __init__(self, db_username: str = None, db_password: str = None):
        
        logger.info("Iniciando UseCase")
        # Autenticação no banco de dados
        self.authenticator = DatabaseAuthenticator(username=db_username, password=db_password)
        if not self.authenticator.authenticate():
            raise PermissionError("Credenciais inválidas")
        self.repository = TaskRepository(username=db_username, password=db_password)

    @with_correlation
    def execute(self, name: str, description: str):
        # Executa a lógica de criação de usuário
        if not name or not description:
            raise ValueError("Nome e descrição são obrigatórios")
        
        logger.info("Executando lógica de negócio")
        task = Task(name, description)
        logger.info(f"Task criada: {task.to_dict()}")
        result = self.repository.save(task)
        return {"status": "success", "task": result}
