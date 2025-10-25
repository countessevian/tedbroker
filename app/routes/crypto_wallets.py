from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
import qrcode
from io import BytesIO
import base64

from app.database import get_collection, CRYPTO_WALLETS_COLLECTION
from app.auth import get_current_user_token

router = APIRouter(prefix="/api/crypto-wallets", tags=["crypto_wallets"])


@router.get("/")
async def get_crypto_wallets(current_user: dict = Depends(get_current_user_token)):
    """
    Get all active crypto wallets for deposits
    Requires authentication
    """
    try:
        wallets_collection = get_collection(CRYPTO_WALLETS_COLLECTION)
        wallets = []

        # Only get active wallets
        for wallet in wallets_collection.find({"is_active": True}):
            wallets.append({
                "id": str(wallet["_id"]),
                "currency": wallet["currency"],
                "wallet_address": wallet["wallet_address"],
                "network": wallet.get("network"),
                "qr_code_url": f"/api/crypto-wallets/{str(wallet['_id'])}/qr"
            })

        return {"success": True, "wallets": wallets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving crypto wallets: {str(e)}")


@router.get("/{wallet_id}")
async def get_wallet_details(wallet_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Get specific wallet details
    Requires authentication
    """
    try:
        from bson import ObjectId
        wallets_collection = get_collection(CRYPTO_WALLETS_COLLECTION)

        wallet = wallets_collection.find_one({"_id": ObjectId(wallet_id)})
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        return {
            "success": True,
            "wallet": {
                "id": str(wallet["_id"]),
                "currency": wallet["currency"],
                "wallet_address": wallet["wallet_address"],
                "network": wallet.get("network"),
                "qr_code_url": f"/api/crypto-wallets/{wallet_id}/qr"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving wallet: {str(e)}")


@router.get("/{wallet_id}/qr")
async def get_wallet_qr_code(wallet_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Generate and return QR code image for a specific wallet address
    Requires authentication
    Returns PNG image
    """
    try:
        from bson import ObjectId
        wallets_collection = get_collection(CRYPTO_WALLETS_COLLECTION)

        wallet = wallets_collection.find_one({"_id": ObjectId(wallet_id)})
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        # Add wallet address to QR code
        wallet_address = wallet["wallet_address"]
        qr.add_data(wallet_address)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return StreamingResponse(img_byte_arr, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")


@router.get("/{wallet_id}/qr/base64")
async def get_wallet_qr_code_base64(wallet_id: str, current_user: dict = Depends(get_current_user_token)):
    """
    Generate and return QR code as base64 encoded string
    Requires authentication
    Returns JSON with base64 image data
    """
    try:
        from bson import ObjectId
        wallets_collection = get_collection(CRYPTO_WALLETS_COLLECTION)

        wallet = wallets_collection.find_one({"_id": ObjectId(wallet_id)})
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        # Add wallet address to QR code
        wallet_address = wallet["wallet_address"]
        qr.add_data(wallet_address)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        img_base64 = base64.b64encode(img_byte_arr.read()).decode('utf-8')

        return {
            "success": True,
            "qr_code": f"data:image/png;base64,{img_base64}",
            "wallet_address": wallet_address,
            "currency": wallet["currency"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {str(e)}")
