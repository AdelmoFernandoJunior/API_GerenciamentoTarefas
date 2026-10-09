# infra/db/db.py
import threading

from infra.db.authenticator import DatabaseAuthenticator
from infra.logging.logger import ContextLogger, with_correlation

logger = ContextLogger()

class Database:
    _tasks = []
    _lock = threading.RLock()
    
    @classmethod
    def clear(cls):
        """Limpa todas as tasks do banco. Usado principalmente para testes."""
        with cls._lock:
            cls._tasks = []

    def __init__(self, username: str = None, password: str = None):
        with self._lock:
            logger.info("Inicializando conexão com o banco de dados")
            self._authenticator = DatabaseAuthenticator(username, password)
            self._connect()
        
    def _connect(self):
        """Conecta e autentica no banco de dados"""
        logger.info("Tentando autenticar no banco de dados")
        if self._authenticator.authenticate():
            logger.info("Conexão com o banco de dados estabelecida com sucesso!")
        else:
            logger.error("Falha na autenticação do banco de dados")
            raise PermissionError("Não foi possível conectar ao banco de dados. Verifique suas credenciais.")
        
    @with_correlation
    def insert(self, task_data: dict):
        # Insere uma nova tarefa no banco de dados
        self._authenticator.validate_connection()
        logger.info(f"Salvando task no banco: {task_data}")
        with self._lock:
            task_id = len(Database._tasks) + 1
            task_data["id"] = task_id
            Database._tasks.append(task_data.copy())  # Salva uma cópia para evitar modificações externas
        logger.info(f"Task salva com sucesso. ID: {task_id}")
        return task_data
    
    @with_correlation
    def get_last_inserted(self):
        """Retorna a última task inserida no banco"""
        self._authenticator.validate_connection()
        if not Database._tasks:
            return None
        return Database._tasks[-1].copy()  # Retorna uma cópia para evitar modificações externas
    
    @with_correlation
    def get_all_tasks(self):
        """Retorna todas as tasks do banco"""
        self._authenticator.validate_connection()
        return [task.copy() for task in Database._tasks]  # Retorna cópias para evitar modificações externas
