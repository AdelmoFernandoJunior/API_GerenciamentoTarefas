# domain/task.py
class Task:
    def __init__(self, name: str, description: str):
        # Valida o nome da tarefa
        if not name:
            raise ValueError("Nome da tarefa é obrigatório")
        # Inicializa os atributos da tarefa
        self.name = name
        self.description = description or ""
        self.status = "pending"

    def to_dict(self):
        # Converte a tarefa para um dicionário
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status
        }
