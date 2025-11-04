from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from typing import List

from app.auth import get_current_user_token
from app.database import get_collection, NOTIFICATIONS_COLLECTION
from app.schemas import NotificationResponse

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/")
async def get_user_notifications(
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get all active notifications for the current user
    (includes broadcasts and user-specific notifications)

    Args:
        current_user: Current authenticated user

    Returns:
        list: User's notifications
    """
    notifications = get_collection(NOTIFICATIONS_COLLECTION)

    # Get notifications that are either:
    # 1. Broadcast to all users (target_type = 'all')
    # 2. Targeted specifically to this user
    query = {
        "$or": [
            {"target_type": "all"},
            {
                "target_type": "specific",
                "target_user_id": current_user["user_id"]
            }
        ]
    }

    cursor = notifications.find(query).sort("created_at", -1)

    notifications_list = []
    for notif in cursor:
        notifications_list.append({
            "id": str(notif["_id"]),
            "title": notif["title"],
            "message": notif["message"],
            "notification_type": notif["notification_type"],
            "is_dismissed": notif.get("is_dismissed", False),
            "created_at": notif["created_at"].isoformat()
        })

    return notifications_list


@router.put("/{notification_id}/dismiss")
async def dismiss_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Mark a notification as dismissed for the current user

    Args:
        notification_id: Notification ID
        current_user: Current authenticated user

    Returns:
        dict: Success message
    """
    notifications = get_collection(NOTIFICATIONS_COLLECTION)

    try:
        notification = notifications.find_one({"_id": ObjectId(notification_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID"
        )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # Verify this notification is accessible to the user
    is_accessible = (
        notification["target_type"] == "all" or
        (notification["target_type"] == "specific" and
         notification.get("target_user_id") == current_user["user_id"])
    )

    if not is_accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this notification"
        )

    # For broadcast notifications, we need to track dismissals per user
    # Add the user's ID to a dismissed_by array
    if notification["target_type"] == "all":
        notifications.update_one(
            {"_id": ObjectId(notification_id)},
            {"$addToSet": {"dismissed_by": current_user["user_id"]}}
        )
    else:
        # For specific notifications, mark as dismissed
        notifications.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"is_dismissed": True}}
        )

    return {"message": "Notification dismissed successfully"}


@router.get("/active")
async def get_active_notifications(
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get only non-dismissed notifications for the current user

    Args:
        current_user: Current authenticated user

    Returns:
        list: Active (non-dismissed) notifications
    """
    notifications = get_collection(NOTIFICATIONS_COLLECTION)

    # Get notifications that are:
    # 1. Broadcast to all AND user hasn't dismissed it
    # 2. Targeted to this user AND not dismissed
    query = {
        "$or": [
            {
                "target_type": "all",
                "dismissed_by": {"$ne": current_user["user_id"]}
            },
            {
                "target_type": "specific",
                "target_user_id": current_user["user_id"],
                "is_dismissed": {"$ne": True}
            }
        ]
    }

    cursor = notifications.find(query).sort("created_at", -1)

    notifications_list = []
    for notif in cursor:
        notifications_list.append({
            "id": str(notif["_id"]),
            "title": notif["title"],
            "message": notif["message"],
            "notification_type": notif["notification_type"],
            "created_at": notif["created_at"].isoformat()
        })

    return notifications_list
