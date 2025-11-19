from dotenv import load_dotenv
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

    def get_prompt(self, mode):
        if mode == "process":
            data = self._run_cmd("ps -eo pid,user,%cpu,comm --sort=-%cpu | head -n 30")
            return f"""Analise os processos do Fedora ordenados por uso de CPU.

    Identifique e reporte apenas itens suspeitos:
    - Processos com nomes genéricos ou ofuscados (ex: "a", "x", strings aleatórias)
    - Usuários inesperados executando processos privilegiados
    - Consumo anômalo de CPU (muito alto ou processos não reconhecidos)
    - Múltiplas instâncias do mesmo processo incomum

    Para cada item suspeito, indique:
    1. PID, usuário e comando
    2. Por que é suspeito (1 linha)
    3. Nível de risco: BAIXO/MÉDIO/ALTO

    Ignore processos comuns do sistema (systemd, gnome, firefox, chrome, etc).
    Seja objetivo e conciso.

    Dados:
    {data}"""

        elif mode == "network":
            data = self._run_cmd("ss -tunap")
            return f"""Analise as conexões de rede do comando ss -tunap.

    Identifique e reporte apenas conexões suspeitas:
    - Portas não padrão em LISTEN de processos desconhecidos
    - Conexões ESTABLISHED para IPs/portas suspeitas
    - Processos de rede com nomes genéricos ou sem identificação
    - Múltiplas conexões para o mesmo IP externo
    - Portas de backdoors conhecidas (1234, 4444, 5555, 6666, etc)

    Para cada item suspeito:
    1. Estado, porta local/remota, processo
    2. Por que é suspeito (1 linha)
    3. Nível de risco: BAIXO/MÉDIO/ALTO

    Ignore conexões legítimas (DNS:53, HTTP:80/443, SSH:22 para IPs confiáveis, serviços systemd).
    Máximo 3 linhas por item.

    Dados:
    {data}"""

        elif mode == "packages":
            data = self._run_cmd("rpm -qa --last | head -n 40")
            return f"""Analise os pacotes recentemente instalados no Fedora.

    Identifique e reporte apenas pacotes suspeitos ou incomuns:
    - Pacotes com nomes genéricos, ofuscados ou não relacionados ao Fedora
    - Ferramentas de hacking/pentest não justificadas
    - Pacotes compilados localmente suspeitos
    - Dependências estranhas instaladas recentemente
    - Pacotes de repositórios não oficiais

    Para cada item suspeito:
    1. Nome do pacote e data de instalação
    2. Por que é suspeito (1 linha)
    3. Nível de risco: BAIXO/MÉDIO/ALTO

    Ignore atualizações normais do sistema (kernel, lib*, gnome*, systemd, dnf, rpm, etc).
    Seja direto e objetivo.

    Dados:
    {data}"""

        elif mode == "full":
            proc = self._run_cmd("ps -eo user,%cpu,comm --sort=-%cpu | head -n 15")
            net = self._run_cmd("ss -tunap | grep LISTEN")
            return f"""Gere um relatório executivo de segurança cruzando dados de processos e rede.

    ESTRUTURA DO RELATÓRIO:

    1. RESUMO EXECUTIVO (3-4 linhas)
    - Status geral: NORMAL/ATENÇÃO/CRÍTICO
    - Principais achados

    2. ACHADOS CRÍTICOS (se houver)
    - Correlações suspeitas entre processo e rede
    - Processos desconhecidos com portas abertas
    - Alto consumo de recursos + atividade de rede anômala

    3. PROCESSOS SUSPEITOS (se houver)
    - Liste apenas anomalias com nível de risco

    4. REDE SUSPEITA (se houver)
    - Portas LISTEN suspeitas vinculadas a processos

    5. RECOMENDAÇÕES (máximo 3 ações prioritárias)

    Seja conciso. Omita seções sem achados. Foque em correlações de segurança.

    DADOS:

    Processos (Top CPU):
    {proc}

    Rede (Portas LISTEN):
    {net}"""

    def analyze(self, mode, model_id):
        if not self.client:
            return "❌ ERRO: Chave de API não encontrada no arquivo .env"

        prompt = self.get_prompt(mode)
        try:
            response = self.client.models.generate_content(
                model=model_id, contents=prompt
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                return "⚠️ O sistema está sobrecarregado (Erro 429). Aguarde 1 minuto e tente novamente."
            return f"Erro de API: {error_msg}"
