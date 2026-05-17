import asyncio
import logging
from app.utils.database import db
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

async def ensure_default_user():
    """Ensure the single TILLU user exists in user_profile table."""
    user_id = settings.single_user_id
    logger.info(f"Checking for default user: {user_id}")
    
    # Check if user exists
    user = await db.fetch_one("user_profile", {"user_id": user_id})
    
    if not user:
        logger.info(f"User {user_id} not found. Creating default profile...")
        profile = {
            "user_id": user_id,
            "name": "TILLU User",
            "timezone": "Asia/Kolkata",
            "personality_params": {
                "base": {
                    "temperature": 0.75,
                    "sarcasm": 0.70,
                    "warmth": 0.65,
                    "directness": 0.80,
                    "humor_frequency": 0.55,
                    "challenge_style": 0.70,
                    "detail_level": 0.60,
                    "proactivity_threshold": 6
                }
            }
        }
        try:
            inserted = await db.insert("user_profile", profile)
            if inserted:
                logger.info("Default user profile created successfully.")
            else:
                logger.error("Failed to create default user profile (insert returned None).")
        except Exception as e:
            logger.error(f"Error creating default user profile: {e}")
    else:
        logger.info("Default user profile already exists.")

if __name__ == "__main__":
    db.connect()
    asyncio.run(ensure_default_user())
