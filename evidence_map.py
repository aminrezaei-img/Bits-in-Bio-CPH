"""
Evidence map builder for Viably.
Renders an interactive HTML visualization — source groups expand/collapse,
records show full title on hover. Zero dependencies — pure HTML/CSS/JS.
"""
from typing import Any
import html as _html


def build_evidence_map_html(
    idea: str,
    papers: list[dict],
    trials: list[dict],
    drugs: list[dict],
    regulatory: list[dict] | None = None,
    patents: list[dict] | None = None,
    max_per_source: int = 5,
) -> str:
    """
    Build an interactive HTML evidence map.
    Source groups are clickable to expand/collapse. Records show
    full title on hover via title attribute. Max 25 nodes.
    """
    if regulatory is None:
        regulatory = []
    if patents is None:
        patents = []

    sources = [
        ("📄 Literature", papers[:max_per_source], "#4f46e5"),
        ("🔬 Trials", trials[:max_per_source], "#0891b2"),
        ("💊 Drugs", drugs[:max_per_source], "#7c3aed"),
        ("🏛️ Regulatory", regulatory[:max_per_source], "#b45309"),
        ("📜 Patents", patents[:max_per_source], "#059669"),
    ]

    active_sources = [(l, r, c) for l, r, c in sources if r]

    if not active_sources:
        return "<p style='text-align:center;color:#888;padding:40px'>No evidence to map.</p>"

    idea_escaped = _html.escape(idea[:80] + ("…" if len(idea) > 80 else ""))

    parts = [
        "<style>",
        ".ev-group{cursor:pointer;transition:all 0.2s;user-select:none}",
        ".ev-group:hover{transform:translateY(-1px);box-shadow:0 2px 8px rgba(0,0,0,0.1)}",
        ".ev-records{overflow:hidden;transition:max-height 0.3s ease}",
        ".ev-rec{position:relative;cursor:default}",
        ".ev-rec:hover{background:rgba(0,0,0,0.03)}",
        ".ev-tooltip{display:none;position:absolute;bottom:100%;left:0;right:0;",
        "  background:#1e293b;color:white;padding:6px 10px;border-radius:6px;",
        "  font-size:11px;z-index:10;line-height:1.4;margin-bottom:4px;",
        "  box-shadow:0 4px 12px rgba(0,0,0,0.2)}",
        ".ev-rec:hover .ev-tooltip{display:block}",
        "</style>",
    ]

    parts.append("<div style='font-family:system-ui,sans-serif;max-width:900px;margin:0 auto'>")

    # Center node
    parts.append(
        "<div style='text-align:center;margin-bottom:20px'>"
        "<div style='display:inline-block;background:#1e293b;color:white;padding:12px 20px;"
        "border-radius:10px;font-weight:600;font-size:14px;max-width:600px'>"
        f"💡 {idea_escaped}"
        "</div></div>"
    )

    # Connector
    parts.append(
        "<div style='text-align:center;margin-bottom:16px'>"
        "<div style='display:inline-block;width:3px;height:20px;background:#94a3b8;border-radius:2px'></div>"
        "</div>"
    )

    # Source groups
    parts.append("<div style='display:flex;flex-wrap:wrap;gap:10px;justify-content:center'>")

    for idx, (label, records, color) in enumerate(active_sources):
        uid = f"g{idx}"
        rec_count = len(records)

        # Group header (clickable)
        parts.append(
            f"<div class='ev-group' onclick=\"var r=document.getElementById('r{uid}');"
            f"r.style.maxHeight=r.style.maxHeight==='0px'?'800px':'0px';"
            f"this.querySelector('.arrow').textContent=r.style.maxHeight==='0px'?'▸':'▾'\""
            f" style='background:{color}15;border-left:4px solid {color};"
            f"border-radius:8px;padding:10px 14px;min-width:150px;max-width:240px;flex:1'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center'>"
            f"<span style='font-weight:600;font-size:13px;color:{color}'>{label} ({rec_count})</span>"
            f"<span class='arrow' style='color:{color};font-size:14px'>▾</span>"
            f"</div></div>"
        )

        # Records container (initially expanded)
        parts.append(
            f"<div id='r{uid}' class='ev-records' style='max-height:800px'>"
            f"<div style='padding:0 10px;margin-top:-2px'>"
        )

        for rec in records[:max_per_source]:
            title = rec.get("title") or rec.get("briefTitle") or rec.get("name") or "N/A"
            title_full = _html.escape(str(title))
            title_short = title_full[:70] + ("…" if len(title_full) > 70 else "")

            parts.append(
                f"<div class='ev-rec' style='font-size:11px;color:#475569;padding:4px 6px;"
                f"border-radius:4px;line-height:1.3'>"
                f"{title_short}"
                f"<div class='ev-tooltip'>{title_full}</div>"
                f"</div>"
            )

        parts.append("</div></div>")

    parts.append("</div>")
    parts.append("<p style='text-align:center;color:#94a3b8;font-size:10px;margin-top:12px'>Click source groups to expand/collapse · Hover records for full title</p>")
    parts.append("</div>")

    return "\n".join(parts)


def has_evidence(
    papers: list[dict],
    trials: list[dict],
    drugs: list[dict],
    regulatory: list[dict] | None = None,
    patents: list[dict] | None = None,
) -> bool:
    """Check if there's any evidence to map."""
    if regulatory is None:
        regulatory = []
    if patents is None:
        patents = []
    return bool(papers or trials or drugs or regulatory or patents)
