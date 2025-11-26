import shutil

commands = {
    "process": {
        "tasklist": "tasklist /v",
        "Get-Process": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 30",
        "ps": "ps -eo pid,user,%cpu,comm --sort=-%cpu | head -n 30",
        "__not_found__": "Error: Process manager not identified."
    },
    "network": {
        "ss": "ss -tunap",
        "Get-NetTCPConnection": "Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess, AppliedSetting",
        "netstat": "netstat -abno",
        "__not_found__": "Error: Network tool not identified."
    },
    "packages": {
        "rpm": "rpm -qa --last | head -n 40",
        "dpkg": "dpkg-query -W -f='${Package} ${Version}\n' | head -n 40",
        "apk": "apk list --installed | head -n 40",
        "Get-ItemProperty": "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion, InstallDate | Sort-Object InstallDate -Descending | Select-Object -First 40",
        "winget": "winget list",
        "__not_found__": "Error: Package manager not identified."
    }
}

def getCommand(type: str):
    for key, command in commands[type].items():
        if shutil.which(key): 
            return command
    return commands[type]["__not_found__"]