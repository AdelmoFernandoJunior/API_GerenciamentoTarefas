import pytest
from domain.task import Task
from infra.db.authenticator import DatabaseAuthenticator
from infra.db.repository import TaskRepository
from infra.db.db import Database
from interface.user_controller import create_user_controller
from lambda_handler import lambda_handler

class TestIntegration:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Limpa o banco antes de cada teste"""
        Database.clear()
    
    @pytest.fixture
    def valid_credentials(self):
        return {
            "db_username": "admin",
            "db_password": "senha123"
        }
    
    @pytest.fixture
    def sample_task(self):
        return {
            "name": "Tarefa de Integração",
            "description": "Teste de integração completo do sistema"
        }
    
    def test_complete_flow_integration(self, valid_credentials, sample_task):
        """
        Teste de integração que verifica o fluxo completo da aplicação:
        1. Autenticação no banco
        2. Criação da task
        3. Persistência no banco
        4. Resposta do lambda
        """
        # Prepara o evento para o lambda
        event = {
            "body": {
                **valid_credentials,
                **sample_task
            }
        }

        # Executa o fluxo completo através do lambda_handler
        response = lambda_handler(event, None)

        # Verifica o status code da resposta
        assert response["statusCode"] == 200
        
        # Verifica se a resposta contém os dados corretos
        assert response["body"]["task"]["name"] == sample_task["name"]
        assert response["body"]["task"]["description"] == sample_task["description"]
        assert "correlation_id" in response["body"]
        
        # Verifica diretamente no banco se a task foi persistida
        db = Database(
            username=valid_credentials["db_username"],
            password=valid_credentials["db_password"]
        )
        saved_data = db.get_last_inserted()
        
        assert saved_data["name"] == sample_task["name"]
        assert saved_data["description"] == sample_task["description"]
    
    def test_database_connection_failure(self):
        """
        Teste de integração que verifica o comportamento do sistema
        quando há falha na conexão com o banco de dados
        """
        invalid_credentials = {
            "db_username": "invalid",
            "db_password": "wrong"
        }
        
        event = {
            "body": {
                **invalid_credentials,
                "name": "Test Task",
                "description": "Test Description"
            }
        }
        
        response = lambda_handler(event, None)
        
        # Verifica se o sistema retorna erro 401 para credenciais inválidas
        assert response["statusCode"] == 401
        assert "error" in response["body"]
        assert "correlation_id" in response["body"]
    
    def test_data_persistence_integration(self, valid_credentials):
        """
        Teste de integração focado na persistência dos dados,
        verificando se os dados são mantidos corretamente no banco
        """
        # Cria uma task diretamente
        task = Task("Teste Persistência", "Teste de persistência de dados")
        
        # Tenta salvar usando o repository
        repository = TaskRepository(
            username=valid_credentials["db_username"],
            password=valid_credentials["db_password"]
        )
        saved_task = repository.save(task)
        
        # Verifica se o salvamento retornou os dados corretos
        assert saved_task["name"] == "Teste Persistência"
        assert saved_task["description"] == "Teste de persistência de dados"
        assert saved_task["status"] == "pending"
        
        # Verifica se pode recuperar a task do banco
        db = Database(
            username=valid_credentials["db_username"],
            password=valid_credentials["db_password"]
        )
        saved_data = db.get_last_inserted()
        
        assert saved_data["name"] == "Teste Persistência"
        assert saved_data["description"] == "Teste de persistência de dados"
        assert saved_data["status"] == "pending"
    
    def test_concurrent_operations(self, valid_credentials):
        """
        Teste de integração que verifica o comportamento do sistema
        com operações concorrentes
        """
        import concurrent.futures
        import uuid
        
        def create_task(task_id):
            event = {
                "body": {
                    "db_username": valid_credentials["db_username"],
                    "db_password": valid_credentials["db_password"],
                    "name": f"Task Concorrente {task_id}",
                    "description": f"Descrição da task {task_id}"
                }
            }
            return lambda_handler(event, None)
        
        # Cria 5 tasks concorrentemente
        task_ids = [str(uuid.uuid4())[:8] for _ in range(5)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            responses = list(executor.map(create_task, task_ids))
        
        # Verifica se todas as operações foram bem-sucedidas
        for response in responses:
            assert response["statusCode"] == 200
            assert "correlation_id" in response["body"]
        
        # Verifica se todas as tasks foram salvas no banco
        db = Database(
            username=valid_credentials["db_username"],
            password=valid_credentials["db_password"]
        )
        saved_tasks = db.get_all_tasks()
        
        assert len(saved_tasks) >= len(task_ids)  # Pode haver outras tasks de outros testes
        
        # Verifica se encontra todas as tasks criadas
        created_tasks = [task for task in saved_tasks 
                        if any(f"Task Concorrente {task_id}" in task["name"] 
                              for task_id in task_ids)]
        assert len(created_tasks) == len(task_ids)