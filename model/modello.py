import networkx as nx
import csv
import requests
import openai
import groq
from datetime import datetime

from database.DAO import DAO
from model.operatore import Operatore
from model.fascicolo import Fascicolo

#variabile globale che rappresenta il nome della tabella utilizzata dall' AI assistant
TABLE_NAME = "digitalizzazione"


class Model:
    def __init__(self):
        self._grafo = nx.Graph()
        # CSV import state
        self._csv_rows = []
        self._csv_total = 0
        # AI Assistant state
        self._schema_info = None

    def get_sedi(self) -> list[str]:
        return DAO.get_sedi()


    # AI ASSISTANT LOGIC

    def get_schema_info(self) -> str:
        """Ritorna lo schema della tabella """
        if self._schema_info is None:
            self._schema_info = DAO.get_table_schema()
        return self._schema_info

    def load_ai_models(self, provider: str, api_key: str) -> list:
        """Carica i modelli disponibili dal provider selezionato."""
        models = []
        try:
            if "Ollama" in provider:
                r = requests.get("http://localhost:11434/api/tags", timeout=3)
                models = [m["name"] for m in r.json().get("models", [])]
            elif "LM Studio" in provider:
                r = requests.get("http://localhost:1234/v1/models", timeout=3)
                models = [m["id"] for m in r.json().get("data", [])]
            elif "OpenAI" in provider:
                client = openai.OpenAI(api_key=api_key)
                models = [m.id for m in client.models.list() if "gpt" in m.id]
            elif "Groq" in provider:
                client = groq.Groq(api_key=api_key)
                models = [m.id for m in client.models.list().data]
        except Exception as e:
            raise e
        return models

    def query_ai(self, provider: str, model: str, api_key: str, prompt: str, is_sql: bool = True) -> str:
        """Interroga l'AI e ritorna la risposta."""
        schema = self.get_schema_info()
        sys_msg = f"Expert SQL Analyst. Table: {TABLE_NAME}. Schema: {schema}. Response: {'RAW SQL' if is_sql else 'Italian summary'}"
        
        try:
            if "Ollama" in provider:
                client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            elif "LM Studio" in provider:
                client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="lm")
            elif "Groq" in provider:
                client = groq.Groq(api_key=api_key)
            else:
                client = openai.OpenAI(api_key=api_key)
            
            resp = client.chat.completions.create(
                model=model, 
                messages=[
                    {"role": "system", "content": sys_msg}, 
                    {"role": "user", "content": prompt}
                ]
            )
            result = resp.choices[0].message.content
            print(f"--- [DEBUG IA] ---\nIN: {prompt}\nOUT: {result}\n---", flush=True)
            return result
        except Exception as e:
            raise e

    def execute_ai_query(self, sql: str) -> list:
        """Esegue una query SQL sul database."""
        return DAO.execute_ai_query(sql)


    # GRAFICI LOGIC

    def get_chart_data(self, chart_type: str) -> list:
        """Ritorna i dati per il grafico selezionato."""
        if chart_type == "pages_per_operator":
            return DAO.get_pages_per_operator(5)
        elif chart_type == "pages_per_sede":
            return DAO.get_pages_per_sede()
        elif chart_type == "pages_per_month":
            return DAO.get_pages_per_month()
        elif chart_type == "pages_per_ufficio":
            return DAO.get_pages_per_ufficio()
        elif chart_type == "top_fascicoli":
            return DAO.get_top_fascicoli(5)
        else:
            return []

    def get_stats_totals(self) -> dict:
        """Ritorna le statistiche totali per le card."""
        return DAO.get_stats_totals()


    # CSV IMPORT LOGIC

    def load_csv_file(self, file_path: str) -> int:
        """Carica il file CSV in memoria e ritorna il numero di righe."""
        self._csv_rows = []
        field_names = [
            "Sede", "Ufficio", "Attivita", "Nome_operatore", "ID_Operatore",
            "ID_attivita", "Data_Attivita", "ID_Fascicolo", "Anno_fascicolo",
            "conta_pagine_giorno"
        ]
        
        with open(file_path, mode='r', encoding='utf-8-sig', newline='') as f:
            line = f.readline()
            delim = ';' if ';' in line else ','
            f.seek(0)
            

            if "Sede" in line:
                reader = csv.DictReader(f, delimiter=delim)
            else:
                f.seek(0)
                reader = csv.DictReader(f, delimiter=delim, fieldnames=field_names)
            
            self._csv_rows = list(reader)
            self._csv_total = len(self._csv_rows)
        
        return self._csv_total

    def format_date(self, raw_date: str) -> str:
        """Restituisce la data come stringa pulita (il campo DB è VARCHAR)."""
        if not raw_date:
            return None
        # Rimuove spazi e caratteri invisibili (es. \r da Windows)
        clean_date = raw_date.strip()
        # Se dopo lo strip è vuota, ritorna None
        return clean_date if clean_date else None

    def get_csv_rows(self) -> list:
        """Ritorna le righe CSV caricate."""
        return self._csv_rows


    def _to_int(self, value) -> int | None:
        """Converte un valore in intero, ritorna None se vuoto o non valido."""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def import_csv_row(self, index: int) -> bool:
        """Importa una singola riga CSV nel database."""
        if index >= len(self._csv_rows):
            return False
        row = self._csv_rows[index]
        
        # Prepara i dati convertendo i campi numerici
        clean_row = {
            "Sede": row.get("Sede"),
            "Ufficio": row.get("Ufficio"),
            "Attivita": row.get("Attivita"),
            "Nome_operatore": row.get("Nome_operatore"),
            "ID_Operatore": self._to_int(row.get("ID_Operatore")),
            "ID_attivita": self._to_int(row.get("ID_attivita")),
            "ID_Fascicolo": self._to_int(row.get("ID_Fascicolo")),
            "Anno_fascicolo": self._to_int(row.get("Anno_fascicolo")),
            "conta_pagine_giorno": self._to_int(row.get("conta_pagine_giorno"))
        }
        
        fmt_date = self.format_date(row.get("Data_Attivita", ""))
        return DAO.insert_csv_row(clean_row, fmt_date)

    def clear_csv_data(self):
        """Pulisce i dati CSV dalla memoria."""
        self._csv_rows = []
        self._csv_total = 0


    #GRAFO LOGIC

    def create_graph(self, sede: str):
        self._grafo.clear()

        operatori = DAO.get_nodes_operatori(sede)
        fascicoli = DAO.get_nodes_fascicoli(sede)

        # aggiunta nodi con attributo bipartite
        for op in operatori:
            self._grafo.add_node(op, bipartite=0)
        for fasc in fascicoli:
            self._grafo.add_node(fasc, bipartite=1)

        # dizionari  id -> oggetto
        map_op = {op.id: op for op in operatori}
        map_fasc = {fasc.id: fasc for fasc in fascicoli}

        # calcolo degli edges
        edges = DAO.get_edges(sede)
        for id_op, id_fasc, tot_pagine in edges:
            if id_op in map_op and id_fasc in map_fasc:
                self._grafo.add_edge(map_op[id_op], map_fasc[id_fasc], weight=tot_pagine)

    def get_num_of_nodes(self) -> int:
        return self._grafo.number_of_nodes()

    def get_num_of_edges(self) -> int:
        return self._grafo.number_of_edges()

    def get_nodes_operatori(self) -> list[Operatore]:
        return [n for n, d in self._grafo.nodes(data=True) if d.get("bipartite") == 0]

    def get_nodes_fascicoli(self) -> list[Fascicolo]:
        return [n for n, d in self._grafo.nodes(data=True) if d.get("bipartite") == 1]

    def get_top5_operatori(self) -> list[tuple]:
        """I 5 operatori con più pagine totali inserite/scannerizzate."""
        result = []
        for op in self.get_nodes_operatori():
            tot = sum(d["weight"] for _, _, d in self._grafo.edges(op, data=True))
            result.append((op, tot))
        result.sort(key=lambda x: x[1], reverse=True)
        return result[0:5]

    def get_top5_fascicoli(self) -> list[tuple]:
        """I 5 fascicoli con più pagine totali lavorate/scannerizzate."""
        result = []
        for fasc in self.get_nodes_fascicoli():
            tot = sum(d["weight"] for _, _, d in self._grafo.edges(fasc, data=True))
            result.append((fasc, tot))
        result.sort(key=lambda x: x[1], reverse=True)
        return result[0:5]

    def get_top5_archi(self) -> list[tuple]:
        """I 5 archi con peso maggiore (operatore più produttivo su singolo fascicolo)."""
        edges = [e for e in self._grafo.edges(data=True)]
        edges.sort(key=lambda x: x[2]["weight"], reverse=True)
        return edges[0:5]

    def get_operatori_fascicolo(self, fascicolo: Fascicolo) -> list[tuple]:
        """Dato un fascicolo, restituisce la lista di (Operatore, pagine)
        per tutti gli operatori che ci hanno lavorato, ordinati per pagine decrescenti."""
        result = []
        for vicino, data in self._grafo[fascicolo].items():
            result.append((vicino, data["weight"]))
        result.sort(key=lambda x: x[1], reverse=True)
        return result


    # PENALI LOGIC

    def get_penali_operatori(self, mese: str) -> list:
        """Ritorna la lista degli operatori con penali nel mese specificato.
        Ogni elemento contiene: ID_Operatore, Nome_operatore, giorni_penale, totale_penale."""
        return DAO.get_penali_operatori(mese)


    # PAGAMENTI LOGIC

    def get_mesi_disponibili(self) -> list:
        """Ritorna la lista dei mesi disponibili """
        return DAO.get_mesi_disponibili()

    def get_anomalie_attivita(self) -> list:
        """Ritorna la lista delle anomalie (operatori con più attività dello stesso tipo nella stessa data)."""
        return DAO.get_anomalie_attivita()

    def get_pagamenti_operatori(self, mese: str) -> dict:
        """Ritorna i pagamenti con totali calcolati.
        
        Returns:
            dict con 'operatori' (lista), 'totale_pagine' (int), 'totale_euro' (float)
        """
        pagamenti = DAO.get_pagamenti_operatori(mese)
        totale_pagine = sum(int(row.get("pagine_nette", 0)) for row in pagamenti)
        totale_euro = sum(float(row.get("totale_pagamento", 0)) for row in pagamenti)
        
        return {
            "operatori": pagamenti,
            "totale_pagine": totale_pagine,
            "totale_euro": totale_euro
        }

    def get_indennita_trasferta(self, mese: str) -> dict:
        """Ritorna le indennità di trasferta con totali calcolati."""
        indennita = DAO.get_indennita_trasferta(mese)
        totale_giorni = sum(int(row.get("giorni_trasferta", 0)) for row in indennita)
        totale_euro = sum(float(row.get("totale_indennita", 0)) for row in indennita)
        
        return {
            "operatori": indennita,
            "totale_giorni": totale_giorni,
            "totale_euro": totale_euro
        }


    # ANALISI OPERATORI LOGIC

    def get_operatori_multisettoriali(self) -> list:
        """Operatori che hanno lavorato sia in Contabilita che in Personale."""
        return DAO.get_operatori_multisettoriali()

    def get_operatori_esperti(self) -> list:
        """Operatori che hanno lavorato in tutte le sedi del progetto."""
        return DAO.get_operatori_esperti()
