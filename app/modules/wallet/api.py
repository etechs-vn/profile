from typing import List

from fastapi import APIRouter, Path

from app.api.deps import WalletServicePathDep
from app.modules.wallet.schemas import (
    WalletResponse,
    WalletAssetResponse,
    WalletAssetCreate,
    AssetRateResponse,
    AssetRateCreate,
    WalletTransactionResponse,
    WalletTopupRequest,
    WalletTransferRequest,
)

router = APIRouter()


@router.post(
    "/{tenant_id}/users/{user_id}/wallet",
    response_model=WalletResponse,
)
async def create_wallet(
    service: WalletServicePathDep,
    user_id: int = Path(...),
):
    return await service.create_wallet(user_id)


@router.get(
    "/{tenant_id}/users/{user_id}/wallet",
    response_model=WalletResponse,
)
async def get_wallet(
    service: WalletServicePathDep,
    user_id: int = Path(...),
):
    return await service.get_wallet(user_id)


@router.post(
    "/{tenant_id}/users/{user_id}/wallet/topup",
    response_model=WalletResponse,
)
async def topup_wallet(
    topup_data: WalletTopupRequest,
    service: WalletServicePathDep,
    user_id: int = Path(...),
):
    return await service.topup_wallet(user_id, topup_data.amount)


@router.post(
    "/{tenant_id}/users/{user_id}/wallet/transfer",
    response_model=WalletResponse,
)
async def transfer_wallet(
    transfer_data: WalletTransferRequest,
    service: WalletServicePathDep,
    user_id: int = Path(...),
):
    return await service.transfer_wallet(
        user_id, transfer_data.target_profile_id, transfer_data.amount
    )


@router.get(
    "/{tenant_id}/users/{user_id}/wallet/assets",
    response_model=List[WalletAssetResponse],
)
async def get_wallet_assets(
    service: WalletServicePathDep,
    user_id: int = Path(...),
):
    return await service.get_wallet_assets(user_id)


@router.post(
    "/{tenant_id}/users/{user_id}/wallet/assets",
    response_model=WalletAssetResponse,
)
async def add_wallet_asset(
    asset_data: WalletAssetCreate,
    service: WalletServicePathDep,
    user_id: int = Path(...),
):
    return await service.add_wallet_asset(user_id, asset_data)


@router.get(
    "/{tenant_id}/users/{user_id}/wallet/transactions",
    response_model=List[WalletTransactionResponse],
)
async def get_wallet_transactions(
    service: WalletServicePathDep,
    user_id: int = Path(...),
):
    return await service.get_wallet_transactions(user_id)


@router.get(
    "/{tenant_id}/wallet/rates",
    response_model=List[AssetRateResponse],
)
async def get_asset_rates(
    service: WalletServicePathDep,
):
    return await service.get_asset_rates()


@router.post(
    "/{tenant_id}/wallet/rates",
    response_model=AssetRateResponse,
)
async def create_asset_rate(
    rate_data: AssetRateCreate,
    service: WalletServicePathDep,
):
    return await service.create_asset_rate(rate_data)
