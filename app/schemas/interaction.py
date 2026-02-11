from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class InteractionResponseData(BaseModel):
    confirmed: Optional[bool] = None
    values: Optional[Dict[str, Any]] = None
    cancelled: bool = False


class InteractionFieldSchema(BaseModel):
    name: str
    label: str
    type: str = "text"
    required: bool = True
    default: Optional[str] = None


class PendingInteractionResponse(BaseModel):
    pending: bool
    request_id: Optional[int] = None
    interaction_type: Optional[str] = None
    tool_name: Optional[str] = None
    prompt_message: Optional[str] = None
    fields: Optional[List[InteractionFieldSchema]] = None
    preview: Optional[Dict[str, Any]] = None
