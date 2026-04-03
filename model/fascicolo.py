from dataclasses import dataclass


@dataclass
class Fascicolo:
    id: int
    anno: int
    ufficio: str

    def __str__(self):
        return f"Fasc.{self.id}/{self.anno}"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Fascicolo) and self.id == other.id
