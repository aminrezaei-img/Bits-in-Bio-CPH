"""
Evidence map builder for Viably.
Renders a simple HTML visualization showing the project idea
connected to retrieved evidence across source groups.
Zero dependencies — pure HTML/CSS, no networkx needed.
"""
from typing import Any


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
    Build an HTML evidence map: center node (idea) connected to source groups,
    each showing top records. Returns HTML string for st.components.v1.html().

    Rules per MVP spec §10:
    - Max 25 total nodes
    - Center node = user idea
    - Edges = "retrieved as relevant"
    """
    if regulatory is None:
        regulatory = []
    if patents is None:
        patents = []

    sources = [
        ("📄 Literature", papers[:max_per_source], "#4f46e5", "bg1"),
        ("🔬 Trials", trials[:max_per_source], "#0891b2", "bg2"),
        ("💊 Drugs", drugs[:max_per_source], "#7c3aed", "bg3"),
        ("🏛️ Regulatory", regulatory[:max_per_source], "#b45309", "bg4"),
        ("📜 Patents", patents[:max_per_source], "#059669", "bg5"),
    ]

    # Filter to sources with records, cap total nodes at 25
    total_nodes = 0
    active_sources = []
    for label, records, color, css_class in sources:
        if records:
            active_sources.append((label, records[:max_per_source], color, css_class))
            total_nodes += min(len(records), max_per_source)

    if not active_sources:
        return "<p style='text-align:center;color:#888;padding:40px'>No evidence to map.</p>"

    # Build HTML
    idea_short = idea[:80] + ("…" if len(idea) > 80 else "")
    html_parts = [
        "<div style='font-family:system-ui,sans-serif;max-width:900px;margin:0 auto'>",
        # Center node
        "<div style='text-align:center;margin-bottom:24px'>",
        "<div style='display:inline-block;background:#1e293b;color:white;padding:14px 24px;border-radius:12px;font-weight:600;font-size:15px;max-width:600px'>",
        f"💡 {idea_short}",
        "</div></div>",
        # Connector line
        "<div style='text-align:center;margin-bottom:16px'>",
        "<div style='display:inline-block;width:3px;height:24px;background:#94a3b8;border-radius:2px'></div>",
        "</div>",
        # Source groups grid
        "<div style='display:flex;flex-wrap:wrap;gap:12px;justify-content:center'>",
    ]

    for label, records, color, _ in active_sources:
        html_parts.append(
            f"<div style='background:{color}15;border-left:4px solid {color};"
            f"border-radius:8px;padding:12px 16px;min-width:160px;max-width:220px;flex:1'>"
            f"<div style='font-weight:600;font-size:13px;color:{color};margin-bottom:8px'>{label} ({len(records)})</div>"
        )
        for rec in records[:max_per_source]:
            title = rec.get("title") or rec.get("briefTitle") or rec.get("name") or "N/A"
            title = title[:70] + ("…" if len(str(title)) > 70 else "")
            html_parts.append(
                f"<div style='font-size:11px;color:#475569;padding:3px 0;"
                f"border-bottom:1px solid {color}10;line-height:1.3'>{title}</div>"
            )
        html_parts.append("</div>")

    html_parts.append("</div>")
    html_parts.append("</div>")

    return "\n".join(html_parts)


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
