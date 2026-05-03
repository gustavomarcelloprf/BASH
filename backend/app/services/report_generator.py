from __future__ import annotations

from datetime import datetime
from typing import Any

from weasyprint import HTML


def _html(entries: list[Any], period_label: str) -> str:
    generated = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Aggregate by project
    by_project: dict[int, dict] = {}
    for e in entries:
        pid = e["project_id"]
        if pid not in by_project:
            by_project[pid] = {
                "name": e.get("project_name", f"Projeto {pid}"),
                "hours": 0.0,
                "budget_hours": e.get("budget_hours", 0.0),
            }
        by_project[pid]["hours"] += e["hours"]

    # Aggregate by user
    by_user: dict[int, dict] = {}
    for e in entries:
        uid = e["user_id"]
        if uid not in by_user:
            by_user[uid] = {"name": e.get("user_name", f"Usuário {uid}"), "hours": 0.0}
        by_user[uid]["hours"] += e["hours"]

    def row_class(i: int) -> str:
        return 'class="alt"' if i % 2 == 1 else ""

    project_rows = "".join(
        f'<tr {row_class(i)}>'
        f'<td>{p["name"]}</td>'
        f'<td class="num">{p["hours"]:.1f}h</td>'
        f'<td class="num">'
        + (
            f'{p["hours"] / p["budget_hours"] * 100:.0f}%'
            if p["budget_hours"] > 0
            else "—"
        )
        + "</td></tr>"
        for i, p in enumerate(sorted(by_project.values(), key=lambda x: -x["hours"]))
    )

    user_rows = "".join(
        f'<tr {row_class(i)}>'
        f'<td>{u["name"]}</td>'
        f'<td class="num">{u["hours"]:.1f}h</td>'
        "</tr>"
        for i, u in enumerate(sorted(by_user.values(), key=lambda x: -x["hours"]))
    )

    total = sum(e["hours"] for e in entries)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  body {{
    font-family: Arial, sans-serif;
    font-size: 11pt;
    color: #111;
    margin: 2cm 2.5cm;
  }}
  header {{
    border-bottom: 1px solid #333;
    padding-bottom: 6pt;
    margin-bottom: 18pt;
  }}
  header h1 {{
    font-size: 16pt;
    font-weight: bold;
    margin: 0 0 2pt 0;
    letter-spacing: 0.04em;
  }}
  header p {{
    font-size: 9pt;
    color: #666;
    margin: 0;
  }}
  h2 {{
    font-size: 11pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #333;
    margin: 18pt 0 6pt 0;
    border-bottom: 1px solid #e5e5e5;
    padding-bottom: 3pt;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 10pt;
  }}
  th {{
    text-align: left;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #666;
    padding: 4pt 6pt;
    border-bottom: 1px solid #333;
  }}
  td {{
    padding: 5pt 6pt;
    border-bottom: 1px solid #f0f0f0;
  }}
  td.num {{
    text-align: right;
    font-family: monospace;
  }}
  tr.alt td {{
    background: #f5f5f5;
  }}
  .total-row td {{
    font-weight: bold;
    border-top: 1px solid #333;
    border-bottom: none;
  }}
  footer {{
    margin-top: 24pt;
    font-size: 8pt;
    color: #aaa;
    border-top: 1px solid #e5e5e5;
    padding-top: 6pt;
  }}
</style>
</head>
<body>
<header>
  <h1>DASH &middot; {period_label}</h1>
  <p>gerado em {generated}</p>
</header>

<h2>Horas por Projeto</h2>
<table>
  <thead>
    <tr>
      <th>Projeto</th>
      <th style="text-align:right">Total</th>
      <th style="text-align:right">% Budget</th>
    </tr>
  </thead>
  <tbody>
    {project_rows}
    <tr class="total-row">
      <td>Total</td>
      <td class="num">{total:.1f}h</td>
      <td></td>
    </tr>
  </tbody>
</table>

<h2>Horas por Colaborador</h2>
<table>
  <thead>
    <tr>
      <th>Colaborador</th>
      <th style="text-align:right">Total</th>
    </tr>
  </thead>
  <tbody>
    {user_rows}
  </tbody>
</table>

<footer>gerado em {generated} &bull; DASH &mdash; rastreio de horas</footer>
</body>
</html>"""


def generate_pdf(entries: list[Any], period_label: str) -> bytes:
    html = _html(entries, period_label)
    return HTML(string=html).write_pdf()
