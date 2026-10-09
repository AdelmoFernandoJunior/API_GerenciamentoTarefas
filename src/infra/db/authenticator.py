# infra/db/authenticator.py
from infra.logging.logger import ContextLogger, with_correlation

logger = ContextLogger()

class DatabaseAuthenticator:
    def __init__(self, username: str = None, password: str = None):
        # Simula um sistema de autenticação simples
        self._username = username
        self._password = password
        self._is_authenticated = False
        logger.info("Authenticator inicializado")
    
    @with_correlation
    def authenticate(self) -> bool:
        #
        logger.info("Iniciando processo de autenticação")
        if not self._username or not self._password:
            logger.warning("Tentativa de autenticação sem credenciais")
            return False

        if self._username == "admin" and self._password == "senha123":
            self._is_authenticated = True
            logger.info("Autenticação realizada com sucesso")
            return True
            
        logger.warning(f"Falha na autenticação para usuário: {self._username}")
        self._is_authenticated = False
        return False
    
    @property
    def is_authenticated(self) -> bool:
        # Retorna o estado de autenticação
        return self._is_authenticated
    
    @with_correlation
    def validate_connection(self):
        # Valida se a conexão está autenticada antes de operações sensíveis
        if not self.is_authenticated:
            logger.error("Tentativa de operação sem autenticação")
            raise PermissionError("É necessário autenticar antes de usar o banco de dados!")
