from .commands import SystemInfo, getCommand, get_system_info
from dotenv import load_dotenv
from .prompts import PROMPTS
from google import genai
import subprocess
import os


class SystemAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.system_info: SystemInfo = get_system_info()

        if not api_key:
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def _run_cmd(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Erro: {str(e)}"

    def _collect_section(self, section: str) -> str:
        command = getCommand(section, self.system_info)
        if command.startswith("Error:"):
            return command
        return self._run_cmd(command)

    def get_prompt(self, mode, language="pt-br"):
        template = PROMPTS.get(language, PROMPTS["en"]).get(mode)
        
        if not template:
            return "Error: Prompt not found."

        system_name = self.system_info.friendly_name()
        format_kwargs = {"system_name": system_name}

        if mode == "processes":
            format_kwargs["data"] = self._collect_section("processes")
            return template.format(**format_kwargs)

        elif mode == "network":
            format_kwargs["data"] = self._collect_section("network")
            return template.format(**format_kwargs)

        elif mode == "packages":
            format_kwargs["data"] = self._collect_section("packages")
            return template.format(**format_kwargs)

        elif mode == "full":
            format_kwargs.update(
                {
                    "proc": self._collect_section("processes"),
                    "net": self._collect_section("network"),
                    "pkg": self._collect_section("packages"),
                }
            )
            return template.format(**format_kwargs)
            
        return ""

    def analyze(self, mode, model_id, language="pt-br"):
        if not self.client:
            return "❌ ERRO: Chave de API não encontrada no arquivo .env" if language == "pt-br" else "❌ ERROR: API Key not found in .env file"

        prompt = self.get_prompt(mode, language)
        try:
            response = self.client.models.generate_content(
                model=model_id, contents=prompt
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                return "⚠️ O sistema está sobrecarregado (Erro 429). Aguarde." if language == "pt-br" else "⚠️ System overloaded (Error 429). Please wait."
            return f"Erro de API: {error_msg}"