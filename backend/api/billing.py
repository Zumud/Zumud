from fastapi import APIRouter, Depends, HTTPException, status, Body
import logging

from backend.api.auth import get_current_user
from backend.models import db_models
from backend.core.stripe_billing_service import create_customer_portal_session

router = APIRouter(prefix="/billing", tags=["billing"])

logger = logging.getLogger(__name__)


@router.post("/manage-subscription")
async def manage_subscription(
    return_url: str = Body(..., description="URL to redirect back to after portal session"),
    current_user: db_models.User = Depends(get_current_user)
):
    """
    Create a Stripe Customer Portal session for the authenticated user.
    
    This allows users to:
    - Add/remove payment methods
    - View billing history and invoices
    - Update subscription details
    - Download receipts
    - Manage tax information
    
    Args:
        return_url: URL to redirect back to after the portal session (required)
        current_user: Authenticated user from JWT token
        
    Returns:
        dict: Contains the portal session URL for redirection
        
    Raises:
        HTTPException: If portal session creation fails
    """
    try:
        # Create customer portal session
        portal_url = create_customer_portal_session(
            email=current_user.email,
            name=current_user.username,
            return_url=return_url
        )
        
        if portal_url is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create customer portal session. Please try again later."
            )
        
        logger.info(f"Created customer portal session for user {current_user.email}")
        
        return {
            "portal_url": portal_url,
            "message": "Customer portal session created successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating customer portal for {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the customer portal session"
        )
