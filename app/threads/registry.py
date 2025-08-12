import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List 
from app.db.mongo import get_db


COLL = "threads"

def _title_from_text(text: str, n: int = 20) -> str:
    t = (text or "").strip().replace("\n", " ")
    return t[:n] + ("…" if len(t) > n else "")

def create_thread(title: str = "New chat") -> Dict[str, Any]:
    db = get_db()
    now = datetime.now(timezone.utc)
    tid = str(uuid.uuid4())  # canonical server ID

    doc = {
        "thread_id": tid,
        "title": title,
        "created_at": now,
        "updated_at": now,
        "last_user_message": "",
        "message_count": 0,
    }
    db[COLL].insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}  # no ObjectId leakage


def upsert_thread(thread_id: str, first_user_text: str) -> Dict[str, Any]:
    db = get_db()
    now = datetime.now(timezone.utc)
    existing = db[COLL].find_one({"thread_id": thread_id})
    if existing:
        return existing
    doc = {
        "thread_id": thread_id,
        "title": _title_from_text(first_user_text),
        "created_at": now,
        "updated_at": now,
        "last_user_message": first_user_text,
        "message_count": 1,
    }
    db[COLL].insert_one(doc)
    return doc

def touch_thread(thread_id: str, user_text: str):
    """Create thread if missing; otherwise bump updated_at, last_user_message, count."""
    db = get_db()
    now = datetime.now(timezone.utc)
    res = db[COLL].update_one(
        {"thread_id": thread_id},
        {
            "$setOnInsert": {
                "title": _title_from_text(user_text),
                "created_at": now,
            },
            "$set": {
                "updated_at": now,
                "last_user_message": user_text,
            },
            "$inc": {"message_count": 1},
        },
        upsert=True,
    )
    return res
# def upsert_thread(thread_id: str, first_user_text: str) -> Dict[str, Any]:
#     """
#     Create the thread doc if it doesn't exist.
#     Never updates title or message_count after creation.
#     """
#     db = get_db()
#     now = datetime.now(timezone.utc)
    
#     # Only insert if it doesn't already exist
#     existing = db[COLL].find_one({"thread_id": thread_id})
#     if existing:
#         return existing  # Return existing doc, no update
    
#     doc = {
#         "thread_id": thread_id,
#         "title": _title_from_text(first_user_text),
#         "created_at": now,
#         "updated_at": now,
#         "last_user_message": first_user_text,
#         "message_count": 1,
#     }
#     db[COLL].insert_one(doc)
#     return doc

# def touch_thread(thread_id: str, user_text: str):
#     """Create thread if missing; otherwise bump updated_at, last_user_message, count."""
#     db = get_db()
#     now = datetime.now(timezone.utc)
#     res = db[COLL].update_one(
#         {"thread_id": thread_id},
#         {
#             "$setOnInsert": {
#                 "title": _title_from_text(user_text),
#                 "created_at": now,
#             },
#             "$set": {
#                 "updated_at": now,
#                 "last_user_message": user_text,
#             },
#             "$inc": {"message_count": 1},
#         },
#         upsert=True,
#     )
#     return res

def list_threads() -> List[Dict[str, Any]]:
    db = get_db()
    return list(db[COLL].find({}, {"_id": 0}).sort("updated_at", -1))

def get_thread(thread_id: str) -> Optional[Dict[str, Any]]:
    db = get_db()
    return db[COLL].find_one({"thread_id": thread_id}, {"_id": 0})

def delete_all_threads() -> int:
    """
    Delete all threads from the database.
    Returns the number of deleted documents.
    """
    db = get_db()
    result = db[COLL].delete_many({})
    return result.deleted_count

def delete_thread_by_id(thread_id: str):
    """
    Delete a specific thread by its ID.
    Returns True if a thread was deleted, False if no thread was found.
    """
    db = get_db()
    result = db[COLL].delete_one({"thread_id": thread_id})

    total = 0
    tid = str(thread_id)

    # Common collection names used by LangGraph's MongoDBSaver
    # NOTE: Depending on your LangGraph version, schemas can vary.
    # We match by the config key used in your graph: config.configurable.thread_id
    q = {"config.configurable.thread_id": tid}

    for coll in ("checkpoints", "checkpoint_blobs"):
        if coll in db.list_collection_names():
            total += db[coll].delete_many(q).deleted_count

    # (Optional) clean up any stray shapes if your version stores keys differently
    # Try alternative keys that sometimes appear:
    alt_qs = [
        {"config.thread_id": tid},
        {"thread_id": tid},
        {"keys.thread_id": tid},
    ]
    for alt_q in alt_qs:
        for coll in ("checkpoints", "checkpoint_blobs"):
            if coll in db.list_collection_names():
                total += db[coll].delete_many(alt_q).deleted_count

    return [result.deleted_count > 0, total]
