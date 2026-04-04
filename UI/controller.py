import flet as ft
from UI.view import View, VERDE, ARANCIO, ROSSO, TESTO_CHIARO, TESTO_SECONDARIO, BORDO, CIANO
from model.modello import Model


class Controller:
    def __init__(self, view: View, model: Model):
        self._view: View = view
        self._model: Model = model
        self._selected_file_path = None   # CSV import state

    def fill_dd_sede(self):
        """Popola il dropdown con le sedi disponibili."""
        sedi = self._model.get_sedi()
        self._view.dd_sede.options.clear()
        for s in sedi:
            self._view.dd_sede.options.append(ft.dropdown.Option(f"{s}"))

    def fill_dd_fascicolo(self):
        """Popola il dropdown con i fascicoli disponibili."""
        fascicoli = self._model.get_nodes_fascicoli()
        fascicoli.sort(key=lambda f: str(f))
        self._view.dd_fascicolo.options.clear()
        for fasc in fascicoli:
            self._view.dd_fascicolo.options.append(ft.dropdown.Option(
                key=str(fasc.id),
                text=str(fasc)
            ))

    #GRAFICI HANDLERS
    def handle_graph(self, e):

        if self._view.dd_sede.value is None or self._view.dd_sede.value == "":
            self._view.create_alert("Selezionare una sede!")
            return
        sede = self._view.dd_sede.value

        # crea il grafo
        self._view.txt_result1.controls.clear()
        self._model.create_graph(sede)

        self._view.txt_result1.controls.append(
            ft.Text(f"Grafo creato per: {sede}", weight=ft.FontWeight.BOLD))
        self._view.txt_result1.controls.append(
            ft.Text(f"Numero di vertici: {self._model.get_num_of_nodes()}"))
        self._view.txt_result1.controls.append(
            ft.Text(f"  di cui operatori: {len(self._model.get_nodes_operatori())}"))
        self._view.txt_result1.controls.append(
            ft.Text(f"  di cui fascicoli: {len(self._model.get_nodes_fascicoli())}"))
        self._view.txt_result1.controls.append(
            ft.Text(f"Numero di archi   : {self._model.get_num_of_edges()}"))

        self._view.btn_stats.disabled = False
        self._view.btn_operatori.disabled = False
        self.fill_dd_fascicolo()
        self._view.update_page()

    def handle_stats(self, e):
        self._view.txt_result2.controls.clear()

        # top 5 operatori
        self._view.txt_result2.controls.append(
            ft.Text("Top 5 operatori per pagine inserite:", weight=ft.FontWeight.BOLD))
        for op, tot in self._model.get_top5_operatori():
            self._view.txt_result2.controls.append(
                ft.Text(f"  {op}  ->  {tot} pag."))

        # top 5 fascicoli
        self._view.txt_result2.controls.append(ft.Text(""))
        self._view.txt_result2.controls.append(
            ft.Text("Top 5 fascicoli più lavorati:", weight=ft.FontWeight.BOLD))
        for fasc, tot in self._model.get_top5_fascicoli():
            self._view.txt_result2.controls.append(
                ft.Text(f"  {fasc}  ->  {tot} pag."))

        # top 5 archi
        self._view.txt_result2.controls.append(ft.Text(""))
        self._view.txt_result2.controls.append(
            ft.Text("Top 5 archi (operatore su singolo fascicolo):", weight=ft.FontWeight.BOLD))
        for u, v, data in self._model.get_top5_archi():
            self._view.txt_result2.controls.append(
                ft.Text(f"  {u} <-> {v}  |  peso = {data['weight']}"))

        self._view.update_page()

    def handle_operatori_fascicolo(self, e):
        if self._view.dd_fascicolo.value is None or self._view.dd_fascicolo.value == "":
            self._view.create_alert("Selezionare un fascicolo!")
            return

        # recupero il nodo Fascicolo corrispondente all'id selezionato
        id_selezionato = int(self._view.dd_fascicolo.value)
        fascicolo = None
        for fasc in self._model.get_nodes_fascicoli():
            if fasc.id == id_selezionato:
                fascicolo = fasc
                break

        self._view.txt_result2.controls.clear()
        self._view.txt_result2.controls.append(
            ft.Text(f"Operatori su {fascicolo}:", weight=ft.FontWeight.BOLD))

        for op, pagine in self._model.get_operatori_fascicolo(fascicolo):
            self._view.txt_result2.controls.append(
                ft.Text(f"  {op}  ->  {pagine} pag."))

        self._view.update_page()

    # PENALI HANDLER
    def handle_calcola_penali(self, e):
        """Calcola le penali per gli operatori sotto il minimo di 2400 pagine/giorno."""
        self._view.txt_result2.controls.clear()
        
        try:
            penali = self._model.get_penali_operatori()
            
            if not penali:
                self._view.txt_result2.controls.append(
                    ft.Text("Nessuna penale rilevata.", weight=ft.FontWeight.BOLD, color=VERDE))
                self._view.update_page()
                return
            

            self._view.txt_result2.controls.append(
                ft.Text(" PENALI OPERATORI (min. 2400 pag/giorno, 0.05€/pag)",
                        weight=ft.FontWeight.BOLD, color=ARANCIO))
            self._view.txt_result2.controls.append(ft.Divider(height=10, color=BORDO))
            
            totale_complessivo = 0
            for row in penali:
                id_op = row.get("ID_Operatore", "N/A")
                nome = row.get("Nome_Operatore", "N/A")
                giorni = row.get("giorni_penale", 0)
                pagine_mancanti = row.get("pagine_mancanti", 0)
                penale = float(row.get("totale_penale", 0))
                totale_complessivo += penale
                
                self._view.txt_result2.controls.append(
                    ft.Text(f"ID: {id_op} | {nome}", weight=ft.FontWeight.BOLD, color=TESTO_CHIARO))
                self._view.txt_result2.controls.append(
                    ft.Text(f"   Giorni sotto soglia: {giorni} | Pagine mancanti: {pagine_mancanti:,}".replace(",", "."), 
                            color=TESTO_SECONDARIO))
                self._view.txt_result2.controls.append(
                    ft.Text(f"    Penale: € {penale:.2f}".replace(".", ","), color=ROSSO))
                self._view.txt_result2.controls.append(ft.Container(height=5))
            
            # Totale
            self._view.txt_result2.controls.append(ft.Divider(height=10, color=BORDO))
            self._view.txt_result2.controls.append(
                ft.Text(f"TOTALE PENALI: € {totale_complessivo:.2f}".replace(".", ","), 
                        weight=ft.FontWeight.BOLD, size=16, color=ROSSO))
            
        except Exception as ex:
            self._view.txt_result2.controls.append(
                ft.Text(f"Errore: {ex}", color=ROSSO))
        
        self._view.update_page()


    # PAGAMENTI HANDLERS
    def fill_dd_mese(self):
        """Popola il dropdown dei mesi disponibili."""
        mesi = self._model.get_mesi_disponibili()
        self._view.dd_mese.options.clear()
        for m in mesi:
            self._view.dd_mese.options.append(ft.dropdown.Option(key=m, text=m))


    def handle_calcola_pagamenti(self, e):
        """Calcola i pagamenti dovuti per gli operatori nel mese selezionato."""
        self._view.txt_result2.controls.clear()
        
        if not self._view.dd_mese.value:
            self._view.create_alert("Selezionare un mese!")
            return
        
        mese = self._view.dd_mese.value
        
        try:
            # Controllo anomalie
            anomalie = self._model.get_anomalie_attivita()
            if anomalie:
                self._view.mostra_anomalie(anomalie)

            dati = self._model.get_pagamenti_operatori(mese)
            
            if not dati["operatori"]:
                self._view.txt_result2.controls.append(
                    ft.Text(f"Nessun pagamento per {mese}.", weight=ft.FontWeight.BOLD, color=TESTO_SECONDARIO))
                self._view.update_page()
                return

            self._view.mostra_pagamenti(mese, dati)
            
        except Exception as ex:
            self._view.txt_result2.controls.append(ft.Text(f"Errore: {ex}", color=ROSSO))
        
        self._view.update_page()


    # CSV IMPORT HANDLERS
    def handle_file_pick(self, e):
        """Apre il FilePicker per selezionare il file CSV."""
        self._view.open_file_picker()

    def on_file_result(self, e: ft.FilePickerResultEvent):
        """Gestisce il risultato della selezione file."""
        if e.files:
            self._selected_file_path = e.files[0].path
            self._view.csv_file_label.value = f"File: {e.files[0].name}"
            self._view.btn_start_import.disabled = False
            self._view.csv_status.value = "File pronto per l'importazione."
            self._view.update_page()
        else:
            self._view.csv_status.value = "Selezione annullata."
            self._view.update_page()

    def handle_start_import(self, e):
        """Avvia l'importazione del file CSV nel database."""
        if self._selected_file_path is None:
            self._view.create_alert("Nessun file selezionato!")
            return

        try:
            self._view.csv_status.value = "Caricamento file..."
            self._view.csv_progress.value = 0
            self._view.update_page()

            # Carica il CSV nel modello
            total = self._model.load_csv_file(self._selected_file_path)
            
            self._view.csv_status.value = "Connessione al database..."
            self._view.update_page()

            # Importa riga per riga
            rows = self._model.get_csv_rows()
            for i, row in enumerate(rows):
                self._model.import_csv_row(i)
                if i % 100 == 0:
                    self._view.csv_progress.value = (i + 1) / total
                    self._view.csv_status.value = f"Importazione: {i + 1}/{total}..."
                    self._view.update_page()

            self._view.csv_status.value = f"Successo! {total} record inseriti."
            self._view.csv_progress.value = 1
            self._model.clear_csv_data()
            self._view.update_page()

        except Exception as ex:
            self._view.csv_status.value = f"Errore: {ex}"
            self._view.update_page()


    # AI ASSISTANT HANDLERS
    def handle_load_models(self, e):
        """Carica i modelli dal provider selezionato."""
        self._view.ai_progress.visible = True
        self._view.update_ai_status(f"Caricamento modelli per {self._view.ai_dd_provider.value}...")
        
        provider = self._view.ai_dd_provider.value
        api_key = self._view.ai_txt_api_key.value
        self._view.ai_dd_model.options = []
        
        try:
            models = self._model.load_ai_models(provider, api_key)
            self._view.ai_dd_model.options = [ft.dropdown.Option(m) for m in models]
            self._view.ai_dd_model.disabled = False
            
            if models:
                self._view.ai_dd_model.value = models[0]
                self._view.update_ai_status("Modelli caricati.")
            else:
                self._view.update_ai_status("Nessun modello trovato.")
        except Exception as ex:
            self._view.update_ai_status(f"Errore connessione: {ex}")
        
        self._view.ai_progress.visible = False
        self._view.update_page()

    def handle_ai_send(self, e):
        """Invia la domanda all'IA e mostra la risposta."""
        question = self._view.ai_txt_question.value.strip()
        if not question or not self._view.ai_dd_model.value:
            self._view.update_ai_status("Attenzione: seleziona un modello prima di chiedere!")
            return
        
        # Aggiungo domanda alla chat
        self._view.add_ai_message(question, "user")
        self._view.ai_txt_question.value = ""
        self._view.ai_progress.visible = True
        self._view.update_page()
        
        provider = self._view.ai_dd_provider.value
        model = self._view.ai_dd_model.value
        api_key = self._view.ai_txt_api_key.value
        
        # STEP 1: L'IA scrive la query
        self._view.add_ai_message("Passo 1: L'IA sta scrivendo la query...", "system")
        
        try:
            sql = self._model.query_ai(provider, model, api_key, question, is_sql=True)
            if sql:
                sql = sql.replace("```sql", "").replace("```", "").strip()
                
                # STEP 2: Esegue query
                self._view.add_ai_message(f"Passo 2: Eseguo query: {sql}", "system")
                
                try:
                    results = self._model.execute_ai_query(sql)
                    
                    # STEP 3: Analisi risultati
                    self._view.add_ai_message(f"Passo 3: Trovati {len(results)} risultati. Analisi in corso...", "system")
                    
                    answer = self._model.query_ai(
                        provider, model, api_key, 
                        f"Dati: {str(results)}. Domanda: {question}", 
                        is_sql=False
                    )
                    self._view.add_ai_message(answer, "response")
                    
                except Exception as db_ex:
                    self._view.add_ai_message(f"DATABASE: {db_ex}", "error")
        except Exception as ai_ex:
            self._view.add_ai_message(f"IA: {ai_ex}", "error")
        
        self._view.ai_progress.visible = False
        self._view.update_ai_status("Pronto.")
        self._view.update_page()


    # GRAFICI HANDLERS
    def handle_generate_chart(self, e):
        """Genera il grafico selezionato con i dati dal database."""
        if self._view.chart_selector.value is None:
            self._view.create_alert("Seleziona un tipo di grafico!")
            return
        
        chart_type = self._view.chart_selector.value
        
        try:
            # Recupera i dati dal modello
            data = self._model.get_chart_data(chart_type)
            
            if not data:
                self._view.create_alert("Nessun dato disponibile per questo grafico.")
                return
            
            # Aggiorna il grafico nella view
            self._view.update_chart(chart_type, data)
            
            # Aggiorna le statistiche
            stats = self._model.get_stats_totals()
            self._view.update_stats_cards(stats)
            
            self._view.update_page()
            
        except Exception as ex:
            self._view.create_alert(f"Errore: {ex}")
