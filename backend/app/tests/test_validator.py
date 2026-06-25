import pytest
import io
from app.core.validator import PDFValidator
from app.core.config import Settings
from app.schemas import SemaphoreStatus


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def validator(settings):
    return PDFValidator(settings)


def create_minimal_pdf(producer: str = "TestProducer", creator: str = "TestCreator") -> bytes:
    pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj

xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 

trailer
<< /Size 4 /Root 1 0 R /Info 4 0 R >>

4 0 obj
<< /Producer ({producer}) /Creator ({creator}) >>
endobj

startxref
190
%%EOF"""
    return pdf_content.encode('latin-1')


@pytest.mark.asyncio
async def test_validate_returns_valid_result(validator):
    pdf = create_minimal_pdf()
    result = await validator.validate("test.pdf", pdf)

    assert result.filename == "test.pdf"
    assert result.status in ("APPROVED", "SUSPICIOUS", "REJECTED")
    assert 0 <= result.score <= 100
    assert result.verdict
    assert result.details


@pytest.mark.asyncio
async def test_validate_clean_pdf_is_approved(validator):
    pdf = create_minimal_pdf()
    result = await validator.validate("clean.pdf", pdf)

    assert result.status == "APPROVED"
    assert result.semaphore == SemaphoreStatus.GREEN
    assert result.score <= 25


@pytest.mark.asyncio
async def test_validate_ilovepdf_is_detected(validator):
    pdf = create_minimal_pdf(producer="iLovePDF")
    result = await validator.validate("ilovepdf.pdf", pdf)

    assert result.status in ("SUSPICIOUS", "REJECTED")
    assert any("iLovePDF" in f.finding for f in result.flags)
    assert any(f.layer == "metadata" for f in result.flags)


@pytest.mark.asyncio
async def test_validate_ai_producer_detected(validator):
    pdf = create_minimal_pdf(producer="ChatGPT")
    result = await validator.validate("ai.pdf", pdf)

    assert any(f.layer == "ai" for f in result.flags)
    assert any("ChatGPT" in f.finding for f in result.flags)


@pytest.mark.asyncio
async def test_validate_corrupt_pdf(validator):
    corrupt = b"this is not a pdf"
    result = await validator.validate("corrupt.pdf", corrupt)

    assert result.status == "REJECTED"
    assert result.semaphore == SemaphoreStatus.RED
    assert result.score == 100


@pytest.mark.asyncio
async def test_validate_empty_pdf(validator):
    result = await validator.validate("empty.pdf", b"")

    assert result.status == "REJECTED"
    assert result.semaphore == SemaphoreStatus.RED
    assert result.score == 100