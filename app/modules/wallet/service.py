import uuid
from decimal import Decimal
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.modules.profile.models import (
    Profile,
    Wallet,
    WalletAsset,
    AssetRateToCredit,
    WalletTransaction,
)
from app.modules.wallet.schemas import WalletAssetCreate, AssetRateCreate


class WalletService:
    def __init__(self, tenant_db: AsyncSession):
        self.tenant_db = tenant_db

    async def _get_profile_by_user_id(self, user_id: int) -> Profile:
        result = await self.tenant_db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile chưa được tạo")
        return profile

    async def get_wallet(self, user_id: int) -> Wallet:
        profile = await self._get_profile_by_user_id(user_id)

        result = await self.tenant_db.execute(
            select(Wallet).where(Wallet.profile_id == profile.profile_id)
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            raise HTTPException(status_code=404, detail="Ví không tồn tại")
        return wallet

    async def create_wallet(self, user_id: int) -> Wallet:
        profile = await self._get_profile_by_user_id(user_id)

        existing = await self.tenant_db.execute(
            select(Wallet).where(Wallet.profile_id == profile.profile_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Ví đã tồn tại")

        wallet_id = str(uuid.uuid4())
        new_wallet = Wallet(
            wallet_id=wallet_id,
            profile_id=profile.profile_id,
            ets=Decimal(0),
        )
        self.tenant_db.add(new_wallet)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_wallet)
        return new_wallet

    async def topup_wallet(
        self,
        user_id: int,
        amount: Decimal,
        ref_type: str | None = None,
        ref_id: str | None = None,
    ) -> Wallet:
        wallet = await self.get_wallet(user_id)

        if amount <= 0:
            raise HTTPException(status_code=400, detail="Số tiền phải lớn hơn 0")

        tx_id = str(uuid.uuid4())
        transaction = WalletTransaction(
            tx_id=tx_id,
            wallet_id=wallet.wallet_id,
            asset_type="credit",
            direction=1,
            amount=amount,
            ref_type=ref_type,
            ref_id=ref_id,
        )
        self.tenant_db.add(transaction)

        wallet.ets = Decimal(str(wallet.ets or Decimal(0))) + amount  # type: ignore

        await self.tenant_db.commit()
        await self.tenant_db.refresh(wallet)
        return wallet

    async def transfer_wallet(
        self, user_id: int, target_profile_id: str, amount: Decimal
    ) -> Wallet:
        wallet = await self.get_wallet(user_id)

        if amount <= 0:
            raise HTTPException(status_code=400, detail="Số tiền phải lớn hơn 0")

        if Decimal(str(wallet.ets or Decimal(0))) < amount:
            raise HTTPException(status_code=400, detail="Số dư không đủ")

        target_profile_result = await self.tenant_db.execute(
            select(Profile).where(Profile.profile_id == target_profile_id)
        )
        target_profile = target_profile_result.scalar_one_or_none()
        if not target_profile:
            raise HTTPException(status_code=404, detail="Người nhận không tồn tại")

        target_wallet_result = await self.tenant_db.execute(
            select(Wallet).where(Wallet.profile_id == target_profile_id)
        )
        target_wallet = target_wallet_result.scalar_one_or_none()
        if not target_wallet:
            raise HTTPException(status_code=404, detail="Ví người nhận không tồn tại")

        tx_id = str(uuid.uuid4())
        transaction = WalletTransaction(
            tx_id=tx_id,
            wallet_id=wallet.wallet_id,
            asset_type="credit",
            direction=-1,
            amount=amount,
            ref_type="transfer",
            ref_id=target_wallet.wallet_id,
        )
        self.tenant_db.add(transaction)

        tx_id_out = str(uuid.uuid4())
        transaction_out = WalletTransaction(
            tx_id=tx_id_out,
            wallet_id=target_wallet.wallet_id,
            asset_type="credit",
            direction=1,
            amount=amount,
            ref_type="transfer",
            ref_id=wallet.wallet_id,
        )
        self.tenant_db.add(transaction_out)

        wallet.ets = Decimal(str(wallet.ets or Decimal(0))) - amount  # type: ignore
        target_wallet.ets = Decimal(str(target_wallet.ets or Decimal(0))) + amount  # type: ignore

        await self.tenant_db.commit()
        await self.tenant_db.refresh(wallet)
        return wallet

    async def get_wallet_assets(self, user_id: int) -> list[WalletAsset]:
        wallet = await self.get_wallet(user_id)

        result = await self.tenant_db.execute(
            select(WalletAsset)
            .where(WalletAsset.wallet_id == wallet.wallet_id)
            .order_by(desc(WalletAsset.created_at))
        )
        return list(result.scalars().all())

    async def add_wallet_asset(
        self, user_id: int, data: WalletAssetCreate
    ) -> WalletAsset:
        wallet = await self.get_wallet(user_id)

        asset_id = str(uuid.uuid4())
        new_asset = WalletAsset(
            asset_id=asset_id,
            wallet_id=wallet.wallet_id,
            asset_type=data.asset_type,
            asset_code=data.asset_code,
            amount=data.amount,
            metadata_id=data.metadata_id,
        )
        self.tenant_db.add(new_asset)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_asset)
        return new_asset

    async def get_wallet_transactions(self, user_id: int) -> list[WalletTransaction]:
        wallet = await self.get_wallet(user_id)

        result = await self.tenant_db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet.wallet_id)
            .order_by(desc(WalletTransaction.created_at))
        )
        return list(result.scalars().all())

    async def get_asset_rates(self) -> list[AssetRateToCredit]:
        result = await self.tenant_db.execute(
            select(AssetRateToCredit).order_by(AssetRateToCredit.created_at)
        )
        return list(result.scalars().all())

    async def create_asset_rate(self, data: AssetRateCreate) -> AssetRateToCredit:
        rate_id = str(uuid.uuid4())
        new_rate = AssetRateToCredit(
            rate_id=rate_id,
            from_asset_type=data.from_asset_type,
            rate_to_ets=data.rate_to_ets,
            metadata_id=data.metadata_id,
        )
        self.tenant_db.add(new_rate)
        await self.tenant_db.commit()
        await self.tenant_db.refresh(new_rate)
        return new_rate
