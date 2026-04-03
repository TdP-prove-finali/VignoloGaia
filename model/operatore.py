from dataclasses import dataclass


@dataclass
class Operatore:
    id: int
    nome: str
    sede: str
    ufficio: str

    def __str__(self):
        return f"{self.nome} ({self.sede})"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Operatore) and self.id == other.id
