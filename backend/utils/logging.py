import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger("research_agent_v2")
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
        )
    return logger


def log_stage(job_id: str, stage: str, event: str) -> None:
    logger = get_logger()
    logger.info("[%s] %s %s", job_id, stage, event)
