from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging

from backend.api.auth import get_current_user
from backend.models import db_models
from backend.core.stripe_billing_service import create_customer_portal_session
from backend.config.envs import CUSTOMER_PORTAL_RETURN_URL


class CustomerPortalRequest(BaseModel):
    return_url: Optional[str] = None

router = APIRouter(prefix="/billing", tags=["billing"])

logger = logging.getLogger(__name__)


@router.post("/manage-subscription")
async def manage_subscription(
    request: CustomerPortalRequest,
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
        request: Request body containing optional return_url (uses environment default if not provided)
        current_user: Authenticated user from JWT token
        
    Returns:
        dict: Contains the portal session URL for redirection
        
    Raises:
        HTTPException: If portal session creation fails
    """
    try:
        # Use provided return_url or fall back to environment configuration
        return_url = request.return_url or CUSTOMER_PORTAL_RETURN_URL
        
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
