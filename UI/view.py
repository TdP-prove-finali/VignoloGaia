import flet as ft



# COLORI TEMA - Variabili per una gestione centralizzata

BLU_PRIMARIO = "#3B82F6"
BLU_SCURO = "#1E293B"
BLU_SCURO_ALPHA = "#1E293BCC"
BLU_NOTTE = "#0F172A"
BLU_CHAT = "#1e1e2e"
VERDE = "#10B981"
VIOLA = "#8B5CF6"
ARANCIO = "#F59E0B"
ROSSO = "#EF4444"
CIANO = "#06B6D4"
ROSA = "#EC4899"
LIME = "#84CC16"
TESTO_CHIARO = "#F8FAFC"
TESTO_SECONDARIO = "#94A3B8"
BORDO = "#334155"
BORDO_SCURO = "#333333"
BG_RISPOSTA = "#33334d"

# Palette colori per grafici
CHART_COLORS = [BLU_PRIMARIO, VERDE, VIOLA, ARANCIO, ROSSO, CIANO, ROSA, LIME]


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._page.title = "Digitalizzazione"
        self._page.horizontal_alignment = "CENTER"
        self._page.window_width = 1150
        self._page.window_height = 900
        self._page.theme_mode = ft.ThemeMode.DARK
        self._page.bgcolor = BLU_NOTTE
        self._page.padding = 0
        
        self._controller = None
        self.nav_rail = None
        self.content_area = None
        
        # Grafo Bipartito controls
        self.dd_sede = None
        self.dd_fascicolo = None
        self.dd_mese = None
        self.btn_graph = None
        self.btn_stats = None
        self.btn_penali = None
        self.btn_pagamenti = None
        self.btn_indennita = None
        self.btn_operatori = None
        self.btn_multisettoriali = None
        self.btn_esperti = None
        self.txt_result1 = None
        self.txt_result2 = None
        
        # Upload CSV controls
        self.csv_file_label = None
        self.csv_upload_btn = None
        self.csv_status = None
        self.csv_progress = None
        self.btn_start_import = None
        self.file_picker = None
        
        # AI Assistant controls
        self.ai_dd_provider = None
        self.ai_txt_api_key = None
        self.ai_btn_load = None
        self.ai_dd_model = None
        self.ai_txt_question = None
        self.ai_btn_send = None
        self.ai_chat_history = None
        self.ai_status_text = None
        self.ai_progress = None
        
        # Controlli Univocità controls
        self.btn_controlli = None
        self.controlli_results = None

        # Grafici controls
        self.chart_selector = None
        self.chart_container = None
        self.chart_content = None
        self.chart_title_text = None
        self.btn_generate_chart = None
        self.stat_card_pagine = None
        self.stat_card_operatori = None
        self.stat_card_fascicoli = None
        self.stat_card_media = None



    def load_interface(self):
        self.file_picker = ft.FilePicker(on_result=self._on_file_result)
        self._page.overlay.append(self.file_picker)
        
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            bgcolor=BLU_SCURO,
            indicator_color=BLU_PRIMARIO,
            expand=True,
            on_change=self._on_nav_change,
            destinations=[
                ft.NavigationRailDestination(icon=ft.icons.HUB_OUTLINED, selected_icon=ft.icons.HUB, label="Home", padding=10),
                ft.NavigationRailDestination(icon=ft.icons.UPLOAD_FILE_OUTLINED, selected_icon=ft.icons.UPLOAD_FILE, label="Upload CSV", padding=10),
                ft.NavigationRailDestination(icon=ft.icons.SMART_TOY_OUTLINED, selected_icon=ft.icons.SMART_TOY, label="AI Assistant", padding=10),
                ft.NavigationRailDestination(icon=ft.icons.BAR_CHART_OUTLINED, selected_icon=ft.icons.BAR_CHART, label="Grafici", padding=10),
                ft.NavigationRailDestination(icon=ft.icons.VERIFIED_OUTLINED, selected_icon=ft.icons.VERIFIED, label="Controlli", padding=10),
            ],
        )

        sidebar = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.DOCUMENT_SCANNER, size=40, color=BLU_PRIMARIO),
                    ft.Text("GSD", size=12, weight="bold", color=TESTO_CHIARO),
                ], horizontal_alignment="center", spacing=5),
                padding=20,
            ),
            ft.Divider(height=1, color=BORDO),
            self.nav_rail,
        ], spacing=0)

        sidebar_container = ft.Container(
            content=sidebar,
            bgcolor=BLU_SCURO,
            border=ft.border.only(right=ft.BorderSide(1, BORDO)),
            width=120,
        )

        self.content_area = ft.Container(content=self._build_home_page(), expand=True, padding=30)

        self._page.controls.clear()
        self._page.controls.append(ft.Row([sidebar_container, self.content_area], expand=True, spacing=0))
        self._page.update()

    def _on_nav_change(self, e):
        pages = [self._build_home_page, self._build_upload_csv_page, self._build_ai_assistant_page, self._build_grafici_page, self._build_controlli_page]
        self.content_area.content = pages[e.control.selected_index]()
        self._page.update()


    # PAGINA 1: HOME PAGE

    def _build_home_page(self):
        header = ft.Container(
            content=ft.Column([
                ft.Text("GSD", size=36, weight="bold", color=TESTO_CHIARO),
                ft.Text("Gestione servizi digitalizazione", color=TESTO_SECONDARIO, size=14),
            ], horizontal_alignment="center", spacing=5),
            padding=ft.padding.only(bottom=20)
        )

        self.dd_sede = ft.Dropdown(
            label="Sede", hint_text="Seleziona una sede", width=350,
            border_color=BORDO, focused_border_color=BLU_PRIMARIO,
            bgcolor=BLU_SCURO, border_radius=12, color=TESTO_CHIARO,
            label_style=ft.TextStyle(color=TESTO_SECONDARIO),
        )
        if self._controller:
            self._controller.fill_dd_sede()

        self.btn_graph = ft.ElevatedButton(
            text="Crea Grafo", icon="account_tree",
            on_click=self._controller.handle_graph if self._controller else None,
            style=ft.ButtonStyle(bgcolor=BLU_PRIMARIO, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12))
        )
        
        self.btn_stats = ft.ElevatedButton(
            text="Calcola Statistiche", icon="analytics", disabled=True,
            on_click=self._controller.handle_stats if self._controller else None,
            style=ft.ButtonStyle(bgcolor=VERDE, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12))
        )

        controls_section = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(name="location_city", color=BLU_PRIMARIO, size=24),
                        ft.Text("Selezione Sede", size=18, weight="w600", color=TESTO_CHIARO)], spacing=10),
                ft.Divider(height=20, color=BORDO),
                ft.Row([self.dd_sede], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=15),
                ft.Row([self.btn_graph, self.btn_stats], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ], spacing=10),
            padding=30, bgcolor=BLU_SCURO_ALPHA, border_radius=20, border=ft.border.all(1, BORDO),
        )

        # Sezione Pagamenti
        self.dd_mese = ft.Dropdown(
            label="Mese", hint_text="Seleziona un mese", width=200,
            border_color=BORDO, focused_border_color=CIANO,
            bgcolor=BLU_SCURO, border_radius=12, color=TESTO_CHIARO,
            label_style=ft.TextStyle(color=TESTO_SECONDARIO),
        )
        if self._controller:
            self._controller.fill_dd_mese()

        self.btn_pagamenti = ft.ElevatedButton(
            text="Calcola Pagamenti", icon="payments",
            on_click=self._controller.handle_calcola_pagamenti if self._controller else None,
            style=ft.ButtonStyle(bgcolor=CIANO, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12))
        )

        self.btn_indennita = ft.ElevatedButton(
            text="Indennità Trasferta", icon="directions_car",
            on_click=self._controller.handle_indennita_trasferta if self._controller else None,
            style=ft.ButtonStyle(bgcolor=LIME, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12))
        )

        self.btn_penali = ft.ElevatedButton(
            text="Calcola Penali", icon="warning",
            on_click=self._controller.handle_calcola_penali if self._controller else None,
            style=ft.ButtonStyle(bgcolor=ARANCIO, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12))
        )

        pagamenti_section = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(name="euro", color=CIANO, size=24),
                        ft.Text("Calcolo Pagamenti", size=18, weight="w600", color=TESTO_CHIARO)], spacing=10),
                ft.Divider(height=20, color=BORDO),
                ft.Row([self.dd_mese, self.btn_pagamenti, self.btn_indennita, self.btn_penali], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ], spacing=10),
            padding=30, bgcolor=BLU_SCURO_ALPHA, border_radius=20, border=ft.border.all(1, BORDO),
        )

        # Sezione Analisi Operatori
        self.btn_multisettoriali = ft.ElevatedButton(
            text="Multisettoriali", icon="swap_horiz",
            on_click=self._controller.handle_operatori_multisettoriali if self._controller else None,
            style=ft.ButtonStyle(bgcolor=VIOLA, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12))
        )
        self.btn_esperti = ft.ElevatedButton(
            text="Esperti", icon="star",
            on_click=self._controller.handle_operatori_esperti if self._controller else None,
            style=ft.ButtonStyle(bgcolor=ROSA, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12))
        )

        analisi_operatori_section = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(name="people", color=VIOLA, size=24),
                        ft.Text("Analisi Operatori", size=18, weight="w600", color=TESTO_CHIARO)], spacing=10),
                ft.Divider(height=20, color=BORDO),
                ft.Row([self.btn_multisettoriali, self.btn_esperti], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ], spacing=10),
            padding=30, bgcolor=BLU_SCURO_ALPHA, border_radius=20, border=ft.border.all(1, BORDO),
        )

        #sezione fascicoli
        self.dd_fascicolo = ft.Dropdown(
            label="Fascicolo", hint_text="Seleziona un fascicolo", width=400,
            border_color=BORDO, focused_border_color=BLU_PRIMARIO,
            bgcolor=BLU_SCURO, border_radius=12, color=TESTO_CHIARO,
            label_style=ft.TextStyle(color=TESTO_SECONDARIO),
        )
        
        self.btn_operatori = ft.ElevatedButton(
            text="Chi ha lavorato?", icon="group", disabled=True,
            on_click=self._controller.handle_operatori_fascicolo if self._controller else None,
            style=ft.ButtonStyle(bgcolor=VIOLA, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12))
        )

        fascicolo_section = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(name="folder_open", color=VIOLA, size=24),
                        ft.Text("Analisi Fascicolo", size=18, weight="w600", color=TESTO_CHIARO)], spacing=10),
                ft.Divider(height=20, color=BORDO),
                ft.Row([self.dd_fascicolo, self.btn_operatori], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True),
            ], spacing=10),
            padding=30, bgcolor=BLU_SCURO_ALPHA, border_radius=20, border=ft.border.all(1, BORDO),
        )

        self.txt_result1 = ft.ListView(expand=1, spacing=8, padding=15, auto_scroll=False)
        self.txt_result2 = ft.ListView(expand=1, spacing=8, padding=15, auto_scroll=False)
        self.txt_result1.controls.append(ft.Text(" Risultati Grafo", color=TESTO_SECONDARIO, size=14, italic=True))
        self.txt_result2.controls.append(ft.Text(" Statistiche", color=TESTO_SECONDARIO, size=14, italic=True))

        container1 = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(name="hub", color=BLU_PRIMARIO, size=20),
                        ft.Text("Risultati Grafo", weight="w600", color=TESTO_CHIARO, size=16)], spacing=8),
                ft.Divider(height=15, color=BORDO),
                ft.Container(content=self.txt_result1, expand=True),
            ]),
            padding=20, bgcolor=BLU_SCURO, width=420, height=320, border_radius=16, border=ft.border.all(1, BORDO),
        )
        
        container2 = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(name="bar_chart", color=VERDE, size=20),
                        ft.Text("Statistiche", weight="w600", color=TESTO_CHIARO, size=16)], spacing=8),
                ft.Divider(height=15, color=BORDO),
                ft.Container(content=self.txt_result2, expand=True),
            ]),
            padding=20, bgcolor=BLU_SCURO, width=420, height=320, border_radius=16, border=ft.border.all(1, BORDO),
        )

        return ft.Column([
            header, controls_section, ft.Container(height=15),
            pagamenti_section, ft.Container(height=15),
            analisi_operatori_section, ft.Container(height=15),
            fascicolo_section, ft.Container(height=20),
            ft.Row([container1, container2], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
        ], horizontal_alignment="center", spacing=0, scroll=ft.ScrollMode.AUTO)

    # Pagamenti metodi di visualizazione
    def _fmt_num(self, n) -> str:
        """Formatta numero con separatore delle migliaia ."""
        return f"{int(n):,}".replace(",", ".")

    def _fmt_euro(self, n) -> str:
        """Formatta euro con virgola """
        return f"{float(n):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def mostra_anomalie(self, anomalie: list):
        """Visualizza le anomalie nella ListView."""
        self.txt_result2.controls.append(
            ft.Text("ANOMALIE RILEVATE", weight=ft.FontWeight.BOLD, color=ROSSO))
        self.txt_result2.controls.append(
            ft.Text("Operatori con più attività dello stesso tipo nella stessa data e sede:",
                    color=TESTO_SECONDARIO, size=12))
        self.txt_result2.controls.append(ft.Divider(height=10, color=BORDO))

        for row in anomalie[:10]:
            self.txt_result2.controls.append(
                ft.Text(f"ID: {row['ID_Operatore']} | {row['Nome_operatore']}", color=ARANCIO, size=12))
            self.txt_result2.controls.append(
                ft.Text(f"   Data: {row['Data_Attivita']} | {row['Sede']} | {row['Attivita']} x{row['conteggio']}",
                        color=TESTO_SECONDARIO, size=11))

        if len(anomalie) > 10:
            self.txt_result2.controls.append(
                ft.Text(f"   ... e altre {len(anomalie) - 10} anomalie", color=TESTO_SECONDARIO, size=11, italic=True))

        self.txt_result2.controls.append(ft.Container(height=15))

    def mostra_pagamenti(self, mese: str, dati: dict):
        """Visualizza i pagamenti nella ListView."""
        self.txt_result2.controls.append(
            ft.Text(f"PAGAMENTI MESE {mese} (0,139 €/pag)", weight=ft.FontWeight.BOLD, color=CIANO))
        self.txt_result2.controls.append(ft.Divider(height=10, color=BORDO))

        # Dettaglio operatori
        for row in dati["operatori"]:
            self.txt_result2.controls.append(
                ft.Text(f"ID: {row['ID_Operatore']} | {row['Nome_operatore']}",
                        weight=ft.FontWeight.BOLD, color=TESTO_CHIARO))
            self.txt_result2.controls.append(
                ft.Text(
                    f"   Inserite: {self._fmt_num(row['pag_inserite'])} | Eliminate: {self._fmt_num(row['pag_eliminate'])} | Nette: {self._fmt_num(row['pagine_nette'])}",
                    color=TESTO_SECONDARIO))
            self.txt_result2.controls.append(
                ft.Text(f"   Pagamento: € {self._fmt_euro(row['totale_pagamento'])}", color=VERDE))
            self.txt_result2.controls.append(ft.Container(height=5))

        # Totali
        self.txt_result2.controls.append(ft.Divider(height=10, color=BORDO))
        self.txt_result2.controls.append(
            ft.Text(f"TOTALE: {self._fmt_num(dati['totale_pagine'])} pag -> € {self._fmt_euro(dati['totale_euro'])}",
                    weight=ft.FontWeight.BOLD, size=16, color=VERDE))

    def mostra_indennita_trasferta(self, mese: str, dati: dict):
        """Visualizza le indennità di trasferta nella ListView."""
        self.txt_result2.controls.append(
            ft.Text(f"INDENNITÀ TRASFERTA {mese} (83,40 €/giorno)", weight=ft.FontWeight.BOLD, color=LIME))
        self.txt_result2.controls.append(
            ft.Text("Operatori che hanno lavorato in sedi diverse nello stesso giorno:",
                    color=TESTO_SECONDARIO, size=12))
        self.txt_result2.controls.append(ft.Divider(height=10, color=BORDO))

        for row in dati["operatori"]:
            self.txt_result2.controls.append(
                ft.Text(f"ID: {row['ID_Operatore']} | {row['Nome_operatore']}",
                        weight=ft.FontWeight.BOLD, color=TESTO_CHIARO))
            self.txt_result2.controls.append(
                ft.Text(f"   Giorni trasferta: {row['giorni_trasferta']}", color=TESTO_SECONDARIO))
            self.txt_result2.controls.append(
                ft.Text(f"   Indennità: € {self._fmt_euro(row['totale_indennita'])}", color=LIME))
            self.txt_result2.controls.append(ft.Container(height=5))

        # Totali
        self.txt_result2.controls.append(ft.Divider(height=10, color=BORDO))
        self.txt_result2.controls.append(
            ft.Text(f"TOTALE: {dati['totale_giorni']} giorni -> € {self._fmt_euro(dati['totale_euro'])}",
                    weight=ft.FontWeight.BOLD, size=16, color=LIME))


    # PAGINA 2: UPLOAD CSV

    def _build_upload_csv_page(self):
        self.csv_file_label = ft.Text("Nessun file selezionato", color=TESTO_SECONDARIO)
        self.csv_status = ft.Text("Pronto per iniziare...", color=TESTO_SECONDARIO)
        self.csv_progress = ft.ProgressBar(width=600, color=BLU_PRIMARIO, value=0, bgcolor=BORDO)
        
        self.csv_upload_btn = ft.ElevatedButton(
            "Seleziona File CSV", icon="folder_open",
            on_click=self._controller.handle_file_pick if self._controller else None,
        )
        
        self.btn_start_import = ft.ElevatedButton(
            "Inizia Importazione", icon="upload",
            on_click=self._controller.handle_start_import if self._controller else None,
            disabled=True,
            style=ft.ButtonStyle(bgcolor=VERDE, color="white", padding=24, shape=ft.RoundedRectangleBorder(radius=12))
        )

        main_container = ft.Container(
            content=ft.Column([
                ft.Text("Database Uploader", size=36, weight="bold", color=TESTO_CHIARO),
                ft.Text("Caricamento dati in db_digital7", color=TESTO_SECONDARIO),
                ft.Divider(height=40, color=BLU_SCURO),
                ft.Row([self.csv_upload_btn, self.csv_file_label], alignment="center"),
                ft.Divider(height=30, color=BLU_SCURO),
                ft.Container(
                    content=ft.Column([self.csv_status, self.csv_progress], spacing=15),
                    padding=30, bgcolor=BLU_SCURO, border_radius=16
                ),
                ft.Container(height=20),
                self.btn_start_import
            ], horizontal_alignment="center"),
            padding=40, bgcolor=BLU_SCURO_ALPHA, border_radius=30, border=ft.border.all(1, BORDO)
        )

        return ft.Column([main_container], horizontal_alignment="center", spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    # file pickers methods
    def open_file_picker(self):
        self.file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.ANY, allowed_extensions=["csv"])

    def _on_file_result(self, e: ft.FilePickerResultEvent):
        if self._controller:
            self._controller.on_file_result(e)


    # PAGINA 3: AI ASSISTANT

    def _build_ai_assistant_page(self):
        self.ai_dd_provider = ft.Dropdown(
            label="1. Scegli Provider",
            options=[
                ft.dropdown.Option("Ollama (Locale)"),
                ft.dropdown.Option("LM Studio (Locale)"),
                ft.dropdown.Option("Groq"),
                ft.dropdown.Option("OpenAI"),
            ],
            width=230, value="Ollama (Locale)", on_change=self._on_provider_change
        )
        self.ai_txt_api_key = ft.TextField(label="2. API Key", password=True, expand=True, value="n/a", disabled=True)
        self.ai_btn_load = ft.ElevatedButton("3. Carica Modelli", icon=ft.icons.REFRESH,
                                              on_click=self._controller.handle_load_models if self._controller else None)
        self.ai_dd_model = ft.Dropdown(label="4. Scegli il Modello", options=[], width=450, disabled=True)
        
        self.ai_txt_question = ft.TextField(
            label=" SCRIVI QUI LA TUA DOMANDA",
            hint_text="Esempio: Quante pagine ha inserito Rossi nel 2024?",
            border_color=BLU_PRIMARIO, border_width=2, height=70, expand=True,
            on_submit=self._controller.handle_ai_send if self._controller else None
        )
        self.ai_btn_send = ft.ElevatedButton(
            "CHIEDI ALL'IA", icon=ft.icons.SEND,
            on_click=self._controller.handle_ai_send if self._controller else None,
            bgcolor=BLU_PRIMARIO, color="white", height=70
        )

        self.ai_chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        self.ai_status_text = ft.Text("Pronto.", size=12, color=TESTO_SECONDARIO)
        self.ai_progress = ft.ProgressBar(visible=False, color=BLU_PRIMARIO)

        return ft.Container(
            padding=30, expand=True,
            content=ft.Column([
                ft.Text("🤖 AI SQL Data Assistant", size=32, weight="bold", color=TESTO_CHIARO),
                ft.Row([self.ai_dd_provider, self.ai_txt_api_key, self.ai_btn_load]),
                ft.Row([self.ai_dd_model], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=20, color=BORDO),
                ft.Row([self.ai_txt_question, self.ai_btn_send]),
                ft.Row([self.ai_progress, self.ai_status_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=self.ai_chat_history, expand=True, bgcolor=BLU_CHAT, 
                    border_radius=15, padding=20, border=ft.border.all(1, BORDO_SCURO)
                ),
            ])
        )

    def _on_provider_change(self, e):
        is_local = "Locale" in self.ai_dd_provider.value
        self.ai_txt_api_key.disabled = is_local
        self.ai_txt_api_key.value = "n/a" if is_local else ""
        self._page.update()

    # ai assistant methods
    def add_ai_message(self, text: str, msg_type: str = "user"):
        if msg_type == "user":
            self.ai_chat_history.controls.append(ft.Text(f" DOMANDA: {text}", weight="bold", color=BLU_PRIMARIO))
        elif msg_type == "system":
            self.ai_chat_history.controls.append(ft.Text(f"⚡ [SISTEMA] {text}", size=12, color=ARANCIO, italic=True))
        elif msg_type == "response":
            self.ai_chat_history.controls.append(ft.Container(
                content=ft.Text(f"🤖 RISPOSTA: {text}"),
                bgcolor=BG_RISPOSTA, padding=15, border_radius=10, border=ft.border.all(1, BORDO)
            ))
        elif msg_type == "error":
            self.ai_chat_history.controls.append(ft.Text(f" ERRORE: {text}", color=ROSSO, weight="bold"))
        self._page.update()

    def update_ai_status(self, msg: str):
        self.ai_status_text.value = msg
        self._page.update()

    def set_ai_progress(self, visible: bool):
        self.ai_progress.visible = visible
        self._page.update()


    # PAGINA 4: GRAFICI

    def _build_grafici_page(self):
        header = ft.Container(
            content=ft.Column([
                ft.Text("Grafici", size=36, weight="bold", color=TESTO_CHIARO),
                ft.Text("Visualizzazione dati dal database", color=TESTO_SECONDARIO, size=14),
            ], horizontal_alignment="center", spacing=5),
            padding=ft.padding.only(bottom=20)
        )

        self.chart_selector = ft.Dropdown(
            label="Tipo di grafico", hint_text="Seleziona", width=350,
            border_color=BORDO, focused_border_color=BLU_PRIMARIO,
            bgcolor=BLU_SCURO, border_radius=12, color=TESTO_CHIARO,
            label_style=ft.TextStyle(color=TESTO_SECONDARIO),
            options=[
                ft.dropdown.Option("pages_per_operator", "Top 5 Operatori"),
                ft.dropdown.Option("pages_per_sede", "Pagine per Sede"),
                ft.dropdown.Option("pages_per_month", "Pagine per Mese"),
                ft.dropdown.Option("pages_per_ufficio", "Distribuzione per Ufficio"),
                ft.dropdown.Option("top_fascicoli", "Top 5 Fascicoli"),
            ]
        )

        self.btn_generate_chart = ft.ElevatedButton(
            text="Genera Grafico", icon=ft.icons.AUTO_GRAPH,
            style=ft.ButtonStyle(bgcolor=BLU_PRIMARIO, color="white", padding=20, shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=self._controller.handle_generate_chart if self._controller else None
        )

        self.chart_title_text = ft.Text("Seleziona un grafico", size=18, weight="w600", color=TESTO_CHIARO)
        
        self.chart_content = ft.Container(
            content=ft.Column([
                ft.Icon(name=ft.icons.BAR_CHART, color=TESTO_SECONDARIO, size=80),
                ft.Text("Seleziona un tipo di grafico e clicca 'Genera'", color=TESTO_SECONDARIO, size=14),
            ], horizontal_alignment="center", alignment="center", spacing=15),
            height=300, expand=True, alignment=ft.alignment.center
        )

        self.chart_container = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(name="auto_graph", color=BLU_PRIMARIO, size=24), self.chart_title_text], spacing=10),
                ft.Divider(height=20, color=BORDO),
                self.chart_content,
            ]),
            padding=30, bgcolor=BLU_SCURO, border_radius=20, border=ft.border.all(1, BORDO), width=850, height=420,
        )

        self.stat_card_pagine = self._create_stat_card("Totale Pagine", "---", ft.icons.DESCRIPTION, BLU_PRIMARIO)
        self.stat_card_operatori = self._create_stat_card("Operatori", "---", ft.icons.PEOPLE, VERDE)
        self.stat_card_fascicoli = self._create_stat_card("Fascicoli", "---", ft.icons.FOLDER, VIOLA)
        self.stat_card_media = self._create_stat_card("Media/Giorno", "---", ft.icons.TRENDING_UP, ARANCIO)

        return ft.Column([
            header,
            ft.Row([self.chart_selector, self.btn_generate_chart], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            ft.Container(height=20), self.chart_container,
            ft.Container(height=25),
            ft.Row([self.stat_card_pagine, self.stat_card_operatori, self.stat_card_fascicoli, self.stat_card_media],
                   alignment=ft.MainAxisAlignment.CENTER, spacing=20),
        ], horizontal_alignment="center", spacing=0, scroll=ft.ScrollMode.AUTO)

    def _create_stat_card(self, title, value, icon, color):
        value_text = ft.Text(value, size=24, weight="bold", color=TESTO_CHIARO)
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=28),
                value_text,
                ft.Text(title, size=12, color=TESTO_SECONDARIO),
            ], horizontal_alignment="center", spacing=5),
            padding=20, bgcolor=BLU_SCURO, border_radius=16, border=ft.border.all(1, BORDO), width=170,
            data={"value_text": value_text}
        )

    def update_chart(self, chart_type: str, data: list):
        if not data:
            return
        
        titles = {
            "pages_per_operator": "Top 5 Operatori per Pagine",
            "pages_per_sede": "Pagine per Sede",
            "pages_per_month": "Pagine Inserite per Mese",
            "pages_per_ufficio": "Distribuzione Pagine per Ufficio",
            "top_fascicoli": "Top 5 Fascicoli più Lavorati",
        }
        self.chart_title_text.value = titles.get(chart_type, "Grafico")
        
        if chart_type == "pages_per_ufficio":
            chart = self._create_pie_chart(data)
        elif chart_type == "pages_per_month":
            chart = self._create_line_chart(data)
        else:
            chart = self._create_bar_chart(data)
        
        self.chart_content.content = chart
        self._page.update()

    def _create_bar_chart(self, data: list) -> ft.BarChart:
        bar_groups, labels, max_val = [], [], 0
        
        for i, item in enumerate(data[:10]):
            nome = str(item.get("nome", f"Item {i+1}"))
            totale = int(item.get("totale", 0))
            max_val = max(max_val, totale)
            color = CHART_COLORS[i % len(CHART_COLORS)]
            bar_groups.append(ft.BarChartGroup(x=i, bar_rods=[
                ft.BarChartRod(from_y=0, to_y=totale, width=50, color=color, border_radius=4, tooltip=f"{nome}: {totale:,}")
            ]))
            labels.append(ft.ChartAxisLabel(value=i, label=ft.Text(nome[:12] + "..." if len(nome) > 12 else nome, color=TESTO_SECONDARIO, size=10)))
        
        return ft.BarChart(
            bar_groups=bar_groups, border=ft.border.all(1, BORDO),
            left_axis=ft.ChartAxis(labels_size=50, title=ft.Text("Pagine", color=TESTO_SECONDARIO), title_size=14),
            bottom_axis=ft.ChartAxis(labels=labels, labels_size=50),
            horizontal_grid_lines=ft.ChartGridLines(color=BORDO, width=1, dash_pattern=[3, 3]),
            tooltip_bgcolor=BLU_SCURO, max_y=max_val * 1.15 if max_val > 0 else 100, expand=True, animate=500,
        )

    def _create_pie_chart(self, data: list) -> ft.PieChart:
        sections = []
        total = sum(int(item.get("totale", 0)) for item in data)
        
        for i, item in enumerate(data[:8]):
            nome = str(item.get("nome", f"Item {i+1}"))
            totale = int(item.get("totale", 0))
            percentage = (totale / total * 100) if total > 0 else 0
            sections.append(ft.PieChartSection(
                value=totale, title=f"{nome}\n{percentage:.1f}%",
                title_style=ft.TextStyle(size=10, color=TESTO_CHIARO, weight="bold"),
                color=CHART_COLORS[i % len(CHART_COLORS)], radius=120,
            ))
        
        return ft.PieChart(sections=sections, sections_space=2, center_space_radius=50, expand=True, animate=500)

    def _create_line_chart(self, data: list) -> ft.LineChart:
        data_points, labels, max_val = [], [], 0
        
        for i, item in enumerate(data[-12:]):
            mese = str(item.get("mese", ""))
            totale = int(item.get("totale", 0))
            max_val = max(max_val, totale)
            data_points.append(ft.LineChartDataPoint(i, totale, tooltip=f"{mese}: {totale:,}"))
            if i % 2 == 0 or len(data) <= 6:
                labels.append(ft.ChartAxisLabel(value=i, label=ft.Text(mese[-5:] if len(mese) > 5 else mese, color=TESTO_SECONDARIO, size=10)))
        
        return ft.LineChart(
            data_series=[ft.LineChartData(
                data_points=data_points, stroke_width=3, color=BLU_PRIMARIO,
                curved=True, stroke_cap_round=True, below_line_bgcolor=f"{BLU_PRIMARIO}33",
            )],
            border=ft.border.all(1, BORDO),
            left_axis=ft.ChartAxis(labels_size=50, title=ft.Text("Pagine", color=TESTO_SECONDARIO), title_size=14),
            bottom_axis=ft.ChartAxis(labels=labels, labels_size=40),
            horizontal_grid_lines=ft.ChartGridLines(color=BORDO, width=1, dash_pattern=[3, 3]),
            tooltip_bgcolor=BLU_SCURO, min_y=0, max_y=max_val * 1.15 if max_val > 0 else 100, expand=True, animate=500,
        )

    def update_stats_cards(self, stats: dict):
        def fmt(n): return f"{n:,}".replace(",", ".")
        self.stat_card_pagine.data["value_text"].value = fmt(stats.get("totale_pagine", 0))
        self.stat_card_operatori.data["value_text"].value = fmt(stats.get("operatori", 0))
        self.stat_card_fascicoli.data["value_text"].value = fmt(stats.get("fascicoli", 0))
        self.stat_card_media.data["value_text"].value = fmt(stats.get("media_giorno", 0))


    # PAGINA 5: CONTROLLI UNIVOCITÀ

    def _build_controlli_page(self):
        header = ft.Container(
            content=ft.Column([
                ft.Text("Controlli Univocità", size=36, weight="bold", color=TESTO_CHIARO),
                ft.Text("Verifica della consistenza degli identificativi gestionali", color=TESTO_SECONDARIO, size=14),
            ], horizontal_alignment="center", spacing=5),
            padding=ft.padding.only(bottom=20)
        )

        self.btn_controlli = ft.ElevatedButton(
            text="Esegui Controlli", icon="verified",
            on_click=self._controller.handle_esegui_controlli if self._controller else None,
            style=ft.ButtonStyle(bgcolor=CIANO, color="white", padding=24, shape=ft.RoundedRectangleBorder(radius=12))
        )

        info_checks = ft.Container(
            content=ft.Column([
                ft.Text("Controlli eseguiti:", weight=ft.FontWeight.BOLD, color=TESTO_CHIARO),
                ft.Text("1. ID_Fascicolo univoco per Anno di riferimento (globalmente)", color=TESTO_SECONDARIO, size=12),
                ft.Text("2. Nome_operatore e ID_Operatore univoci (stessa coppia ovunque)", color=TESTO_SECONDARIO, size=12),
                ft.Text("3. Coerenza ID_attivita / Attivita (case insensitive)", color=TESTO_SECONDARIO, size=12),
                ft.Text("4. Ogni ID_Fascicolo presente in una sola Sede", color=TESTO_SECONDARIO, size=12),
            ], spacing=6),
            padding=20, bgcolor=BLU_SCURO_ALPHA, border_radius=16, border=ft.border.all(1, BORDO)
        )

        self.controlli_results = ft.ListView(expand=1, spacing=4, padding=15, auto_scroll=False)
        self.controlli_results.controls.append(
            ft.Text("Premi 'Esegui Controlli' per avviare la verifica.", color=TESTO_SECONDARIO, size=14, italic=True))

        results_container = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(name="verified", color=CIANO, size=20),
                        ft.Text("Risultati", weight="w600", color=TESTO_CHIARO, size=16)], spacing=8),
                ft.Divider(height=15, color=BORDO),
                ft.Container(content=self.controlli_results, expand=True),
            ]),
            padding=20, bgcolor=BLU_SCURO, border_radius=16, border=ft.border.all(1, BORDO),
            height=480, width=870,
        )

        return ft.Column([
            header,
            ft.Row([self.btn_controlli], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=15),
            info_checks,
            ft.Container(height=15),
            results_container,
        ], horizontal_alignment="center", spacing=0, scroll=ft.ScrollMode.AUTO)


    # UTILITY METHODS
    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message, color=TESTO_CHIARO), bgcolor=BLU_SCURO, shape=ft.RoundedRectangleBorder(radius=16))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    def update_page(self):
        self._page.update()
