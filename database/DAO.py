from database.DB_connect import DBConnect
from model.operatore import Operatore
from model.fascicolo import Fascicolo

#variabile globale che rappresenta il nome della tabella utilizzata nelle query
TABLE_NAME = "digitalizzazione_test"


class DAO:
    def __init__(self):
        pass

    @staticmethod
    def insert_csv_row(row: dict, formatted_date: str) -> bool:
        """Inserisce una singola riga nel database.
        Ritorna True se l'inserimento è andato a buon fine, False altrimenti."""
        cnx = DBConnect.get_connection()
        if cnx is None:
            return False
        try:
            cursor = cnx.cursor()
            query = f"""INSERT INTO {TABLE_NAME} 
                        (Sede, Ufficio, Attivita, `Nome_operatore`, ID_Operatore, 
                         ID_attivita, Data_Attivita, ID_Fascicolo, Anno_fascicolo, conta_pagine_giorno) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (
                row.get("Sede"), row.get("Ufficio"), row.get("Attivita"),
                row.get("Nome_operatore"), row.get("ID_Operatore"), row.get("ID_attivita"),
                formatted_date, row.get("ID_Fascicolo"), row.get("Anno_fascicolo"),
                row.get("conta_pagine_giorno")
            ))
            cnx.commit()
            cursor.close()
            cnx.close()
            return True
        except Exception as e:
            print(f"Errore inserimento: {e}")
            cnx.close()
            return False

    @staticmethod
    def get_sedi() -> list[str]:
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT DISTINCT Sede
                       FROM digitalizzazione
                       ORDER BY Sede ASC"""
            cursor.execute(query)

            for row in cursor:
                result.append(row["Sede"])

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_nodes_operatori(sede: str) -> list[Operatore]:
        """Restituisce i nodi di tipo operatore"""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT DISTINCT ID_operatore, Nome_operatore, Sede, Ufficio
                       FROM digitalizzazione
                       WHERE Sede = %s"""
            cursor.execute(query, (sede,))

            for row in cursor:
                result.append(Operatore(
                    id=row["ID_operatore"],
                    nome=row["Nome_operatore"],
                    sede=row["Sede"],
                    ufficio=row["Ufficio"]
                ))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_nodes_fascicoli(sede: str) -> list[Fascicolo]:
        """Restituisce i nodi di tipo fascicolo"""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT DISTINCT ID_fascicolo, Anno_fascicolo, Ufficio
                       FROM digitalizzazione
                       WHERE Sede = %s"""
            cursor.execute(query, (sede,))

            for row in cursor:
                result.append(Fascicolo(
                    id=row["ID_fascicolo"],
                    anno=row["Anno_fascicolo"],
                    ufficio=row["Ufficio"]
                ))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_edges(sede: str) -> list[tuple]:
        """Restituisce lista di (id_operatore, id_fascicolo, tot_pagine)
        considerando solo gli inserimenti (Inserimento_Pagina)."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT ID_operatore, ID_fascicolo,
                              SUM(conta_pagine_giorno) AS tot_pagine
                       FROM digitalizzazione
                       WHERE Sede = %s
                         AND Attivita = 'Inserimento_Pagina'
                       GROUP BY ID_operatore, ID_fascicolo"""
            cursor.execute(query, (sede,))

            for row in cursor:
                result.append((row["ID_operatore"], row["ID_fascicolo"], row["tot_pagine"]))

            cursor.close()
            cnx.close()
        return result


    # AI ASSISTANT - Database Methods

    @staticmethod
    def get_table_schema() -> str:
        """Ritorna lo schema della tabella come stringa (per AI)"""
        cnx = DBConnect.get_connection()
        if cnx is None:
            return "Sede, Nome_operatore, Data_Attivita, conta_pagine_giorno"
        try:
            cursor = cnx.cursor()
            cursor.execute(f"DESCRIBE {TABLE_NAME}")
            cols = [f"{row[0]} ({row[1]})" for row in cursor.fetchall()]
            cursor.close()
            return ", ".join(cols)
        except Exception as e:
            print(f"[DB ERROR] {e}")
            return "Sede, Nome_operatore, Data_Attivita, conta_pagine_giorno"
        finally:
            cnx.close()

    @staticmethod
    def execute_ai_query(sql: str) -> list:
        """Esegue una query SQL e ritorna i risultati come lista di dict."""
        cnx = DBConnect.get_connection()
        if cnx is None:
            raise Exception("Connessione al database fallita")
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            raise e
        finally:
            cnx.close()


    # GRAFICI - Database Methods

    @staticmethod
    def get_pages_per_operator(limit: int = 5) -> list:
        """Ritorna i top N operatori per pagine inserite."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT Nome_operatore as nome, SUM(conta_pagine_giorno) as totale
                       FROM digitalizzazione
                       WHERE Attivita = 'Inserimento_Pagina'
                       GROUP BY Nome_operatore
                       ORDER BY totale DESC
                       LIMIT %s"""
            cursor.execute(query, (limit,))
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_pages_per_operator: {e}")
        finally:
            cnx.close()
        return result

    @staticmethod
    def get_pages_per_sede() -> list:
        """Ritorna le pagine totali per sede."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT Sede as nome, SUM(conta_pagine_giorno) as totale
                       FROM digitalizzazione
                       WHERE Attivita = 'Inserimento_Pagina'
                       GROUP BY Sede
                       ORDER BY totale DESC"""
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_pages_per_sede: {e}")
        finally:
            cnx.close()
        return result

    @staticmethod
    def get_pages_per_month() -> list:
        """Ritorna le pagine inserite per mese.
        Gestisce date in formato stringa (dd/mm/yyyy)"""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)

            query = """SELECT CONCAT(SUBSTRING(Data_Attivita, 7, 4), '-', SUBSTRING(Data_Attivita, 4, 2)) as mese,
                        SUM(conta_pagine_giorno) as totale
                        FROM digitalizzazione
                        WHERE Attivita = 'Inserimento_Pagina'
                        AND Data_Attivita IS NOT NULL
                        AND Data_Attivita != ''
                        GROUP BY mese
                        ORDER BY mese ASC"""
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_pages_per_month: {e}")
        finally:
            cnx.close()
        return result

    @staticmethod
    def get_pages_per_ufficio() -> list:
        """Ritorna la distribuzione pagine per ufficio."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT Ufficio as nome, SUM(conta_pagine_giorno) as totale
                       FROM digitalizzazione
                       WHERE Attivita = 'Inserimento_Pagina'
                       GROUP BY Ufficio
                       ORDER BY totale DESC"""
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_pages_per_ufficio: {e}")
        finally:
            cnx.close()
        return result

    @staticmethod
    def get_top_fascicoli(limit: int = 5) -> list:
        """Ritorna i top N fascicoli per pagine lavorate."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT CONCAT('Fasc. ', ID_Fascicolo) as nome, 
                              SUM(conta_pagine_giorno) as totale
                       FROM digitalizzazione
                       WHERE Attivita = 'Inserimento_Pagina'
                       GROUP BY ID_Fascicolo
                       ORDER BY totale DESC
                       LIMIT %s"""
            cursor.execute(query, (limit,))
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_top_fascicoli: {e}")
        finally:
            cnx.close()
        return result

    @staticmethod
    def get_stats_totals() -> dict:
        """Ritorna le statistiche totali per le card."""
        cnx = DBConnect.get_connection()
        result = {"totale_pagine": 0, "operatori": 0, "fascicoli": 0, "media_giorno": 0}
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            
            # Totale pagine
            cursor.execute("""SELECT SUM(conta_pagine_giorno) as tot 
                             FROM digitalizzazione 
                             WHERE Attivita = 'Inserimento_Pagina'""")
            row = cursor.fetchone()
            result["totale_pagine"] = int(row["tot"]) if row and row["tot"] else 0
            
            # Operatori unici
            cursor.execute("""SELECT COUNT(DISTINCT ID_Operatore) as tot FROM digitalizzazione""")
            row = cursor.fetchone()
            result["operatori"] = int(row["tot"]) if row and row["tot"] else 0
            
            # Fascicoli unici
            cursor.execute("""SELECT COUNT(DISTINCT ID_Fascicolo) as tot FROM digitalizzazione""")
            row = cursor.fetchone()
            result["fascicoli"] = int(row["tot"]) if row and row["tot"] else 0
            
            # Media giornaliera (gestisce date stringa)
            cursor.execute("""SELECT AVG(daily_total) as avg_tot FROM 
                             (SELECT SUM(conta_pagine_giorno) as daily_total
                              FROM digitalizzazione 
                              WHERE Attivita = 'Inserimento_Pagina'
                              GROUP BY Data_Attivita) as daily""")
            row = cursor.fetchone()
            result["media_giorno"] = int(row["avg_tot"]) if row and row["avg_tot"] else 0
            
            cursor.close()
        except Exception as e:
            print(f"Errore get_stats_totals: {e}")
        finally:
            cnx.close()
        return result


    # PENALI - Database Methods

    # Costanti per il calcolo penali
    MINIMO_PAGINE_GIORNO = 2400
    COSTO_PENALE_PAGINA = 0.05

    @staticmethod
    def get_penali_operatori() -> list:
        """Calcola le penali per gli operatori sotto il minimo di 2400 pagine/giorno.
        Penale = (2400 - pagine_giorno) * 0.05 € per ogni giorno sotto il minimo.
        Ritorna lista di dict con ID_Operatore, Nome_operatore, giorni_penale, totale_penale."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            # Query che calcola le penali per ogni operatore
            # ID_attivita = 1 significa scansione pagine
            query = """
                SELECT 
                    ID_Operatore,
                    Nome_operatore,
                    COUNT(*) as giorni_penale,
                    SUM(2400 - conta_pagine_giorno) as pagine_mancanti,
                    ROUND(SUM((2400 - conta_pagine_giorno) * 0.05), 2) as totale_penale
                FROM digitalizzazione
                WHERE ID_attivita = 1
                  AND conta_pagine_giorno < 2400
                GROUP BY ID_Operatore, Nome_operatore
                HAVING totale_penale > 0
                ORDER BY totale_penale DESC
            """
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_penali_operatori: {e}")
        finally:
            cnx.close()
        return result


    # PAGAMENTI - Database Methods

    # Costante per il calcolo pagamenti
    COSTO_COPIA = 0.139

    @staticmethod
    def get_mesi_disponibili() -> list:
        """Ritorna la lista dei mesi disponibili"""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """
                SELECT DISTINCT CONCAT(SUBSTRING(Data_Attivita, 7, 4), '-', SUBSTRING(Data_Attivita, 4, 2)) as mese
                FROM digitalizzazione
                WHERE Data_Attivita IS NOT NULL AND Data_Attivita != ''
                ORDER BY mese DESC
            """
            cursor.execute(query)
            for row in cursor:
                if row["mese"]:
                    result.append(row["mese"])
            cursor.close()
        except Exception as e:
            print(f"Errore get_mesi_disponibili: {e}")
        finally:
            cnx.close()
        return result

    @staticmethod
    def get_anomalie_attivita() -> list:
        """Trova operatori con più di una attività dello stesso tipo nella stessa data.
        Ritorna lista di dict con ID_Operatore, Nome_operatore, Data_Attivita, Attivita, conteggio."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """
                SELECT  ID_Operatore,Nome_operatore,Data_Attivita,Attivita,COUNT(*) as conteggio
                FROM digitalizzazione
                GROUP BY ID_Operatore, Nome_operatore, Data_Attivita, Attivita
                HAVING conteggio > 1
                ORDER BY Data_Attivita DESC, Nome_operatore
            """
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_anomalie_attivita: {e}")
        finally:
            cnx.close()
        return result

    @staticmethod
    def get_pagamenti_operatori(mese: str) -> list:
        """Calcola i pagamenti dovuti per ogni operatore nel mese specificato.
        Pagine prodotte = pagine inserite (ID_attivita=1) - pagine eliminate (ID_attivita=-1)
        Pagamento = pagine_prodotte * 0.139 €
        Ritorna lista di dict con ID_Operatore, Nome_operatore, pag_inserite, pag_eliminate, 
        pagine_nette, totale_pagamento."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """
                SELECT ID_Operatore,Nome_operatore,
                    SUM(CASE WHEN ID_attivita = 1 THEN conta_pagine_giorno ELSE 0 END) as pag_inserite,
                    SUM(CASE WHEN ID_attivita = -1 THEN conta_pagine_giorno ELSE 0 END) as pag_eliminate,
                    SUM(conta_pagine_giorno * ID_attivita) as pagine_nette,
                    ROUND(SUM(conta_pagine_giorno * ID_attivita) * 0.139, 2) as totale_pagamento
                FROM digitalizzazione
                WHERE CONCAT(SUBSTRING(Data_Attivita, 7, 4), '-', SUBSTRING(Data_Attivita, 4, 2)) = %s
                GROUP BY ID_Operatore, Nome_operatore
                HAVING pagine_nette > 0
                ORDER BY totale_pagamento DESC
            """
            cursor.execute(query, (mese,))
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_pagamenti_operatori: {e}")
        finally:
            cnx.close()
        return result



    # ANALISI OPERATORI - Database Methods


    @staticmethod
    def get_operatori_multisettoriali() -> list:
        """Operatori che hanno lavorato sia in Contabilita che in Personale."""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """
                SELECT ID_Operatore, Nome_operatore
                FROM digitalizzazione
                WHERE Ufficio IN ('Contabilita', 'Personale')
                GROUP BY ID_Operatore, Nome_operatore
                HAVING COUNT(DISTINCT Ufficio) = 2
                ORDER BY Nome_operatore
            """
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_operatori_multisettoriali: {e}")
        finally:
            cnx.close()
        return result

    @staticmethod
    def get_operatori_esperti() -> list:
        """Operatori che hanno lavorato in tutte le sedi del progetto.
          La query gestisce il caso in cui il numero di sedi aumentino"""
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            return result
        try:
            cursor = cnx.cursor(dictionary=True)
            query = """
                SELECT ID_Operatore, Nome_operatore
                FROM digitalizzazione
                GROUP BY ID_Operatore, Nome_operatore
                HAVING COUNT(DISTINCT Sede) = (SELECT COUNT(DISTINCT Sede) FROM digitalizzazione)
                ORDER BY Nome_operatore
            """
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Errore get_operatori_esperti: {e}")
        finally:
            cnx.close()
        return result
