#!/usr/bin/env python3
"""
Migration script to add assigned_agent_name to existing chat conversations
that don't have one assigned yet.
"""
import random
from app.database import get_collection, CHAT_CONVERSATIONS_COLLECTION

# Pool of support agent names shown to users
SUPPORT_AGENT_NAMES = [
    "Sarah Mitchell",
    "James Thompson",
    "Emily Rodriguez",
    "Michael Chen",
    "Jessica Williams"
]

def migrate_conversations():
    """Add assigned_agent_name to conversations that don't have one"""
    conversations = get_collection(CHAT_CONVERSATIONS_COLLECTION)

    # Find conversations without assigned_agent_name
    conversations_to_update = conversations.find({
        "assigned_agent_name": {"$exists": False}
    })

    count = 0
    for conversation in conversations_to_update:
        # Assign a random agent name
        assigned_agent_name = random.choice(SUPPORT_AGENT_NAMES)

        # Update the conversation
        conversations.update_one(
            {"_id": conversation["_id"]},
            {"$set": {"assigned_agent_name": assigned_agent_name}}
        )

        count += 1
        print(f"Updated conversation {conversation['_id']} with agent name: {assigned_agent_name}")

    print(f"\nMigration complete! Updated {count} conversations.")

if __name__ == "__main__":
    migrate_conversations()
