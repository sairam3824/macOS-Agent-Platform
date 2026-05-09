from fastapi import APIRouter, Query
from sqlalchemy import select, desc
from backend.database import AsyncSessionLocal, ActionLog, ConversationMessage
from typing import Optional

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/actions")
async def get_action_logs(limit: int = Query(50, le=500), offset: int = 0):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ActionLog).order_by(desc(ActionLog.timestamp)).offset(offset).limit(limit)
        )
        rows = result.scalars().all()
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "action_type": r.action_type,
                "description": r.description,
                "parameters": r.parameters,
                "status": r.status,
                "result": r.result,
                "approved": r.approved,
                "dry_run": r.dry_run,
            }
            for r in rows
        ]


@router.get("/conversations")
async def get_conversation_logs(
    session_id: Optional[str] = None,
    limit: int = Query(100, le=500),
):
    async with AsyncSessionLocal() as db:
        query = select(ConversationMessage).order_by(desc(ConversationMessage.timestamp)).limit(limit)
        if session_id:
            query = query.where(ConversationMessage.session_id == session_id)
        result = await db.execute(query)
        rows = result.scalars().all()
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "session_id": r.session_id,
                "role": r.role,
                "content": r.content,
                "model_used": r.model_used,
            }
            for r in rows
        ]


@router.delete("/clear")
async def clear_logs():
    async with AsyncSessionLocal() as db:
        await db.execute(ActionLog.__table__.delete())
        await db.execute(ConversationMessage.__table__.delete())
        await db.commit()
    return {"status": "cleared"}
