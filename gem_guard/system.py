from .commands import SystemInfo, getCommand, get_system_info
from .reporting import AnalysisResult, SectionCapture
from dotenv import load_dotenv
from .prompts import PROMPTS
from google import genai
from datetime import datetime
import subprocess
import os


ERROR_MESSAGES = {
    "pt-br": {
        "missing_api_key": "❌ ERRO: Chave de API não encontrada no arquivo .env",
        "rate_limited": "⚠️ O sistema está sobrecarregado (Erro 429). Aguarde.",
        "api_error": "Erro de API: {error}",
    },
    "en": {
        "missing_api_key": "❌ ERROR: API key not found in .env file",
        "rate_limited": "⚠️ System overloaded (Error 429). Please wait.",
        "api_error": "API error: {error}",
    },
    "zh-cn": {
        "missing_api_key": "❌ 错误：未在 .env 中找到 GEMINI_API_KEY",
        "rate_limited": "⚠️ 系统繁忙（429）。请稍候重试。",
        "api_error": "API 错误：{error}",
    },
}


class SystemAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.system_info: SystemInfo = get_system_info()

        if not api_key:
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def _messages(self, language: str):
        return ERROR_MESSAGES.get(language, ERROR_MESSAGES["en"])

    def _run_cmd(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Erro: {str(e)}"

    def _capture_section(self, section: str) -> SectionCapture:
        command = getCommand(section, self.system_info)
        if command.startswith("Error:"):
            output = command
        else:
            output = self._run_cmd(command) or "(no data returned)"
        return SectionCapture(key=section, command=command, output=output)

    def _sections_for_mode(self, mode: str):
        if mode == "full":
            keys = ("processes", "network", "packages")
        elif mode in ("processes", "network", "packages"):
            keys = (mode,)
        else:
            keys = ()

        return {key: self._capture_section(key) for key in keys}

    def _build_prompt(self, mode, language="pt-br"):
        template = PROMPTS.get(language, PROMPTS["en"]).get(mode)
        sections = self._sections_for_mode(mode)

        if not template:
            return "", sections

        system_name = self.system_info.friendly_name()
        format_kwargs = {"system_name": system_name}

        if mode == "processes":
            format_kwargs["data"] = sections["processes"].output

        elif mode == "network":
            format_kwargs["data"] = sections["network"].output

        elif mode == "packages":
            format_kwargs["data"] = sections["packages"].output

        elif mode == "full":
            format_kwargs.update(
                {
                    "proc": sections["processes"].output,
                    "net": sections["network"].output,
                    "pkg": sections["packages"].output,
                }
            )
        else:
            return "", sections

        return template.format(**format_kwargs), sections

    def perform_analysis(self, mode, model_id, language="pt-br") -> AnalysisResult:
        messages = self._messages(language)
        prompt, sections = self._build_prompt(mode, language)

        if not prompt:
            ai_text = messages["api_error"].format(error="Prompt not found.")
        elif not self.client:
            ai_text = messages["missing_api_key"]
        else:
            try:
                response = self.client.models.generate_content(
                    model=model_id, contents=prompt
                )
                ai_text = response.text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    ai_text = messages["rate_limited"]
                else:
                    ai_text = messages["api_error"].format(error=error_msg)

        return AnalysisResult(
            mode=mode,
            language=language,
            model_id=model_id,
            timestamp=datetime.utcnow(),
            system=self.system_info,
            prompt=prompt,
            ai_markdown=ai_text,
            sections=sections,
        )

    def analyze(self, mode, model_id, language="pt-br"):
        return self.perform_analysis(mode, model_id, language).ai_markdown