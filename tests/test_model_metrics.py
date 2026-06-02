from modules.model_metrics import load_evaluation_report


def test_load_evaluation_report_has_fallback():
    report = load_evaluation_report()

    assert "available" in report
