from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Footer, Header, Static, Button, Markdown, LoadingIndicator, Select
from .system import SystemAnalyzer
from textual import work


class GemGuardApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    
    #toolbar {
        dock: top;
        height: 5;
        margin-bottom: 1;
        align: center middle;
        background: $boost;
        padding: 1;
    }

    Button {
        margin: 0 1;
        min-width: 12;
    }
    
    /* Estilo Genérico para os Selects */
    Select {
        margin-right: 2;
    }
    
    #model-select {
        width: 30;
    }
    
    #lang-select {
        width: 15;
    }

    #results-container {
        width: 90%;
        height: 80%;
        border: solid green;
        padding: 1 2;
        background: $surface;
    }

    Markdown {
        padding: 1;
    }

    .title {
        text-align: center;
        text-style: bold;
        color: $secondary;
        margin-bottom: 1;
    }
    """

    BINDINGS = [("d", "toggle_dark", "Modo Escuro/Dark Mode"), ("q", "quit", "Sair/Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal(id="toolbar"):
            yield Select(
                options=[
                    ("PT-BR", "pt-br"),
                    ("EN-US", "en"),
                ],
                value="en",
                allow_blank=False,
                id="lang-select"
            )

            yield Select(
                options=[
                    ("Gemini 3 Pro Preview 🧪", "gemini-3-pro-preview"),
                    ("Gemini 2.5 Pro 🧠", "gemini-2.5-pro"),
                    ("Gemini 2.5 Flash ⚡", "gemini-2.5-flash"),
                    ("Gemini 2.5 Flash Lite 💡", "gemini-2.5-flash-lite"),
                    ("Gemini 2 Flash ⚡", "gemini-2.0-flash"),
                    ("Gemini 2 Flash Lite 💡", "gemini-2.0-flash-lite"),
                ],
                value="gemini-2.0-flash",
                allow_blank=False,
                id="model-select"
            )
            
            yield Button("Processos", id="btn-process", variant="primary")
            yield Button("Rede", id="btn-network", variant="warning")
            yield Button("Pacotes", id="btn-packages", variant="success")
            yield Button("Relatório", id="btn-full", variant="error")

        with VerticalScroll(id="results-container"):
            yield Static("GEM GUARD AI 🛡️", classes="title")
            yield LoadingIndicator(id="loading")
            yield Markdown("Selecione um idioma, modelo e tipo de scan...", id="output-text")
        
        yield Footer()

    def on_mount(self):
        self.analyzer = SystemAnalyzer()
        self.query_one("#loading").display = False

    def on_select_changed(self, event: Select.Changed) -> None:
        """Evento disparado quando qualquer Select muda de valor."""
        if event.select.id == "lang-select":
            self.update_interface_language(event.value)

    def update_interface_language(self, lang: str):
        """Atualiza os textos da interface (Botões, Títulos)"""
        if lang == "en":
            self.query_one("#btn-process").label = "Processes"
            self.query_one("#btn-network").label = "Network"
            self.query_one("#btn-packages").label = "Packages"
            self.query_one("#btn-full").label = "Full Report"
            
            if not self.query_one("#loading").display:
                self.query_one("#output-text").update("Select a model and scan type...")
                self.query_one(".title").update("GEM GUARD AI 🛡️ - Ready")
        else:
            self.query_one("#btn-process").label = "Processos"
            self.query_one("#btn-network").label = "Rede"
            self.query_one("#btn-packages").label = "Pacotes"
            self.query_one("#btn-full").label = "Relatório"
            
            if not self.query_one("#loading").display:
                self.query_one("#output-text").update("Selecione um modelo e um tipo de scan...")
                self.query_one(".title").update("GEM GUARD AI 🛡️ - Pronto")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        mode = button_id.replace("btn-", "")
        
        selected_model = self.query_one("#model-select").value
        selected_lang = self.query_one("#lang-select").value
        
        self.query_one("#output-text").update("")
        self.query_one("#loading").display = True
        
        msg = f"Analisando ({selected_model}): {mode.upper()}..." if selected_lang == "pt-br" else f"Analyzing ({selected_model}): {mode.upper()}..."
        self.query_one(".title").update(msg)
        
        self.run_analysis(mode, selected_model, selected_lang)

    @work(thread=True)
    def run_analysis(self, mode: str, model_id: str, language: str):
        result_text = self.analyzer.analyze(mode, model_id, language)
        self.call_from_thread(self.update_ui, result_text, language)

    def update_ui(self, text, language):
        self.query_one("#loading").display = False
        self.query_one("#output-text").update(text)
        
        status = "Pronto" if language == "pt-br" else "Done"
        self.query_one(".title").update(f"GEM GUARD AI 🛡️ - {status}")