"""
utils/report.py
Genera el reporte estadístico de clasificación y lo guarda en results/.
"""
import os
from datetime import datetime


def generate_report(db, output_dir: str = "results", threshold: float = 0.40):
    """
    Genera un reporte de texto con:
      - Distribución de observaciones por categoría
      - Confianza promedio por categoría
      - Listado de registros con baja confianza (requieren revisión)
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"reporte_{timestamp}.txt")

    stats        = db.get_stats()
    low_conf     = db.get_low_confidence(threshold)
    all_records  = db.get_all_classified()
    total        = len(all_records)

    lines = []
    lines.append("=" * 60)
    lines.append("  REPORTE DE CLASIFICACIÓN CATASTRAL")
    lines.append(f"  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lines.append("=" * 60)
    lines.append(f"\nTotal de observaciones clasificadas: {total}\n")

    # ── Distribución por categoría ──────────────────────────────────
    lines.append("DISTRIBUCIÓN POR CATEGORÍA")
    lines.append("-" * 60)
    lines.append(f"  {'Categoría':<42} {'N':>4}  {'%':>6}  {'Conf.Prom':>9}")
    lines.append(f"  {'-'*42} {'-'*4}  {'-'*6}  {'-'*9}")

    for categoria, count, conf_prom in stats:
        pct = count / total * 100 if total else 0
        conf_str = f"{conf_prom:.3f}" if conf_prom is not None else "  N/A"
        lines.append(f"  {categoria:<42} {count:>4}  {pct:>5.1f}%  {conf_str:>9}")

    # ── Registros de baja confianza ─────────────────────────────────
    lines.append(f"\nREGISTROS CON BAJA CONFIANZA (< {threshold:.0%}) — REVISIÓN MANUAL")
    lines.append("-" * 60)

    if low_conf:
        for id_p, obs, cat, conf in low_conf:
            lines.append(f"\n  ID       : {id_p}")
            lines.append(f"  Observ.  : {obs}")
            lines.append(f"  Categoría: {cat}")
            lines.append(f"  Confianza: {conf:.3f}")
    else:
        lines.append("  Ninguno. Todos los registros superan el umbral de confianza.")

    lines.append("\n" + "=" * 60)

    report_text = "\n".join(lines)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(report_text)
    print(f"\nReporte guardado en: {report_path}")
    return report_path
