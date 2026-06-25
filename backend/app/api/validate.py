from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from app.core.validator import PDFValidator
from app.core.report import generate_report_pdf
from app.core.config import get_settings
from app.schemas import ValidationResult, ErrorResponse

router = APIRouter(prefix="/api", tags=["validate"])


class ValidateResponse(BaseModel):
    result: ValidationResult
    report_available: bool = True


@router.post(
    "/validate",
    response_model=ValidateResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Validar un archivo PDF",
    description="Recibe un archivo PDF y valida si ha sido alterado, editado o generado por IA.",
)
async def validate_pdf(file: UploadFile = File(...)) -> ValidateResponse:
    settings = get_settings()

    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}. Solo se aceptan archivos PDF.",
        )

    content = await file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"El archivo excede el tamaño máximo permitido de {max_mb}MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío.",
        )

    validator = PDFValidator(settings)
    result = await validator.validate(file.filename or "unknown.pdf", content)

    return ValidateResponse(result=result, report_available=True)


@router.post(
    "/validate/report",
    response_class=Response,
    responses={
        200: {"content_type": "application/pdf"},
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
    },
    summary="Validar PDF y generar reporte",
    description="Valida un PDF y retorna un reporte descargable en formato PDF.",
)
async def validate_and_get_report(file: UploadFile = File(...)) -> Response:
    settings = get_settings()

    if file.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}. Solo se aceptan archivos PDF.",
        )

    content = await file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"El archivo excede el tamaño máximo permitido de {max_mb}MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío.",
        )

    validator = PDFValidator(settings)
    result = await validator.validate(file.filename or "unknown.pdf", content)

    pdf_bytes = generate_report_pdf(result)

    filename = file.filename or "reporte.pdf"
    report_name = f"reporte_{filename.replace('.pdf', '')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{report_name}"',
        },
    )