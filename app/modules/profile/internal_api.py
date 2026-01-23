"""
Internal API endpoints for Profile Service.
These endpoints are called by other services (e.g., Auth Service).
"""
from fastapi import APIRouter, Path

from app.api.deps import ProfileServicePathDep
from app.modules.profile.schemas import (
    ProfileProvision,
    ProfileProvisionResponse,
)

router = APIRouter()


@router.post(
    "/internal/{tenant_id}/provision-profile",
    response_model=ProfileProvisionResponse,
    tags=["Internal API"],
)
async def provision_profile(
    data: ProfileProvision,
    service: ProfileServicePathDep,
    tenant_id: str = Path(..., description="Tenant ID"),
):
    """
    Internal endpoint for Auth Service to provision a new profile.

    This endpoint:
    1. Creates a new Profile with default verification_status="unverified"
    2. Creates a Wallet linked to the Profile
    3. Creates default Privacy Settings

    Returns profile_id and wallet_id for the Auth Service to store.
    """
    profile, wallet, _privacy = await service.provision_profile(data)

    return ProfileProvisionResponse(
        profile_id=profile.profile_id,
        wallet_id=wallet.wallet_id,
        verification_status=profile.verification_status,
        created_at=profile.created_at,
    )
