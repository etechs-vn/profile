from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class WalletBaseResponse(BaseModel):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WalletResponse(WalletBaseResponse):
    wallet_id: str
    profile_id: str
    ets: Optional[Decimal] = None
    metadata_id: Optional[str] = None


class WalletCreate(BaseModel):
    metadata_id: Optional[str] = None


class WalletAssetResponse(WalletBaseResponse):
    asset_id: str
    wallet_id: str
    asset_type: Optional[str] = None
    asset_code: Optional[str] = None
    amount: Optional[Decimal] = None
    metadata_id: Optional[str] = None


class WalletAssetCreate(BaseModel):
    asset_type: Optional[str] = None
    asset_code: Optional[str] = None
    amount: Optional[Decimal] = None
    metadata_id: Optional[str] = None


class AssetRateResponse(WalletBaseResponse):
    rate_id: str
    from_asset_type: Optional[str] = None
    rate_to_ets: Optional[Decimal] = None
    metadata_id: Optional[str] = None


class AssetRateCreate(BaseModel):
    from_asset_type: Optional[str] = None
    rate_to_ets: Optional[Decimal] = None
    metadata_id: Optional[str] = None


class WalletTransactionResponse(WalletBaseResponse):
    tx_id: str
    wallet_id: str
    asset_type: Optional[str] = None
    direction: Optional[int] = None
    amount: Optional[Decimal] = None
    ref_type: Optional[str] = None
    ref_id: Optional[str] = None
    metadata_id: Optional[str] = None


class WalletTransactionCreate(BaseModel):
    asset_type: Optional[str] = None
    direction: Optional[int] = None
    amount: Optional[Decimal] = None
    ref_type: Optional[str] = None
    ref_id: Optional[str] = None
    metadata_id: Optional[str] = None


class WalletTopupRequest(BaseModel):
    amount: Decimal


class WalletTransferRequest(BaseModel):
    target_profile_id: str
    amount: Decimal
