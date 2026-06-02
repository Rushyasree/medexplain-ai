from __future__ import annotations

from sqlalchemy import func

from modules.database import AuditLog, Diagnosis, Feedback, Report, User, log_audit, session_scope


def dashboard_metrics() -> dict:
    with session_scope() as session:
        return {
            "reports": session.query(Report).count(),
            "diagnoses": session.query(Diagnosis).count(),
            "critical": session.query(Report).filter(Report.risk_level == "critical").count(),
            "users": session.query(User).count(),
            "feedback": session.query(Feedback).count(),
        }


def save_analysis(user_id, source_type, filename, text, risk, predictions, summary) -> int:
    with session_scope() as session:
        report = Report(
            user_id=user_id,
            source_type=source_type,
            original_filename=filename,
            extracted_text=text,
            summary=summary,
            risk_level=risk,
        )
        session.add(report)
        session.flush()
        for item in predictions:
            session.add(
                Diagnosis(
                    report_id=report.id,
                    label=item["label"],
                    confidence=item["confidence"],
                    explanation=item["explanation"],
                    evidence={"matched_terms": item["evidence"]},
                )
            )
        report_id = report.id
    log_audit("report_analyzed", user_id, {"report_id": report_id, "risk": risk})
    return report_id


def list_user_reports(user_id: int, limit: int = 25) -> list[dict]:
    with session_scope() as session:
        reports = (
            session.query(Report)
            .filter(Report.user_id == user_id)
            .order_by(Report.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "ID": report.id,
                "Date": report.created_at,
                "Source": report.source_type,
                "Risk": report.risk_level,
                "Summary": (report.summary or "")[:180],
            }
            for report in reports
        ]


def latest_report_for_user(user_id: int) -> dict | None:
    with session_scope() as session:
        report = (
            session.query(Report)
            .filter(Report.user_id == user_id)
            .order_by(Report.created_at.desc())
            .first()
        )
        if not report:
            return None
        diagnoses = [
            {
                "label": diagnosis.label,
                "confidence": diagnosis.confidence,
                "evidence": diagnosis.evidence,
            }
            for diagnosis in report.diagnoses
        ]
        return {
            "id": report.id,
            "text": report.extracted_text,
            "summary": report.summary,
            "risk": report.risk_level,
            "diagnoses": diagnoses,
            "created_at": report.created_at,
        }


def save_feedback(user_id: int, report_id: int, rating: int, comments: str) -> None:
    with session_scope() as session:
        session.add(
            Feedback(
                report_id=report_id,
                user_id=user_id,
                rating=rating,
                comments=comments,
            )
        )
    log_audit("feedback_saved", user_id, {"report_id": report_id, "rating": rating})


def risk_distribution() -> list[dict]:
    with session_scope() as session:
        rows = (
            session.query(Report.risk_level, func.count(Report.id))
            .group_by(Report.risk_level)
            .all()
        )
        return [{"Risk": risk or "unknown", "Count": count} for risk, count in rows]


def feedback_summary() -> dict:
    with session_scope() as session:
        count = session.query(Feedback).count()
        average = session.query(func.avg(Feedback.rating)).scalar()
        return {
            "count": count,
            "average_rating": round(float(average), 2) if average else 0,
        }


def latest_audit_logs(limit: int = 30) -> list[dict]:
    with session_scope() as session:
        logs = session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
        return [
            {
                "ID": log.id,
                "Time": log.created_at,
                "User ID": log.user_id,
                "Action": log.action,
                "Details": log.details,
            }
            for log in logs
        ]


def admin_report_rows(limit: int = 50) -> list[dict]:
    with session_scope() as session:
        reports = session.query(Report).order_by(Report.created_at.desc()).limit(limit).all()
        return [
            {
                "ID": report.id,
                "User ID": report.user_id,
                "Date": report.created_at,
                "Source": report.source_type,
                "Risk": report.risk_level,
                "Filename": report.original_filename,
            }
            for report in reports
        ]
