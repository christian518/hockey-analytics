import os, subprocess, logging
from app.workers.celery_app import celery_app
from app.config import get_settings
from app.core.storage import upload_file_sync

logger = logging.getLogger(__name__)
settings = get_settings()

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def generate_clip(self, game_id, event_id, event_type, video_source, timestamp_seconds, pre_seconds=5, post_seconds=8):
    try:
        start = max(0, timestamp_seconds - pre_seconds)
        duration = pre_seconds + post_seconds
        os.makedirs(settings.VIDEO_STORAGE_PATH, exist_ok=True)
        clip_path = os.path.join(settings.VIDEO_STORAGE_PATH, f"clip_{event_id}.mp4")
        cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", video_source, "-t", str(duration), "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-movflags", "+faststart", clip_path]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode != 0:
            raise Exception(f"FFmpeg failed: {r.stderr.decode()}")
        clip_url = upload_file_sync(clip_path, f"games/{game_id}/clips/clip_{event_id}.mp4", "video/mp4")
        _update_db(event_id, game_id, clip_url, None, f"games/{game_id}/clips/clip_{event_id}.mp4")
        if os.path.exists(clip_path):
            os.remove(clip_path)
        return {"clip_url": clip_url}
    except Exception as exc:
        logger.error(f"Clip failed: {exc}")
        self.retry(exc=exc)

@celery_app.task(bind=True, max_retries=2)
def generate_compilation(self, game_id):
    logger.info(f"Compilation for game {game_id}")
    return {"status": "ok"}

def _update_db(event_id, game_id, clip_url, thumb_url, s3_key):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.event import Event
    from app.models.clip import Clip, ClipType
    from uuid import uuid4
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
    db = sessionmaker(bind=create_engine(sync_url))()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            event.clip_url = clip_url
            if not db.query(Clip).filter(Clip.event_id == event_id).first():
                db.add(Clip(id=uuid4(), game_id=game_id, event_id=event_id, clip_type=ClipType.EVENT, title=f"{event.event_type.value.title()}", s3_key=s3_key, clip_url=clip_url, rank_score=event.confidence, is_free=False))
        db.commit()
    except Exception as e:
        logger.error(f"DB update failed: {e}")
        db.rollback()
    finally:
        db.close()