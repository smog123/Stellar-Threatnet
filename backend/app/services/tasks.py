"""Celery background workers.

Run with:  celery -A app.services.tasks worker --loglevel=info --beat
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "stellar_threatnet",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "recalculate-scores-hourly": {
            "task": "app.services.tasks.recalculate_all_scores",
            "schedule": 3600.0,
        },
        "poll-horizon-hourly": {
            "task": "app.services.tasks.poll_stellar_horizon",
            "schedule": 3600.0,
        },
    },
)


@celery_app.task(name="app.services.tasks.recalculate_all_scores")
def recalculate_all_scores() -> str:
    """Recalculate reputation scores for all entities from their evidence.

    Production implementation iterates Wallet/Domain/Token rows and calls
    ThreatService.apply_score() for each. Kept as a scheduling hook here so
    operators can plug in their own DB session wiring.
    """
    return "recalculate_all_scores: 0 entities updated (hook)"


@celery_app.task(name="app.services.tasks.process_report_consensus")
def process_report_consensus(report_id: str) -> str:
    """Evaluate multi-source consensus for a community report.

    When a target accumulates N independent reports, promote confidence to
    Level 2 (multi-source correlation) and auto-flag the entity as suspicious.
    """
    return f"process_report_consensus: report {report_id} queued (hook)"


@celery_app.task(name="app.services.tasks.poll_stellar_horizon")
def poll_stellar_horizon() -> str:
    """Periodic Horizon polling to detect suspicious multi-account creation.

    Placeholder for network monitoring jobs (e.g. rapid claimable-balance
    creation loops, clawback abuse). Extend with your Horizon integration.
    """
    return "poll_stellar_horizon: 0 anomalies (hook)"
