import io
from datetime import datetime
from fpdf import FPDF

from app.schemas import ValidationResult, SemaphoreStatus


class ReportColors:
    GREEN = (34, 197, 94)
    YELLOW = (234, 179, 8)
    RED = (239, 68, 68)
    GRAY = (148, 163, 184)
    DARK = (30, 41, 59)
    WHITE = (255, 255, 255)
    LIGHT_BG = (241, 245, 249)


class ValidationReport(FPDF):
    def __init__(self, result: ValidationResult):
        super().__init__()
        self.result = result
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*ReportColors.GRAY)
        self.cell(0, 8, "SafePILA - Validacion de Seguridad Social", align="L")
        self.cell(0, 8, datetime.now().strftime("%d/%m/%Y %H:%M"), align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ReportColors.GRAY)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*ReportColors.GRAY)
        self.cell(0, 10, f"Reporte generado por SafePILA v0.1.0 | {self.result.filename}", align="C")

    def build(self) -> bytes:
        self.add_page()
        self._draw_title()
        self._draw_semaphore()
        self._draw_verdict()
        self._draw_details()
        self._draw_flags()
        self._draw_disclaimer()

        output = io.BytesIO()
        self.output(output)
        return output.getvalue()

    def _draw_title(self):
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*ReportColors.DARK)
        self.cell(0, 15, "REPORTE DE VALIDACION", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

        self.set_font("Helvetica", "", 12)
        self.set_text_color(*ReportColors.GRAY)
        self.cell(0, 8, f"Archivo: {self.result.filename}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 8, f"Fecha: {datetime.now().strftime('%d de %B de %Y a las %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def _draw_semaphore(self):
        colors = {
            SemaphoreStatus.GREEN: ReportColors.GREEN,
            SemaphoreStatus.YELLOW: ReportColors.YELLOW,
            SemaphoreStatus.RED: ReportColors.RED,
        }
        labels = {
            SemaphoreStatus.GREEN: "APROBADO",
            SemaphoreStatus.YELLOW: "SOSPECHOSO",
            SemaphoreStatus.RED: "RECHAZADO",
        }

        color = colors[self.result.semaphore]
        label = labels[self.result.semaphore]

        self.set_fill_color(*color)
        self.rect(60, self.get_y(), 90, 35, style="F")

        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*ReportColors.WHITE)
        self.set_xy(60, self.get_y() + 5)
        self.cell(90, 12, label, align="C")

        self.set_font("Helvetica", "B", 28)
        self.set_xy(60, self.get_y() + 10)
        self.cell(90, 15, f"Score: {self.result.score}/100", align="C")

        self.set_xy(10, self.get_y() + 25)
        self.ln(15)

    def _draw_verdict(self):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*ReportColors.DARK)
        self.cell(0, 10, "VEREDICTO:", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 11)
        self.set_text_color(*ReportColors.DARK)
        self.multi_cell(0, 7, self.result.verdict)
        self.ln(5)

    def _draw_details(self):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*ReportColors.DARK)
        self.cell(0, 10, "DETALLES DEL DOCUMENTO:", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 10)
        details = self.result.details

        rows = [
            ("Producer", details.producer or "No disponible"),
            ("Creator", details.creator or "No disponible"),
            ("Fecha Creacion", details.creation_date or "No disponible"),
            ("Fecha Modificacion", details.mod_date or "No disponible"),
            ("Paginas", str(details.pages or "N/A")),
            ("Fuentes", str(len(details.fonts))),
            ("Incremental Updates", "Si" if details.has_incremental_updates else "No"),
        ]

        for label, value in rows:
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*ReportColors.GRAY)
            self.cell(55, 7, f"  {label}:", align="L")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*ReportColors.DARK)
            self.cell(0, 7, value, new_x="LMARGIN", new_y="NEXT")

        self.ln(5)

    def _draw_flags(self):
        if not self.result.flags:
            self.set_font("Helvetica", "I", 10)
            self.set_text_color(*ReportColors.GRAY)
            self.cell(0, 8, "No se encontraron hallazgos.", new_x="LMARGIN", new_y="NEXT")
            return

        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*ReportColors.DARK)
        self.cell(0, 10, f"HALLAZGOS ({len(self.result.flags)}):", new_x="LMARGIN", new_y="NEXT")

        severity_colors = {
            "HIGH": ReportColors.RED,
            "MEDIUM": ReportColors.YELLOW,
            "LOW": ReportColors.GRAY,
        }

        for i, flag in enumerate(self.result.flags, 1):
            color = severity_colors.get(flag.severity, ReportColors.GRAY)

            self.set_fill_color(*color)
            self.rect(10, self.get_y(), 3, 20, style="F")

            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*color)
            self.cell(15, 7, f"  #{i}", new_x="RIGHT")
            self.cell(30, 7, f"[{flag.severity}]")
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*ReportColors.GRAY)
            self.cell(0, 7, f"Capa: {flag.layer.upper()}", new_x="LMARGIN", new_y="NEXT")

            self.set_font("Helvetica", "", 10)
            self.set_text_color(*ReportColors.DARK)
            self.set_x(13)
            self.multi_cell(180, 6, flag.finding)
            self.ln(2)

        self.ln(3)

    def _draw_disclaimer(self):
        self.ln(10)
        self.set_draw_color(*ReportColors.GRAY)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*ReportColors.GRAY)
        disclaimer = (
            "AVISO: Este reporte es generado automaticamente por el sistema SafePILA. "
            "Los resultados son indicativos y no constituyen dictamen legal. "
            "Se recomienda revision humana para casos marcados como SOSPECHOSO o RECHAZADO."
        )
        self.multi_cell(0, 4, disclaimer)


def generate_report_pdf(result: ValidationResult) -> bytes:
    report = ValidationReport(result)
    return report.build()
