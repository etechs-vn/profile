import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.modules.profile.models import Profile, Wallet
from app.modules.wallet.schemas import WalletAssetCreate, AssetRateCreate
from app.modules.wallet.service import WalletService


# --- Fixtures ---


@pytest.fixture
async def tenant_db(db_manager, sample_tenant):
    """Get a tenant DB session with tables created."""
    # Ensure schema exists
    await db_manager.ensure_tenant_tables(sample_tenant.tenant_id)

    # Get session
    factory = await db_manager.get_tenant_session_factory(sample_tenant.tenant_id)
    async with factory() as session:
        yield session


@pytest.fixture
async def sample_profile_with_wallet(tenant_db):
    """Create a sample profile with wallet directly in tenant DB."""
    profile = Profile(profile_id="test-profile-1", user_id=1, nickname="Test User")
    tenant_db.add(profile)
    await tenant_db.commit()
    await tenant_db.refresh(profile)

    wallet = Wallet(
        wallet_id="test-wallet-1", profile_id=profile.profile_id, ets=Decimal(100)
    )
    tenant_db.add(wallet)
    await tenant_db.commit()
    await tenant_db.refresh(wallet)

    return profile


# --- Tests ---


@pytest.mark.asyncio
async def test_create_wallet(tenant_db, sample_profile_with_wallet):
    """Test creating a new wallet (if one doesn't exist)."""
    # Create another user
    profile2 = Profile(profile_id="test-profile-2", user_id=2, nickname="Test User 2")
    tenant_db.add(profile2)
    await tenant_db.commit()

    service = WalletService(tenant_db)
    wallet = await service.create_wallet(profile2.user_id)

    assert wallet.wallet_id is not None
    assert wallet.profile_id == profile2.profile_id
    assert wallet.ets == Decimal(0)


@pytest.mark.asyncio
async def test_create_wallet_duplicate(tenant_db, sample_profile_with_wallet):
    """Test creating duplicate wallet raises error."""
    service = WalletService(tenant_db)

    with pytest.raises(HTTPException) as exc:
        await service.create_wallet(sample_profile_with_wallet.user_id)

    assert exc.value.status_code == 400
    assert "Ví đã tồn tại" in exc.value.detail


@pytest.mark.asyncio
async def test_get_wallet(tenant_db, sample_profile_with_wallet):
    """Test getting wallet."""
    service = WalletService(tenant_db)
    wallet = await service.get_wallet(sample_profile_with_wallet.user_id)

    assert wallet.wallet_id == "test-wallet-1"
    assert wallet.ets == Decimal(100)


@pytest.mark.asyncio
async def test_get_wallet_not_found(tenant_db):
    """Test getting non-existent wallet."""
    # Create a profile without wallet
    profile = Profile(
        profile_id="test-profile-no-wallet", user_id=9999, nickname="No Wallet User"
    )
    tenant_db.add(profile)
    await tenant_db.commit()

    service = WalletService(tenant_db)

    with pytest.raises(HTTPException) as exc:
        await service.get_wallet(9999)

    assert exc.value.status_code == 404
    assert "Ví không tồn tại" in exc.value.detail


@pytest.mark.asyncio
async def test_topup_wallet(tenant_db, sample_profile_with_wallet):
    """Test topping up wallet."""
    service = WalletService(tenant_db)

    wallet = await service.topup_wallet(sample_profile_with_wallet.user_id, Decimal(50))

    assert wallet.ets == Decimal(150)

    # Verify transaction was created
    transactions = await service.get_wallet_transactions(
        sample_profile_with_wallet.user_id
    )
    assert len(transactions) == 1
    assert transactions[0].direction == 1
    assert transactions[0].amount == Decimal(50)


@pytest.mark.asyncio
async def test_topup_wallet_invalid_amount(tenant_db, sample_profile_with_wallet):
    """Test topping up with invalid amount raises error."""
    service = WalletService(tenant_db)

    with pytest.raises(HTTPException) as exc:
        await service.topup_wallet(sample_profile_with_wallet.user_id, Decimal(-10))

    assert exc.value.status_code == 400
    assert "Số tiền phải lớn hơn 0" in exc.value.detail


