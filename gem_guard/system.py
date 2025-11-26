from .commands import getCommand
from dotenv import load_dotenv
from .prompts import PROMPTS
from google import genai
import subprocess
import os


class SystemAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
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

    def get_prompt(self, mode, language="pt-br"):
        template = PROMPTS.get(language, PROMPTS["en"]).get(mode)
        
        if not template:
            return "Error: Prompt not found."

        if mode == "process":
            data = self._run_cmd(getCommand("process"))
            return template.format(data=data)

        elif mode == "network":
            data = self._run_cmd(getCommand("network"))
            return template.format(data=data)

        elif mode == "packages":
            data = self._run_cmd(getCommand("packages"))
            return template.format(data=data)

        elif mode == "full":
            proc = self._run_cmd(getCommand("process"))
            net = self._run_cmd(getCommand("network"))
            pkg = self._run_cmd(getCommand("packages"))
            return template.format(proc=proc, net=net, pkg=pkg)
            
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