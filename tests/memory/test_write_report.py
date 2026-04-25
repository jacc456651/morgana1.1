from pathlib import Path
from memory.write_report import write_report_md


def test_write_report_creates_file(tmp_path):
    report_path = write_report_md(
        ticker="AAPL",
        reporte="## AAPL\n**SCORE FINAL: 87/100**\n**DECISION: BUY**",
        decision="BUY",
        score=87.0,
        output_dir=str(tmp_path)
    )
    assert Path(report_path).exists()


def test_write_report_path_includes_ticker(tmp_path):
    report_path = write_report_md(
        ticker="MNDY",
        reporte="## MNDY\n**SCORE FINAL: 75/100**\n**DECISION: HOLD**",
        decision="HOLD",
        score=75.0,
        output_dir=str(tmp_path)
    )
    assert "MNDY" in report_path


def test_write_report_file_has_content(tmp_path):
    write_report_md(
        ticker="AAPL",
        reporte="## AAPL\n**SCORE FINAL: 87/100**\n**DECISION: BUY**",
        decision="BUY",
        score=87.0,
        output_dir=str(tmp_path)
    )
    files = list(Path(tmp_path).glob("AAPL/**/*.md"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "AAPL" in content
    assert "BUY" in content
