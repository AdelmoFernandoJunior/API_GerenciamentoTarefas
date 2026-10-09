import logging
import uuid
from functools import wraps
from contextvars import ContextVar

class ContextLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        self.logger = logging.getLogger('to-do-app')
        self.logger.setLevel(logging.INFO)
        
        # Configura o formato do log com correlation_id
        formatter = logging.Formatter(
            '%(asctime)s [%(correlation_id)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self._correlation_id = ContextVar('correlation_id', default=None)

    @property
    def correlation_id(self) -> str:
        return self._correlation_id.get() or 'NO_CORRELATION_ID'

    @correlation_id.setter
    def correlation_id(self, value: str):
        self._correlation_id.set(value)

    def _log(self, level: int, message: str, *args, **kwargs):
        extra = {'correlation_id': self.correlation_id}
        self.logger.log(level, message, *args, extra=extra, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

def with_correlation(f):
    """Decorator para adicionar correlation_id automaticamente"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        logger = ContextLogger()
        current_correlation = logger.correlation_id
        
        if current_correlation == 'NO_CORRELATION_ID':
            logger.correlation_id = str(uuid.uuid4())
            
        try:
            return f(*args, **kwargs)
        finally:
            if current_correlation == 'NO_CORRELATION_ID':
                logger.correlation_id = None
            
    return wrapper
