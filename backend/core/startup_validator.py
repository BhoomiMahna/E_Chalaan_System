import logging
from core.config import Config

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate that all required environment variables are set."""
    # List of critical config variables
    critical_vars = [
        'SECRET_KEY',
    ]

    missing_vars = []
    for var in critical_vars:
        if not getattr(Config, var, None):
            missing_vars.append(var)

    if missing_vars:
        error_msg = f"Missing critical environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("Environment validation successful.")
