PROMPTS = {
    "pt-br": {
        "process": """Analise os processos do Fedora ordenados por uso de CPU.

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
        {data}""",
        "network": """Analise as conexões de rede do comando ss -tunap.

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
        {data}""",
        "packages": """Analise os pacotes recentemente instalados no Fedora.

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
        {data}""",
        "full": """Gere um relatório executivo de segurança cruzando dados de processos e rede.

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
        {net}""",
    },
    "en": {
        "process": """Analyze Fedora processes sorted by CPU usage.

        Identify and report ONLY suspicious items:
        - Processes with generic or obfuscated names (e.g., "a", "x", random strings)
        - Unexpected users running privileged processes
        - Anomalous CPU consumption (too high or unrecognized processes)
        - Multiple instances of the same unusual process

        For each suspicious item, indicate:
        1. PID, user, and command
        2. Why it is suspicious (1 line)
        3. Risk Level: LOW/MEDIUM/HIGH

        Ignore common system processes (systemd, gnome, firefox, chrome, etc.).
        Be objective and concise.

        Data:
        {data}""",
        "network": """Analyze network connections from 'ss -tunap'.

        Identify and report ONLY suspicious connections:
        - Non-standard LISTEN ports from unknown processes
        - ESTABLISHED connections to suspicious IPs/ports
        - Network processes with generic or unidentified names
        - Multiple connections to the same external IP
        - Known backdoor ports (1234, 4444, 5555, 6666, etc.)

        For each suspicious item:
        1. State, local/remote port, process
        2. Why it is suspicious (1 line)
        3. Risk Level: LOW/MEDIUM/HIGH

        Ignore legitimate connections (DNS:53, HTTP:80/443, SSH:22 for trusted IPs, systemd services).
        Max 3 lines per item.

        Data:
        {data}""",
        "packages": """Analyze recently installed packages on Fedora.

        Identify and report ONLY suspicious or unusual packages:
        - Packages with generic, obfuscated names or unrelated to Fedora
        - Unjustified hacking/pentest tools
        - Suspicious locally compiled packages
        - Strange dependencies installed recently
        - Packages from unofficial repositories

        For each suspicious item:
        1. Package name and installation date
        2. Why it is suspicious (1 line)
        3. Risk Level: LOW/MEDIUM/HIGH

        Ignore normal system updates (kernel, lib*, gnome*, systemd, dnf, rpm, etc.).
        Be direct.

        Data:
        {data}""",
        "full": """Generate an executive security report crossing process and network data.

        REPORT STRUCTURE:

        1. EXECUTIVE SUMMARY (3-4 lines)
        - General Status: NORMAL/WARNING/CRITICAL
        - Key findings

        2. CRITICAL FINDINGS (if any)
        - Suspicious correlations between process and network
        - Unknown processes with open ports
        - High resource consumption + anomalous network activity

        3. SUSPICIOUS PROCESSES (if any)
        - List only anomalies with risk level

        4. SUSPICIOUS NETWORK (if any)
        - Suspicious LISTEN ports linked to processes

        5. RECOMMENDATIONS (max 3 priority actions)

        Be concise. Omit sections without findings. Focus on security correlations.

        DATA:

        Processes (Top CPU):
        {proc}

        Network (LISTEN Ports):
        {net}"""
    },
}