@pytest.mark.asyncio
async def test_transfer_wallet(tenant_db, sample_profile_with_wallet):
    """Test transferring money between wallets."""
    service = WalletService(tenant_db)

    # Create receiver profile and wallet
    receiver = Profile(profile_id="test-profile-3", user_id=3, nickname="Receiver")
    tenant_db.add(receiver)
    await tenant_db.commit()
    await tenant_db.refresh(receiver)

    receiver_wallet = Wallet(
        wallet_id="test-wallet-3", profile_id=receiver.profile_id, ets=Decimal(50)
    )
    tenant_db.add(receiver_wallet)
    await tenant_db.commit()

    # Transfer
    wallet = await service.transfer_wallet(
        sample_profile_with_wallet.user_id, receiver.profile_id, Decimal(30)
    )

    assert wallet.ets == Decimal(70)

    # Verify receiver wallet was updated
    receiver_wallet_updated = await service.get_wallet(receiver.user_id)
    assert receiver_wallet_updated.ets == Decimal(80)

    # Verify transactions were created
    sender_transactions = await service.get_wallet_transactions(
        sample_profile_with_wallet.user_id
    )
    assert len(sender_transactions) == 1
    assert sender_transactions[0].direction == -1


@pytest.mark.asyncio
async def test_transfer_wallet_insufficient_balance(
    tenant_db, sample_profile_with_wallet
):
    """Test transfer with insufficient balance raises error."""
    service = WalletService(tenant_db)

    # Create receiver profile and wallet
    receiver = Profile(profile_id="test-profile-4", user_id=4, nickname="Receiver")
    tenant_db.add(receiver)
    await tenant_db.commit()

    with pytest.raises(HTTPException) as exc:
        await service.transfer_wallet(
            sample_profile_with_wallet.user_id, receiver.profile_id, Decimal(200)
        )

    assert exc.value.status_code == 400
    assert "Số dư không đủ" in exc.value.detail


@pytest.mark.asyncio
async def test_add_wallet_asset(tenant_db, sample_profile_with_wallet):
    """Test adding asset to wallet."""
    service = WalletService(tenant_db)

    asset_data = WalletAssetCreate(
        asset_type="coin", asset_code="GOLD", amount=Decimal(10)
    )

    asset = await service.add_wallet_asset(
        sample_profile_with_wallet.user_id, asset_data
    )

    assert asset.asset_id is not None
    assert asset.asset_type == "coin"
    assert asset.asset_code == "GOLD"
    assert asset.amount == Decimal(10)


@pytest.mark.asyncio
async def test_get_wallet_assets(tenant_db, sample_profile_with_wallet):
    """Test getting wallet assets."""
    service = WalletService(tenant_db)

    # Add multiple assets
    await service.add_wallet_asset(
        sample_profile_with_wallet.user_id,
        WalletAssetCreate(asset_type="coin", asset_code="GOLD", amount=Decimal(10)),
    )
    await service.add_wallet_asset(
        sample_profile_with_wallet.user_id,
        WalletAssetCreate(asset_type="token", asset_code="SILVER", amount=Decimal(5)),
    )

    assets = await service.get_wallet_assets(sample_profile_with_wallet.user_id)

    assert len(assets) == 2
    assert assets[0].asset_type == "token"  # Should be sorted by created_at desc
    assert assets[1].asset_type == "coin"


@pytest.mark.asyncio
async def test_get_wallet_transactions(tenant_db, sample_profile_with_wallet):
    """Test getting wallet transactions."""
    service = WalletService(tenant_db)

    # Add transactions
    await service.topup_wallet(sample_profile_with_wallet.user_id, Decimal(10))
    await service.topup_wallet(sample_profile_with_wallet.user_id, Decimal(20))

    transactions = await service.get_wallet_transactions(
        sample_profile_with_wallet.user_id
    )

    assert len(transactions) == 2
    assert transactions[0].amount == Decimal(20)  # Most recent first


@pytest.mark.asyncio
async def test_create_asset_rate(tenant_db):
    """Test creating asset exchange rate."""
    service = WalletService(tenant_db)

    rate_data = AssetRateCreate(from_asset_type="coin", rate_to_ets=Decimal(1.5))

    rate = await service.create_asset_rate(rate_data)

    assert rate.rate_id is not None
    assert rate.from_asset_type == "coin"
    assert rate.rate_to_ets == Decimal(1.5)


@pytest.mark.asyncio
async def test_get_asset_rates(tenant_db):
    """Test getting all asset rates."""
    service = WalletService(tenant_db)

    await service.create_asset_rate(
        AssetRateCreate(from_asset_type="coin", rate_to_ets=Decimal(1.5))
    )
    await service.create_asset_rate(
        AssetRateCreate(from_asset_type="token", rate_to_ets=Decimal(2.0))
    )

    rates = await service.get_asset_rates()

    assert len(rates) == 2
