from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import platform
import shutil
from typing import Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class SystemInfo:
    """Normalized view of the current host platform/distro."""

    system: str
    distro: Optional[str] = None
    distro_like: Tuple[str, ...] = ()
    pretty_name: Optional[str] = None

    def matches(self, systems: Sequence[str], distros: Sequence[str]) -> bool:
        system_check = not systems or self.system in systems
        if not system_check:
            return False

        if not distros:
            return True

        targets = {self.distro, *self.distro_like}
        return any(target in targets for target in distros if target)

    def friendly_name(self) -> str:
        if self.pretty_name:
            return self.pretty_name

        if self.system == "linux":
            if self.distro:
                return f"{self.distro.capitalize()} Linux"
            return "Linux"
        if self.system == "windows":
            return "Windows"
        if self.system == "darwin":
            return "macOS"
        return self.system.capitalize()


@dataclass(frozen=True)
class CommandSpec:
    """Represents a command option guarded by availability conditions."""

    binary: str
    command: str
    systems: Tuple[str, ...] = ("linux", "windows", "darwin")
    distros: Tuple[str, ...] = ()

    def is_available(self, info: SystemInfo) -> bool:
        if not info.matches(self.systems, self.distros):
            return False
        return shutil.which(self.binary) is not None


def _read_os_release() -> Mapping[str, str]:
    try:
        return platform.freedesktop_os_release()
    except (AttributeError, FileNotFoundError, OSError):
        data: dict[str, str] = {}
        try:
            with open("/etc/os-release", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    data[key] = value.strip().strip('"')
        except OSError:
            pass
        return data


@lru_cache(maxsize=1)
def detect_system() -> SystemInfo:
    system = platform.system().lower()
    distro: Optional[str] = None
    distro_like: Tuple[str, ...] = ()
    pretty_name: Optional[str] = None

    if system == "linux":
        data = _read_os_release()
        distro = data.get("ID", "").lower() or None
        like_field = data.get("ID_LIKE", "").lower().strip()
        if like_field:
            distro_like = tuple(filter(None, (token.strip() for token in like_field.split())))
        pretty_name = data.get("PRETTY_NAME") or data.get("NAME")
    elif system == "windows":
        release = platform.release()
        pretty_name = f"Windows {release}" if release else "Windows"
    elif system == "darwin":
        version = platform.mac_ver()[0]
        pretty_name = f"macOS {version}" if version else "macOS"

    return SystemInfo(system=system, distro=distro, distro_like=distro_like, pretty_name=pretty_name)


COMMAND_SETS: Mapping[str, Mapping[str, Sequence[CommandSpec] | str]] = {
    "processes": {
        "options": (
            CommandSpec("tasklist", "tasklist /v", systems=("windows",)),
            CommandSpec(
                "powershell",
                "powershell -Command \"Get-Process | Sort-Object CPU -Descending | Select-Object -First 30\"",
                systems=("windows",),
            ),
            CommandSpec(
                "ps",
                "ps -eo pid,user,%cpu,comm --sort=-%cpu | head -n 30",
                systems=("linux", "darwin"),
            ),
        ),
        "fallback": "Error: Process manager not identified.",
    },
    "network": {
        "options": (
            CommandSpec("ss", "ss -tunap", systems=("linux",)),
            CommandSpec(
                "powershell",
                "powershell -Command \"Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess, AppliedSetting\"",
                systems=("windows",),
            ),
            CommandSpec("netstat", "netstat -abno", systems=("linux", "windows", "darwin")),
        ),
        "fallback": "Error: Network tool not identified.",
    },
    "packages": {
        "options": (
            CommandSpec(
                "paru",
                "paru -Qe --color never --date | head -n 40",
                systems=("linux",),
                distros=("arch", "artix", "manjaro", "endeavouros", "garuda"),
            ),
            CommandSpec(
                "yay",
                "yay -Qe --color never --date | head -n 40",
                systems=("linux",),
                distros=("arch", "artix", "manjaro", "endeavouros", "garuda"),
            ),
            CommandSpec(
                "pacman",
                "LANG=C pacman -Qe --color never | head -n 40",
                systems=("linux",),
                distros=("arch", "artix", "manjaro", "endeavouros", "garuda"),
            ),
            CommandSpec(
                "rpm",
                "rpm -qa --last | head -n 40",
                systems=("linux",),
                distros=("fedora", "rhel", "centos", "rocky", "alma", "sles", "opensuse"),
            ),
            CommandSpec(
                "dpkg",
                "dpkg-query -W -f='${Package} ${Version}\\n' | head -n 40",
                systems=("linux",),
                distros=("debian", "ubuntu", "linuxmint", "pop", "elementary"),
            ),
            CommandSpec(
                "apk",
                "apk list --installed | head -n 40",
                systems=("linux",),
                distros=("alpine",),
            ),
            CommandSpec(
                "powershell",
                "powershell -Command \"Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion, InstallDate | Sort-Object InstallDate -Descending | Select-Object -First 40\"",
                systems=("windows",),
            ),
            CommandSpec("winget", "winget list", systems=("windows",)),
        ),
        "fallback": "Error: Package manager not identified.",
    },
}


def getCommand(command_type: str, system_info: Optional[SystemInfo] = None) -> str:
    command_type = command_type.lower()
    group = COMMAND_SETS.get(command_type)
    if not group:
        raise ValueError(f"Unsupported command type: {command_type}")

    info = system_info or detect_system()
    for spec in group["options"]:  # type: ignore[index]
        if isinstance(spec, CommandSpec) and spec.is_available(info):
            return spec.command

    return group["fallback"]  # type: ignore[index]


def get_system_info() -> SystemInfo:
    """Expose detected system information for other modules."""
    return detect_system()