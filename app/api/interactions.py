import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.crud import get_pending_interaction, respond_to_interaction
from app.auth.dependencies import get_current_user
from app.agents.interaction_manager import InteractionManager
from app.schemas.interaction import InteractionResponseData

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.get("/task/{task_id}/pending")
async def get_pending(
    task_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current pending interaction request for a task."""
    interaction = await get_pending_interaction(db, task_id)
    if not interaction:
        return {"pending": False}
    return {
        "pending": True,
        "request_id": interaction.id,
        "interaction_type": interaction.interaction_type.value,
        "tool_name": interaction.tool_name,
        "prompt_message": interaction.prompt_message,
        "fields": json.loads(interaction.fields_json) if interaction.fields_json else None,
        "preview": json.loads(interaction.preview_json) if interaction.preview_json else None,
    }


@router.post("/{request_id}/respond")
async def respond(
    request_id: int,
    response: InteractionResponseData,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """User responds to an interaction request. Unblocks the waiting tool."""
    interaction = await respond_to_interaction(db, request_id, response.model_dump_json())
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction request not found")

    InteractionManager.resolve(request_id, response.model_dump())

    return {"success": True}
