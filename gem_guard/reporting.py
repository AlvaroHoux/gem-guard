from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from markdown import markdown
from .commands import SystemInfo
import html
import re

try:
    from weasyprint import HTML  # type: ignore
except Exception:  # pragma: no cover - fallback when library missing
    HTML = None


SECTION_TITLES = {
    "processes": "Processes Snapshot",
    "network": "Network Connections",
    "packages": "Package Activity",
}


@dataclass(slots=True)
class SectionCapture:
    key: str
    command: str
    output: str

    @property
    def title(self) -> str:
        return SECTION_TITLES.get(self.key, self.key.title())


@dataclass(slots=True)
class AnalysisResult:
    mode: str
    language: str
    model_id: str
    timestamp: datetime
    system: SystemInfo
    prompt: str
    ai_markdown: str
    sections: Dict[str, SectionCapture]

    def default_stem(self) -> str:
        timestamp = self.timestamp.strftime("%Y%m%d-%H%M%S")
        return f"gem-guard-{self.mode}-{timestamp}"


class ExportError(RuntimeError):
    pass


def _ensure_dir(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip())
    return slug.strip("-") or "gem-guard-report"


def _build_metadata_rows(analysis: AnalysisResult) -> str:
    info = analysis.system
    rows = [
        ("Mode", analysis.mode.title()),
        ("Language", analysis.language),
        ("Model", analysis.model_id),
        ("System", info.friendly_name()),
        ("Timestamp", analysis.timestamp.isoformat()),
    ]
    html_rows = []
    for label, value in rows:
        html_rows.append(
            f"<tr><th>{html.escape(label)}</th><td>{html.escape(value)}</td></tr>"
        )
    return "".join(html_rows)


def _render_sections(analysis: AnalysisResult) -> str:
    blocks = []
    for capture in analysis.sections.values():
        command_html = html.escape(capture.command or "(command unavailable)")
        output_html = html.escape(capture.output or "(no output)")
        blocks.append(
            """
            <section class="snapshot">
              <header>
                <h3>{title}</h3>
                <p class="command"><span>Command</span> {command}</p>
              </header>
              <pre><code>{output}</code></pre>
            </section>
            """.format(
                title=html.escape(capture.title),
                command=command_html,
                output=output_html,
            )
        )
    return "".join(blocks)


def build_html_document(analysis: AnalysisResult) -> str:
    body_html = markdown(
        analysis.ai_markdown or "",
        extensions=["extra", "sane_lists", "tables"],
        output_format="html5",
    )

    metadata_rows = _build_metadata_rows(analysis)
    section_blocks = _render_sections(analysis)

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>GemGuard AI Report</title>
  <style>
    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0;
      padding: 0;
      background: #0b1117;
      color: #e2e8f0;
      line-height: 1.6;
    }}
    main {{
      max-width: 960px;
      margin: auto;
      padding: 2rem;
    }}
    header.report-header {{
      text-align: center;
      margin-bottom: 2rem;
    }}
    header.report-header h1 {{
      margin: 0;
      font-size: 2.2rem;
    }}
    header.report-header p {{
      margin: 0.3rem 0;
      color: #94a3b8;
    }}
    table.meta {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 1.5rem;
      background: rgba(148, 163, 184, 0.08);
      border: 1px solid rgba(148, 163, 184, 0.2);
    }}
    table.meta th {{
      text-align: left;
      padding: 0.6rem 0.8rem;
      width: 25%;
      background: rgba(148, 163, 184, 0.15);
    }}
    table.meta td {{
      padding: 0.6rem 0.8rem;
    }}
    section.analysis {{
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 12px 30px rgba(15, 23, 42, 0.5);
    }}
    section.analysis h2 {{
      margin-top: 0;
    }}
    section.snapshot {{
      margin-top: 2rem;
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 12px;
      background: rgba(15, 23, 42, 0.7);
      overflow: hidden;
    }}
    section.snapshot header {{
      padding: 1rem 1.2rem;
      border-bottom: 1px solid rgba(148, 163, 184, 0.15);
    }}
    section.snapshot h3 {{
      margin: 0 0 0.4rem 0;
    }}
    section.snapshot p.command {{
      margin: 0;
      color: #94a3b8;
      font-size: 0.9rem;
    }}
    section.snapshot p.command span {{
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 0.75rem;
      margin-right: 0.4rem;
      color: #38bdf8;
    }}
    section.snapshot pre {{
      margin: 0;
      padding: 1.2rem;
      background: rgba(2, 6, 23, 0.85);
      color: #cbd5f5;
      overflow-x: auto;
      font-size: 0.85rem;
      line-height: 1.45;
    }}
    section.snapshot code {{
      font-family: 'JetBrains Mono', 'Fira Code', 'SFMono-Regular', monospace;
    }}
    footer {{
      text-align: center;
      margin-top: 2rem;
      color: #64748b;
    }}
    a {{
      color: #38bdf8;
    }}
  </style>
</head>
<body>
  <main>
    <header class=\"report-header\">
      <h1>GemGuard AI Report</h1>
      <p>Enhanced visualization snapshot generated via Gemini</p>
    </header>

    <table class=\"meta\">
      <tbody>
        {metadata_rows}
      </tbody>
    </table>

    <section class=\"analysis\">
      {body_html}
    </section>

    {section_blocks}

    <footer>
      Generated by GemGuard AI • {html.escape(analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S'))}
    </footer>
  </main>
</body>
</html>
"""


def export_analysis(
    analysis: AnalysisResult,
    fmt: str,
    directory: Optional[Path] = None,
    filename: Optional[str] = None,
) -> Path:
    fmt = fmt.lower()
    if fmt not in {"html", "pdf"}:
        raise ExportError(f"Unsupported export format: {fmt}")

    directory = directory or (Path.cwd() / "reports")
    _ensure_dir(directory)

    stem = _slugify(filename) if filename else analysis.default_stem()
    output_path = directory / f"{stem}.{fmt}"

    html_document = build_html_document(analysis)

    if fmt == "html":
        output_path.write_text(html_document, encoding="utf-8")
        return output_path

    if HTML is None:
        raise ExportError(
            "PDF export requires the 'weasyprint' dependency. Install it via 'pip install weasyprint'."
        )

    HTML(string=html_document).write_pdf(str(output_path))
    return output_path
