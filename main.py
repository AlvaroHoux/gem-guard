
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Footer, Header, Static, Button, Markdown, LoadingIndicator, Select
from textual import work
from system import SystemAnalyzer

class GemGuardApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    
    #toolbar {
        dock: top;
        height: 5; /* Aumentei um pouco para caber o Select confortavelmente */
        margin-bottom: 1;
        align: center middle;
        background: $boost;
        padding: 1;
    }

    Button {
        margin: 0 1;
        min-width: 12;
    }
    
    /* Estilo do Menu de Seleção */
    Select {
        width: 30;
        margin-right: 2;
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

    BINDINGS = [("d", "toggle_dark", "Modo Escuro"), ("q", "quit", "Sair")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Horizontal(id="toolbar"):
            # Adicionamos o Select aqui com as opções
            yield Select(
                options=[
                    ("Gemini 3 Pro Preview 🧪", "gemini-3-pro-preview"),
                    ("Gemini 2.5 Pro 🧠", "gemini-2.5-pro"),
                    ("Gemini 2.5 Flash ⚡", "gemini-2.5-flash"),
                    ("Gemini 2.5 Flash Lite 💡", "gemini-2.5-flash-lite"),
                    ("Gemini 2 Flash ⚡", "gemini-2.0-flash"),
                    ("Gemini 2 Flash Lite 💡", "gemini-2.0-flash-lite"),
                ],
                value="gemini-2.0-flash", # Valor padrão seguro
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
            yield Markdown("Selecione um modelo e um tipo de scan...", id="output-text")
        
        yield Footer()

    def on_mount(self):
        self.analyzer = SystemAnalyzer()
        self.query_one("#loading").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        mode = button_id.replace("btn-", "")
        
        selected_model = self.query_one("#model-select").value
        
        self.query_one("#output-text").update("")
        self.query_one("#loading").display = True
        self.query_one(".title").update(f"Analisando ({selected_model}): {mode.upper()}...")
        
        self.run_analysis(mode, selected_model)

    @work(thread=True)
    def run_analysis(self, mode: str, model_id: str):
        result_text = self.analyzer.analyze(mode, model_id)
        app.call_from_thread(self.update_ui, result_text)

    def update_ui(self, text):
        self.query_one("#loading").display = False
        self.query_one("#output-text").update(text)
        self.query_one(".title").update("GEM GUARD AI 🛡️ - Pronto")

if __name__ == "__main__":
    app = GemGuardApp()
    app.run()