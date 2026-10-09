import pytest
from unittest.mock import MagicMock
from infra.db.repository import TaskRepository
from domain.task import Task

@pytest.fixture
def mock_db(mocker):
    return mocker.patch('infra.db.repository.Database', autospec=True)

def test_repository_save_success(mock_db):
    # Configurar o mock do banco de dados
    db_instance = mock_db.return_value
    db_instance.insert.return_value = True
    
    # Criar repositório e tarefa
    repo = TaskRepository(username="admin", password="senha123")
    task = Task("Teste", "Descrição de teste")
    
    # Testar salvamento
    result = repo.save(task)
    assert result == True
    db_instance.insert.assert_called_once_with(task.to_dict())

def test_repository_save_failure(mock_db):
    # Configurar o mock do banco de dados para falhar
    db_instance = mock_db.return_value
    db_instance.insert.return_value = False
    
    # Criar repositório e tarefa
    repo = TaskRepository(username="admin", password="senha123")
    task = Task("Teste", "Descrição de teste")
    
    # Testar salvamento com falha
    result = repo.save(task)
    assert result == False
