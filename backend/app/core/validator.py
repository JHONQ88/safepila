import io
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pdfplumber
import pikepdf
from pikepdf import Pdf

from app.schemas import Flag, Severity, ValidationDetails, SemaphoreStatus, ValidationResult
from app.core.config import Settings, get_settings


class PDFValidator:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    async def validate(self, filename: str, file_content: bytes) -> ValidationResult:
        flags: List[Flag] = []
        details = ValidationDetails()

        try:
            with io.BytesIO(file_content) as pdf_stream:
                pk_pdf = Pdf.open(pdf_stream)
                details = self._extract_details(pk_pdf, file_content)

        except pikepdf.PdfError as e:
            flags.append(Flag(
                layer="metadata",
                finding=f"PDF corrupto o inválido: {e}",
                severity=Severity.HIGH,
                weight=100,
            ))
            return self._build_result(filename, flags, details)

        except Exception as e:
            flags.append(Flag(
                layer="metadata",
                finding=f"Error al abrir PDF: {e}",
                severity=Severity.HIGH,
                weight=100,
            ))
            return self._build_result(filename, flags, details)

        flags.extend(self._check_metadata(details))
        flags.extend(self._check_dates(details))
        flags.extend(self._check_structure(pk_pdf, details))
        flags.extend(self._check_ai_indicators(details, pk_pdf))

        return self._build_result(filename, flags, details)

    def _extract_details(self, pk_pdf: Pdf, file_content: bytes) -> ValidationDetails:
        details = ValidationDetails()

        info = pk_pdf.docinfo or {}
        details.producer = str(info.get("/Producer", "")) or None
        details.creator = str(info.get("/Creator", "")) or None
        details.creation_date = str(info.get("/CreationDate", "")) or None
        details.mod_date = str(info.get("/ModDate", "")) or None

        try:
            with io.BytesIO(file_content) as stream:
                with pdfplumber.open(stream) as plumb_pdf:
                    details.pages = len(plumb_pdf.pages)

                    fonts_set: set[str] = set()
                    images_total = 0
                    images_no_meta = 0

                    for page in plumb_pdf.pages:
                        for char in (page.chars or []):
                            fn = char.get("fontname", "")
                            if fn:
                                fonts_set.add(fn)

                        page_images = page.images or []
                        images_total += len(page_images)

                        for img in page_images:
                            has_meta = bool(img.get("metadata"))
                            if not has_meta:
                                images_no_meta += 1

                    details.fonts = sorted(list(fonts_set))
                    details.images_count = images_total
                    details.images_without_metadata = images_no_meta

        except Exception:
            pass

        return details

    def _check_metadata(self, details: ValidationDetails) -> List[Flag]:
        flags: List[Flag] = []
        producer = (details.producer or "").lower().strip()
        creator = (details.creator or "").lower().strip()

        if not producer:
            flags.append(Flag(
                layer="metadata",
                finding="Sin campo /Producer en metadatos (indica generación programática)",
                severity=Severity.MEDIUM,
                weight=30,
            ))
            return flags

        for bad in self.settings.BLACKLISTED_PRODUCERS:
            if bad in producer:
                flags.append(Flag(
                    layer="metadata",
                    finding=f"Editor de PDF conocido: {details.producer}",
                    severity=Severity.HIGH,
                    weight=50,
                ))
                break

        for pattern in self.settings.SUSPICIOUS_CREATOR_PATTERNS:
            if pattern in producer or pattern in creator:
                flags.append(Flag(
                    layer="metadata",
                    finding=f"Creado con software de oficina: {details.creator or details.producer}",
                    severity=Severity.LOW,
                    weight=10,
                ))
                break

        return flags

    def _check_dates(self, details: ValidationDetails) -> List[Flag]:
        flags: List[Flag] = []
        creation = details.creation_date
        modification = details.mod_date

        if not creation or not modification:
            if not modification and creation:
                pass
            elif not creation:
                flags.append(Flag(
                    layer="dates",
                    finding="Sin fecha de creación (/CreationDate)",
                    severity=Severity.MEDIUM,
                    weight=25,
                ))
            return flags

        try:
            cd = self._parse_pdf_date(creation)
            md = self._parse_pdf_date(modification)

            if cd and md:
                tolerance = timedelta(minutes=self.settings.DATE_TOLERANCE_MINUTES)
                if md > cd + tolerance:
                    diff = md - cd
                    flags.append(Flag(
                        layer="dates",
                        finding=(
                            f"Fecha de modificación posterior a creación. "
                            f"Diferencia: {diff.days}d {diff.seconds // 3600}h"
                        ),
                        severity=Severity.HIGH,
                        weight=25,
                    ))
                elif md < cd:
                    flags.append(Flag(
                        layer="dates",
                        finding="Fecha de modificación anterior a creación",
                        severity=Severity.MEDIUM,
                        weight=25,
                    ))
        except Exception:
            flags.append(Flag(
                layer="dates",
                finding="No se pudieron parsear las fechas del PDF",
                severity=Severity.LOW,
                weight=5,
            ))

        return flags

    def _check_structure(self, pk_pdf: Pdf, details: ValidationDetails) -> List[Flag]:
        flags: List[Flag] = []
        suspicious: List[str] = []

        try:
            objects = list(pk_pdf.objects)
            total_objects = len(objects)

            if total_objects > 1000:
                suspicious.append(f"Cantidad inusual de objetos: {total_objects}")

            for obj in objects:
                try:
                    if isinstance(obj, pikepdf.Stream):
                        if hasattr(obj, "Name") and obj.Name:
                            name = str(obj.Name)
                            if name in ("/PieceInfo", "/OCProperties", "/AA", "/MarkInfo"):
                                suspicious.append(f"Objeto sospechoso: {name}")
                except Exception:
                    continue

            page_count = len(pk_pdf.pages)
            for i, page in enumerate(pk_pdf.pages):
                try:
                    xobjects = page.get("/XObject")
                    if xobjects and hasattr(xobjects, "keys"):
                        for xobj_key in xobjects.keys():
                            xobj = xobjects[xobj_key]
                            if hasattr(xobj, "objgen"):
                                obj_type = ""
                                try:
                                    subtype = xobj.get("/Subtype", "")
                                    obj_type = str(subtype)
                                except Exception:
                                    pass
                                if "/Form" in obj_type:
                                    suspicious.append(
                                        f"Página {i+1}: Form XObject superpuesto ({xobj_key})"
                                    )

                    annotations = page.get("/Annots")
                    if annotations and hasattr(annotations, "__len__"):
                        annot_count = len(annotations)
                        if annot_count > 10:
                            suspicious.append(
                                f"Página {i+1}: {annot_count} anotaciones (posibles campos superpuestos)"
                            )

                except Exception:
                    continue

            try:
                trailer = pk_pdf.trailer
                if trailer and "/Prev" in trailer:
                    details.has_incremental_updates = True
                    details.incremental_update_count += 1
                    suspicious.append(
                        f"Actualizaciones incrementales detectadas: {details.incremental_update_count}"
                    )
            except Exception:
                pass

            if page_count > 0:
                first_page = pk_pdf.pages[0]
                try:
                    media_box = first_page.get("/MediaBox")
                    if media_box:
                        width = float(media_box[2]) - float(media_box[0])
                        height = float(media_box[3]) - float(media_box[1])
                        aspect_ratio = height / width if width > 0 else 0

                        if aspect_ratio > 2.0 or aspect_ratio < 0.3:
                            suspicious.append(
                                f"Dimensiones inusuales: {width:.0f}x{height:.0f} (ratio: {aspect_ratio:.2f})"
                            )
                except Exception:
                    pass

        except Exception:
            pass

        details.suspicious_objects = suspicious

        if suspicious:
            has_critical = any(
                kw in s for s in suspicious
                for kw in ["/PieceInfo", "/OCProperties", "Form XObject", "actualizaciones incrementales"]
            )

            if has_critical:
                flags.append(Flag(
                    layer="structure",
                    finding=f"Estructura alterada: {'; '.join(suspicious[:3])}",
                    severity=Severity.HIGH,
                    weight=35,
                ))
            else:
                flags.append(Flag(
                    layer="structure",
                    finding=f"Anomalías estructurales: {'; '.join(suspicious[:3])}",
                    severity=Severity.MEDIUM,
                    weight=20,
                ))

        return flags

    def _check_ai_indicators(self, details: ValidationDetails, pk_pdf: Pdf) -> List[Flag]:
        flags: List[Flag] = []
        producer = (details.producer or "").lower()
        creator = (details.creator or "").lower()

        for ai_name in self.settings.AI_PRODUCERS:
            if ai_name in producer or ai_name in creator:
                flags.append(Flag(
                    layer="ai",
                    finding=f"Herramienta IA detectada en metadatos: {details.producer or details.creator}",
                    severity=Severity.HIGH,
                    weight=35,
                ))
                break

        synthetic_fonts_found: List[str] = []
        for font in details.fonts:
            font_lower = font.lower()
            for synth in self.settings.SYNTHETIC_FONTS:
                if synth in font_lower:
                    synthetic_fonts_found.append(font)
                    break

        if synthetic_fonts_found and len(synthetic_fonts_found) >= 2:
            flags.append(Flag(
                layer="ai",
                finding=f"Fuentes típicas de generación automática: {', '.join(synthetic_fonts_found[:3])}",
                severity=Severity.MEDIUM,
                weight=8,
            ))

        if (
            details.images_count > 0
            and details.images_without_metadata == details.images_count
            and details.images_count >= 2
        ):
            flags.append(Flag(
                layer="ai",
                finding=f"{details.images_count} imágenes sin metadatos EXIF/origen",
                severity=Severity.LOW,
                weight=5,
            ))

        return flags

    def _build_result(
        self, filename: str, flags: List[Flag], details: ValidationDetails
    ) -> ValidationResult:
        score = self._calculate_score(flags)
        semaphore = self._score_to_semaphore(score)
        status = semaphore_to_status(semaphore)
        verdict = self._build_verdict(flags, status)

        return ValidationResult(
            filename=filename,
            status=status,
            semaphore=semaphore,
            score=score,
            verdict=verdict,
            flags=flags,
            details=details,
        )

    def _calculate_score(self, flags: List[Flag]) -> int:
        if not flags:
            return 0

        has_critical = any(f.weight >= 100 for f in flags)
        if has_critical:
            return 100

        high_flags = [f for f in flags if f.severity == Severity.HIGH]
        if len(high_flags) >= 2:
            return 90

        if len(high_flags) == 1:
            total = 0.0
            for flag in flags:
                severity_mult = {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3}
                mult = severity_mult.get(flag.severity, 0.5)
                total += flag.weight * mult

            if total >= 50:
                return min(round(total), 85)
            return min(round(total), 65)

        total = 0.0
        for flag in flags:
            severity_mult = {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3}
            mult = severity_mult.get(flag.severity, 0.5)
            total += flag.weight * mult

        return min(round(total), 50)

    def _score_to_semaphore(self, score: int) -> SemaphoreStatus:
        if score <= self.settings.SCORE_GREEN_MAX:
            return SemaphoreStatus.GREEN
        elif score <= self.settings.SCORE_YELLOW_MAX:
            return SemaphoreStatus.YELLOW
        else:
            return SemaphoreStatus.RED

    def _build_verdict(self, flags: List[Flag], status: str) -> str:
        if status == "APPROVED":
            return "Documento válido. No se detectaron alteraciones ni ediciones externas."

        reasons = []
        for f in flags:
            if f.severity in (Severity.HIGH, Severity.MEDIUM):
                reasons.append(f.finding)

        if not reasons:
            return "Documento con indicaciones menores que requieren revisión."

        unique_reasons = list(dict.fromkeys(reasons))[:3]
        verdict_text = "Documento con posibles alteraciones. "
        verdict_text += " | ".join(unique_reasons)

        if status == "REJECTED":
            verdict_text = "DOCUMENTO ALTERADO. " + verdict_text

        return verdict_text

    def _parse_pdf_date(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None

        clean = str(date_str).strip().strip("D:() ")
        formats = [
            "%Y%m%d%H%M%S",
            "%Y%m%d%H%M",
            "%Y%m%d%H%M%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(clean[:len(fmt.replace("%", "x"))], fmt)
            except (ValueError, IndexError):
                continue

        try:
            if len(clean) >= 14:
                year = int(clean[0:4])
                month = int(clean[4:6])
                day = int(clean[6:8])
                hour = int(clean[8:10])
                minute = int(clean[10:12])
                second = int(clean[12:14])
                return datetime(year, month, day, hour, minute, second)
        except (ValueError, IndexError):
            pass

        return None


def semaphore_to_status(semaphore: SemaphoreStatus) -> str:
    mapping = {
        SemaphoreStatus.GREEN: "APPROVED",
        SemaphoreStatus.YELLOW: "SUSPICIOUS",
        SemaphoreStatus.RED: "REJECTED",
    }
    return mapping[semaphore]