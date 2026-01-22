from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TenantBase

if TYPE_CHECKING:
    from app.modules.social.models import Group, UserAction


class Profile(TenantBase):
    """
    Bảng thông tin hồ sơ người dùng (profile).

    Quan hệ:
    - user_id: Liên kết với User trong Shared Database (nhiều-1 với profile)
    - Mỗi User có thể có nhiều Profile (một per tenant)
    - Trong một tenant, mỗi user chỉ có 1 profile duy nhất (enforced by app logic)
    """

    __tablename__ = "profile"

    profile_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True, nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships (Reverse)
    educations: Mapped[list["Education"]] = relationship(back_populates="profile")
    identity_documents: Mapped[list["IdentityDocument"]] = relationship(
        back_populates="profile"
    )
    wallets: Mapped[list["Wallet"]] = relationship(back_populates="profile")
    user_interests: Mapped[list["UserInterest"]] = relationship(
        back_populates="profile"
    )

    # Relationships for Social module
    groups: Mapped[list["Group"]] = relationship("Group", back_populates="profile")
    user_actions: Mapped[list["UserAction"]] = relationship(
        "UserAction", back_populates="profile"
    )


class Education(TenantBase):
    """
    Bảng thông tin học vấn (education).
    """

    __tablename__ = "education"

    education_id: Mapped[str] = mapped_column(String, primary_key=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))

    education_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    institution_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_current: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    credential_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    credential_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issuing_organization: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    credential_ref: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="educations")

    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL OR end_date >= start_date",
            name="check_education_dates",
        ),
    )


class IdentityDocument(TenantBase):
    """
    Bảng giấy tờ tùy thân (identity_documents).
    """

    __tablename__ = "identity_documents"

    identity_id: Mapped[str] = mapped_column(String, primary_key=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))

    document_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_number: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    issued_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="identity_documents")


class Wallet(TenantBase):
    """
    Bảng ví người dùng (wallets).
    """

    __tablename__ = "wallets"

    wallet_id: Mapped[str] = mapped_column(String, primary_key=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))

    ets: Mapped[Optional[Numeric]] = mapped_column(Numeric(16, 2), nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="wallets")
    assets: Mapped[list["WalletAsset"]] = relationship(back_populates="wallet")
    transactions: Mapped[list["WalletTransaction"]] = relationship(
        back_populates="wallet"
    )


class WalletAsset(TenantBase):
    """
    Bảng tài sản trong ví (wallet_assets).
    """

    __tablename__ = "wallet_assets"

    asset_id: Mapped[str] = mapped_column(String, primary_key=True)
    wallet_id: Mapped[str] = mapped_column(ForeignKey("wallets.wallet_id"))

    asset_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    asset_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amount: Mapped[Optional[Numeric]] = mapped_column(Numeric(16, 2), nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    wallet: Mapped["Wallet"] = relationship(back_populates="assets")


class AssetRateToCredit(TenantBase):
    """
    Bảng tỷ lệ quy đổi tài sản sang tín dụng (asset_rates_to_credit).
    """

    __tablename__ = "asset_rates_to_credit"

    rate_id: Mapped[str] = mapped_column(String, primary_key=True)

    from_asset_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rate_to_ets: Mapped[Optional[Numeric]] = mapped_column(
        Numeric(16, 2), nullable=True
    )
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class WalletTransaction(TenantBase):
    """
    Bảng giao dịch ví (wallet_transactions).
    """

    __tablename__ = "wallet_transactions"

    tx_id: Mapped[str] = mapped_column(String, primary_key=True)
    wallet_id: Mapped[str] = mapped_column(ForeignKey("wallets.wallet_id"))

    asset_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    direction: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    amount: Mapped[Optional[Numeric]] = mapped_column(Numeric(16, 2), nullable=True)
    ref_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ref_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    wallet: Mapped["Wallet"] = relationship(back_populates="transactions")

    __table_args__ = (
        CheckConstraint("direction IN (1, -1)", name="check_wallet_tx_direction"),
    )


class UserInterest(TenantBase):
    """
    Bảng sở thích người dùng (user_interests).
    """

    __tablename__ = "user_interests"

    interest_id: Mapped[str] = mapped_column(String, primary_key=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.profile_id"))

    interest_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    normalized_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile: Mapped["Profile"] = relationship(back_populates="user_interests")
    mappings: Mapped[list["InterestMapping"]] = relationship(
        back_populates="user_interest"
    )


class InterestCanonical(TenantBase):
    """
    Bảng sở thích chuẩn (interest_canonical).
    """

    __tablename__ = "interest_canonical"

    canonical_id: Mapped[str] = mapped_column(String, primary_key=True)

    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slug: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    mappings: Mapped[list["InterestMapping"]] = relationship(back_populates="canonical")


class InterestMapping(TenantBase):
    """
    Bảng ánh xạ sở thích (interest_mapping).
    """

    __tablename__ = "interest_mapping"

    interest_id: Mapped[str] = mapped_column(
        ForeignKey("user_interests.interest_id"), primary_key=True
    )
    canonical_id: Mapped[str] = mapped_column(
        ForeignKey("interest_canonical.canonical_id")
    )

    confidence: Mapped[Optional[Numeric]] = mapped_column(Numeric(6, 2), nullable=True)
    mapped_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mapped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user_interest: Mapped["UserInterest"] = relationship(back_populates="mappings")
    canonical: Mapped["InterestCanonical"] = relationship(back_populates="mappings")
