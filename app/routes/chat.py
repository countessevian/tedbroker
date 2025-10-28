from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import random

from app.schemas import ChatMessageCreate, ChatMessageResponse, ChatConversationResponse, ChatConversationDetail
from app.auth import get_current_user_token
from app.database import (
    get_collection, USERS_COLLECTION, CHAT_CONVERSATIONS_COLLECTION,
    CHAT_MESSAGES_COLLECTION
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Pool of support agent names shown to users
SUPPORT_AGENT_NAMES = [
    "Sarah Mitchell",
    "James Thompson",
    "Emily Rodriguez",
    "Michael Chen",
    "Jessica Williams"
]


def get_user_by_id(user_id: str):
    """Get user by ID from database"""
    users = get_collection(USERS_COLLECTION)
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except:
        return None


@router.post("/send", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Send a chat message to support
    Creates a new conversation if conversation_id is not provided
    """
    conversations_col = get_collection(CHAT_CONVERSATIONS_COLLECTION)
    messages_col = get_collection(CHAT_MESSAGES_COLLECTION)
    users_col = get_collection(USERS_COLLECTION)

    # Get user details
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    conversation_id = message_data.conversation_id

    # If no conversation_id provided, create a new conversation
    if not conversation_id:
        # Check if user already has an active conversation
        existing_conversation = conversations_col.find_one({
            "user_id": current_user["user_id"],
            "status": "active"
        })

        if existing_conversation:
            conversation_id = str(existing_conversation["_id"])
        else:
            # Create new conversation with assigned support agent name
            assigned_agent_name = random.choice(SUPPORT_AGENT_NAMES)
            conversation = {
                "user_id": current_user["user_id"],
                "user_name": user.get("full_name") or user.get("username", "User"),
                "user_username": user.get("username", "User"),
                "user_email": user.get("email", ""),
                "assigned_agent_name": assigned_agent_name,  # Random agent name for this conversation
                "status": "active",
                "unread_admin_count": 1,  # Admin hasn't read this yet
                "unread_user_count": 0,   # User created the message
                "last_message": message_data.message[:100],
                "last_message_time": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = conversations_col.insert_one(conversation)
            conversation_id = str(result.inserted_id)
    else:
        # Validate conversation exists and belongs to user
        try:
            conversation = conversations_col.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": current_user["user_id"]
            })
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID"
            )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Update conversation
        conversations_col.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    "last_message": message_data.message[:100],
                    "last_message_time": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"unread_admin_count": 1}
            }
        )

    # Create message
    message = {
        "conversation_id": conversation_id,
        "sender_id": current_user["user_id"],
        "sender_type": "user",
        "sender_name": user.get("full_name") or user.get("username", "User"),
        "message": message_data.message,
        "is_read": False,
        "created_at": datetime.utcnow()
    }

    result = messages_col.insert_one(message)
    message["_id"] = result.inserted_id

    return ChatMessageResponse(
        id=str(message["_id"]),
        conversation_id=message["conversation_id"],
        sender_id=message["sender_id"],
        sender_type=message["sender_type"],
        sender_name=message["sender_name"],
        message=message["message"],
        is_read=message["is_read"],
        created_at=message["created_at"]
    )


@router.get("/conversation", response_model=Optional[ChatConversationDetail])
async def get_user_conversation(current_user: dict = Depends(get_current_user_token)):
    """
    Get the user's active conversation with all messages
    """
    conversations_col = get_collection(CHAT_CONVERSATIONS_COLLECTION)
    messages_col = get_collection(CHAT_MESSAGES_COLLECTION)

    # Get user's active conversation
    conversation = conversations_col.find_one({
        "user_id": current_user["user_id"],
        "status": "active"
    })

    if not conversation:
        return None

    conversation_id = str(conversation["_id"])

    # Get all messages for this conversation
    messages = list(messages_col.find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1))

    # Mark admin messages as read by user
    messages_col.update_many(
        {
            "conversation_id": conversation_id,
            "sender_type": "admin",
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )

    # Reset unread count for user
    conversations_col.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"unread_user_count": 0}}
    )

    message_responses = [
        ChatMessageResponse(
            id=str(msg["_id"]),
            conversation_id=msg["conversation_id"],
            sender_id=msg["sender_id"],
            sender_type=msg["sender_type"],
            sender_name=msg["sender_name"],
            message=msg["message"],
            is_read=msg["is_read"],
            created_at=msg["created_at"]
        )
        for msg in messages
    ]

    return ChatConversationDetail(
        id=conversation_id,
        user_id=conversation["user_id"],
        user_name=conversation["user_name"],
        user_email=conversation["user_email"],
        status=conversation["status"],
        messages=message_responses,
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"]
    )


@router.get("/messages", response_model=List[ChatMessageResponse])
async def get_conversation_messages(
    conversation_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get messages for a conversation
    If no conversation_id provided, gets messages from user's active conversation
    """
    conversations_col = get_collection(CHAT_CONVERSATIONS_COLLECTION)
    messages_col = get_collection(CHAT_MESSAGES_COLLECTION)

    if not conversation_id:
        # Get user's active conversation
        conversation = conversations_col.find_one({
            "user_id": current_user["user_id"],
            "status": "active"
        })

        if not conversation:
            return []

        conversation_id = str(conversation["_id"])
    else:
        # Verify conversation belongs to user
        try:
            conversation = conversations_col.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": current_user["user_id"]
            })
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID"
            )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

    # Get messages
    messages = list(messages_col.find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1))

    # Mark admin messages as read
    messages_col.update_many(
        {
            "conversation_id": conversation_id,
            "sender_type": "admin",
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )

    # Reset unread count for user
    conversations_col.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"unread_user_count": 0}}
    )

    return [
        ChatMessageResponse(
            id=str(msg["_id"]),
            conversation_id=msg["conversation_id"],
            sender_id=msg["sender_id"],
            sender_type=msg["sender_type"],
            sender_name=msg["sender_name"],
            message=msg["message"],
            is_read=msg["is_read"],
            created_at=msg["created_at"]
        )
        for msg in messages
    ]


@router.get("/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user_token)):
    """
    Get count of unread messages from admin
    """
    conversations_col = get_collection(CHAT_CONVERSATIONS_COLLECTION)

    conversation = conversations_col.find_one({
        "user_id": current_user["user_id"],
        "status": "active"
    })

    if not conversation:
        return {"unread_count": 0}

    return {"unread_count": conversation.get("unread_user_count", 0)}


@router.put("/close")
async def close_conversation(current_user: dict = Depends(get_current_user_token)):
    """
    Close the user's active conversation
    """
    conversations_col = get_collection(CHAT_CONVERSATIONS_COLLECTION)

    result = conversations_col.update_one(
        {
            "user_id": current_user["user_id"],
            "status": "active"
        },
        {
            "$set": {
                "status": "closed",
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active conversation found"
        )

    return {"message": "Conversation closed successfully"}
