"""Phase 7 reporting, recommendations, and synchronized replay services."""
from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Recommendation:
    category: str
    priority: str
    message: str
    evidence: str


class RecommendationEngine:
    """Create actionable setup advice from measured session metrics."""

    def recommend(self, metrics: dict[str, float]) -> list[Recommendation]:
        recommendations: list[Recommendation] = []
        if metrics.get("best_lap_time_s", 0) <= 0:
            raise ValueError("best_lap_time_s must be provided and positive")

        if metrics.get("max_engine_temp_c", 0) >= 105:
            recommendations.append(Recommendation(
                "engine", "HIGH", "Inspect cooling and reduce sustained high-load operation.",
                f"Peak engine temperature: {metrics['max_engine_temp_c']:.1f} C",
            ))
        if metrics.get("max_lateral_g", 0) < 0.75:
            recommendations.append(Recommendation(
                "tyres", "MEDIUM", "Review tyre pressure and corner entry speed to improve grip usage.",
                f"Peak lateral acceleration: {metrics.get('max_lateral_g', 0):.2f} g",
            ))
        if metrics.get("lap_consistency_pct", 100) < 95:
            recommendations.append(Recommendation(
                "driver", "MEDIUM", "Prioritise repeatable braking and throttle application.",
                f"Lap consistency: {metrics['lap_consistency_pct']:.1f}%",
            ))
        if metrics.get("anomaly_count", 0) > 0:
            recommendations.append(Recommendation(
                "reliability", "HIGH", "Review flagged telemetry intervals before changing setup.",
                f"Detected anomalies: {int(metrics['anomaly_count'])}",
            ))
        if not recommendations:
            recommendations.append(Recommendation(
                "setup", "LOW", "Baseline setup is stable; focus on incremental driver gains.",
                "No configured threshold exceeded",
            ))
        return recommendations


class ReportExporter:
    """Write deterministic CSV telemetry exports and lightweight PDF dossiers."""

    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        report_id: str,
        telemetry: list[dict[str, Any]],
        summary: dict[str, Any],
        report_type: str = "SESSION_DEBRIEF",
    ) -> dict[str, str]:
        safe_id = self._safe_id(report_id)
        csv_path = self.output_dir / f"{safe_id}.csv"
        pdf_path = self.output_dir / f"{safe_id}.pdf"
        self._write_csv(csv_path, telemetry)
        self._write_pdf(pdf_path, safe_id, report_type, summary)
        return {"report_id": safe_id, "csv_path": str(csv_path), "pdf_path": str(pdf_path)}

    @staticmethod
    def _safe_id(value: str) -> str:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", value).strip("._")
        if not safe:
            raise ValueError("report_id must contain at least one safe character")
        return safe[:120]

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        fieldnames = sorted({key for row in rows for key in row}) or ["timestamp_us"]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _write_pdf(path: Path, report_id: str, report_type: str, summary: dict[str, Any]) -> None:
        lines = [report_type, f"Report: {report_id}"]
        lines.extend(f"{key}: {value}" for key, value in sorted(summary.items()))
        text = "\n".join(lines).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content = f"BT /F1 10 Tf 50 780 Td ({text.replace(chr(10), ') Tj 0 -16 Td (' )}) Tj ET"
        objects = [
            "<< /Type /Catalog /Pages 2 0 R >>",
            "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            f"<< /Length {len(content.encode('latin-1'))} >>\nstream\n{content}\nendstream",
        ]
        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for index, obj in enumerate(objects, 1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n{obj}\nendobj\n".encode("latin-1"))
        xref = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
        pdf.extend("".join(f"{offset:010d} 00000 n \n" for offset in offsets[1:]).encode("ascii"))
        pdf.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
        path.write_bytes(pdf)


class SessionReplay:
    """Normalize telemetry timestamps into a synchronized replay timeline."""

    def prepare(self, records: Iterable[dict[str, Any]], speed: float = 1.0) -> list[dict[str, Any]]:
        if speed <= 0:
            raise ValueError("speed must be positive")
        frames = sorted(records, key=lambda row: int(row["timestamp_us"]))
        if not frames:
            return []
        start = int(frames[0]["timestamp_us"])
        return [
            {
                "sequence": index,
                "elapsed_s": round((int(row["timestamp_us"]) - start) / 1_000_000 / speed, 6),
                "progress": round(index / max(len(frames) - 1, 1), 6),
                "telemetry": row,
            }
            for index, row in enumerate(frames)
        ]
