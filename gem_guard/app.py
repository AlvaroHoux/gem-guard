from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import Footer, Header, Static, Button, Markdown, LoadingIndicator, Select
from .system import SystemAnalyzer
from .reporting import ExportError, export_analysis
from textual import work
from pathlib import Path


LANGUAGE_STRINGS = {
    "en": {
        "buttons": {
            "processes": "Processes",
            "network": "Network",
            "packages": "Packages",
            "full": "Full Report",
        },
        "instruction": "Select a model and scan type...",
        "ready": "Ready",
        "done": "Done",
        "analyzing": "Analyzing ({model}): {mode}...",
        "mode_labels": {
            "processes": "PROCESSES",
            "network": "NETWORK",
            "packages": "PACKAGES",
            "full": "FULL",
        },
        "exports": {
            "html": "Export HTML",
            "pdf": "Export PDF",
            "missing": "Run a scan before exporting.",
            "success": "{fmt} saved to {path}",
            "error": "Export failed: {error}",
        },
    },
    "pt-br": {
        "buttons": {
            "processes": "Processos",
            "network": "Rede",
            "packages": "Pacotes",
            "full": "Relatório",
        },
        "instruction": "Selecione um modelo e um tipo de scan...",
        "ready": "Pronto",
        "done": "Pronto",
        "analyzing": "Analisando ({model}): {mode}...",
        "mode_labels": {
            "processes": "PROCESSOS",
            "network": "REDE",
            "packages": "PACOTES",
            "full": "RELATÓRIO",
        },
        "exports": {
            "html": "Exportar HTML",
            "pdf": "Exportar PDF",
            "missing": "Execute uma análise antes de exportar.",
            "success": "{fmt} salvo em {path}",
            "error": "Falha ao exportar: {error}",
        },
    },
    "zh-cn": {
        "buttons": {
            "processes": "进程",
            "network": "网络",
            "packages": "软件包",
            "full": "综合报告",
        },
        "instruction": "请选择模型与扫描类型...",
        "ready": "待命",
        "done": "完成",
        "analyzing": "正在分析 ({model})：{mode}...",
        "mode_labels": {
            "processes": "进程扫描",
            "network": "网络分析",
            "packages": "软件包审计",
            "full": "综合报告",
        },
        "exports": {
            "html": "导出 HTML 报告",
            "pdf": "导出 PDF 报告",
            "missing": "请先完成一次扫描再导出。",
            "success": "{fmt} 已保存到 {path}",
            "error": "导出失败：{error}",
        },
    },
}


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
        default_lang = "en"
        default_strings = LANGUAGE_STRINGS[default_lang]

        yield Header(show_clock=True)
        
        with Horizontal(id="toolbar"):
            yield Select(
                options=[
                    ("PT-BR", "pt-br"),
                    ("EN-US", "en"),
                    ("中文 (简体)", "zh-cn"),
                ],
                value=default_lang,
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
            
            yield Button(default_strings["buttons"]["processes"], id="btn-processes", variant="primary")
            yield Button(default_strings["buttons"]["network"], id="btn-network", variant="warning")
            yield Button(default_strings["buttons"]["packages"], id="btn-packages", variant="success")
            yield Button(default_strings["buttons"]["full"], id="btn-full", variant="error")
            yield Button(default_strings["exports"]["html"], id="btn-export-html", variant="primary", disabled=True)
            yield Button(default_strings["exports"]["pdf"], id="btn-export-pdf", variant="warning", disabled=True)

        with VerticalScroll(id="results-container"):
            yield Static(self._title_text(default_strings["ready"]), classes="title")
            yield LoadingIndicator(id="loading")
            yield Markdown(default_strings["instruction"], id="output-text")
        
        yield Footer()

    def on_mount(self):
        self.analyzer = SystemAnalyzer()
        self.latest_result = None
        self.export_dir = Path.cwd() / "reports"
        self.query_one("#loading").display = False

    def on_select_changed(self, event: Select.Changed) -> None:
        """Evento disparado quando qualquer Select muda de valor."""
        if event.select.id == "lang-select":
            self.update_interface_language(event.value)

    def update_interface_language(self, lang: str):
        """Atualiza os textos da interface (Botões, Títulos)"""
        strings = self._get_strings(lang)
        self.query_one("#btn-processes").label = strings["buttons"]["processes"]
        self.query_one("#btn-network").label = strings["buttons"]["network"]
        self.query_one("#btn-packages").label = strings["buttons"]["packages"]
        self.query_one("#btn-full").label = strings["buttons"]["full"]
        self.query_one("#btn-export-html").label = strings["exports"]["html"]
        self.query_one("#btn-export-pdf").label = strings["exports"]["pdf"]

        if not self.query_one("#loading").display:
            self.query_one("#output-text").update(strings["instruction"])
            self.query_one(".title").update(self._title_text(strings["ready"]))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id in {"btn-export-html", "btn-export-pdf"}:
            fmt = "html" if button_id.endswith("html") else "pdf"
            self.trigger_export(fmt)
            return

        mode = button_id.replace("btn-", "")
        
        selected_model = self.query_one("#model-select").value
        selected_lang = self.query_one("#lang-select").value
        
        self.query_one("#output-text").update("")
        self.query_one("#loading").display = True
        self._set_export_enabled(False)
        
        title_msg = self._get_strings(selected_lang)["analyzing"].format(
            model=selected_model,
            mode=self._mode_label(mode, selected_lang),
        )
        self.query_one(".title").update(title_msg)
        
        self.run_analysis(mode, selected_model, selected_lang)

    @work(thread=True)
    def run_analysis(self, mode: str, model_id: str, language: str):
        result = self.analyzer.perform_analysis(mode, model_id, language)
        self.call_from_thread(self.update_ui, result)

    def update_ui(self, analysis):
        language = analysis.language
        self.latest_result = analysis
        self.query_one("#loading").display = False
        self.query_one("#output-text").update(analysis.ai_markdown)
        done_label = self._get_strings(language)["done"]
        self.query_one(".title").update(self._title_text(done_label))
        self._set_export_enabled(True)

    def _get_strings(self, lang: str):
        return LANGUAGE_STRINGS.get(lang, LANGUAGE_STRINGS["en"])

    def _mode_label(self, mode: str, lang: str) -> str:
        return self._get_strings(lang)["mode_labels"].get(mode, mode.upper())

    def _title_text(self, suffix: str) -> str:
        return f"GEM GUARD AI 🛡️ - {suffix}"

    def _set_export_enabled(self, enabled: bool) -> None:
        for button_id in ("#btn-export-html", "#btn-export-pdf"):
            self.query_one(button_id).disabled = not enabled

    def trigger_export(self, fmt: str) -> None:
        language = self.query_one("#lang-select").value
        if not getattr(self, "latest_result", None):
            message = self._get_strings(language)["exports"]["missing"]
            self._notify(message, severity="warning")
            return
        self.run_export(fmt, language)

    @work(thread=True)
    def run_export(self, fmt: str, language: str):
        try:
            path = export_analysis(
                self.latest_result,
                fmt,
                directory=self.export_dir,
            )
            self.call_from_thread(self._handle_export_success, fmt, path, language)
        except ExportError as exc:
            self.call_from_thread(self._handle_export_error, fmt, str(exc), language)

    def _handle_export_success(self, fmt: str, path: Path, language: str) -> None:
        strings = self._get_strings(language)
        message = strings["exports"]["success"].format(fmt=fmt.upper(), path=str(path))
        self._notify(message, severity="success")

    def _handle_export_error(self, fmt: str, error: str, language: str) -> None:
        strings = self._get_strings(language)
        message = strings["exports"]["error"].format(error=error)
        self._notify(message, severity="error")

    def _notify(self, message: str, severity: str = "information") -> None:
        try:
            self.notify(message, severity=severity)
        except Exception:
            # Fallback: reflect message in title if notifications unsupported
            self.query_one(".title").update(self._title_text(message))