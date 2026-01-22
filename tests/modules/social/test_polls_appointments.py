import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.modules.profile.models import Profile
from app.modules.social.models import Group
from app.modules.social.schemas import PollCreate, PollOptionCreate, AppointmentCreate
from app.modules.social.service import SocialService


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
async def sample_profile(tenant_db):
    """Create a sample profile directly in tenant DB."""
    profile = Profile(profile_id="test-profile-1", user_id=1, nickname="Test User")
    tenant_db.add(profile)
    await tenant_db.commit()
    await tenant_db.refresh(profile)
    return profile


@pytest.fixture
async def sample_group(tenant_db, sample_profile):
    """Create a sample group."""
    group = Group(
        group_id="test-group-1",
        profile_id=sample_profile.profile_id,
        role=True,
        joined_at=datetime.now(),
    )
    tenant_db.add(group)
    await tenant_db.commit()
    await tenant_db.refresh(group)
    return group


# --- Poll Tests ---


@pytest.mark.asyncio
async def test_create_poll(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    poll_data = PollCreate(
        title="What's your favorite color?",
        options=[
            PollOptionCreate(option_text="Red"),
            PollOptionCreate(option_text="Blue"),
            PollOptionCreate(option_text="Green"),
        ],
    )

    poll = await service.create_poll(
        sample_profile.user_id, sample_group.group_id, poll_data
    )

    assert poll.poll_id is not None
    assert poll.title == "What's your favorite color?"
    assert poll.is_closed is False
    assert len(poll.options) == 3


@pytest.mark.asyncio
async def test_get_poll(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    poll_data = PollCreate(
        title="Test Poll",
        options=[
            PollOptionCreate(option_text="Yes"),
            PollOptionCreate(option_text="No"),
        ],
    )

    poll = await service.create_poll(
        sample_profile.user_id, sample_group.group_id, poll_data
    )

    fetched_poll = await service.get_poll(poll.poll_id)

    assert fetched_poll.poll_id == poll.poll_id
    assert fetched_poll.title == "Test Poll"
    assert len(fetched_poll.options) == 2


@pytest.mark.asyncio
async def test_get_poll_not_found(tenant_db):
    service = SocialService(tenant_db)

    with pytest.raises(HTTPException) as exc:
        await service.get_poll("non-existent-poll-id")

    assert exc.value.status_code == 404
    assert "Bình chọn không tồn tại" in exc.value.detail


@pytest.mark.asyncio
async def test_get_group_polls(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    # Create multiple polls
    await service.create_poll(
        sample_profile.user_id,
        sample_group.group_id,
        PollCreate(title="Poll 1", options=[PollOptionCreate(option_text="A")]),
    )
    await service.create_poll(
        sample_profile.user_id,
        sample_group.group_id,
        PollCreate(title="Poll 2", options=[PollOptionCreate(option_text="B")]),
    )

    polls = await service.get_group_polls(sample_group.group_id)

    assert len(polls) == 2


@pytest.mark.asyncio
async def test_vote_poll(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    poll = await service.create_poll(
        sample_profile.user_id,
        sample_group.group_id,
        PollCreate(title="Test", options=[PollOptionCreate(option_text="Yes")]),
    )

    vote = await service.vote_poll(
        sample_profile.user_id, poll.poll_id, poll.options[0].option_id
    )

    assert vote.poll_vote_id is not None
    assert vote.option_id == poll.options[0].option_id


@pytest.mark.asyncio
async def test_vote_poll_closed(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    poll = await service.create_poll(
        sample_profile.user_id,
        sample_group.group_id,
        PollCreate(title="Test", options=[PollOptionCreate(option_text="Yes")]),
    )

    # Close the poll
    await service.close_poll(sample_profile.user_id, poll.poll_id)

    # Get poll again to get fresh state
    updated_poll = await service.get_poll(poll.poll_id)

    # Try to vote
    with pytest.raises(HTTPException) as exc:
        await service.vote_poll(
            sample_profile.user_id, poll.poll_id, updated_poll.options[0].option_id
        )

    assert exc.value.status_code == 400
    assert "Bình chọn đã đóng" in exc.value.detail


@pytest.mark.asyncio
async def test_close_poll(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    poll = await service.create_poll(
        sample_profile.user_id,
        sample_group.group_id,
        PollCreate(title="Test", options=[PollOptionCreate(option_text="Yes")]),
    )

    closed_poll = await service.close_poll(sample_profile.user_id, poll.poll_id)

    assert closed_poll.is_closed is True


@pytest.mark.asyncio
async def test_close_poll_unauthorized(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    # Create poll by profile 1
    poll = await service.create_poll(
        sample_profile.user_id,
        sample_group.group_id,
        PollCreate(title="Test", options=[PollOptionCreate(option_text="Yes")]),
    )

    # Create another profile
    profile2 = Profile(profile_id="profile-2", user_id=2, nickname="User 2")
    tenant_db.add(profile2)
    await tenant_db.commit()

    # Try to close poll by profile 2
    with pytest.raises(HTTPException) as exc:
        await service.close_poll(profile2.user_id, poll.poll_id)

    assert exc.value.status_code == 403


# --- Appointment Tests ---


@pytest.mark.asyncio
async def test_create_appointment(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)

    appt_data = AppointmentCreate(
        title="Team Meeting",
        start_time=start_time,
        end_time=end_time,
        note="Discuss project roadmap",
        remind_enabled=True,
        remind_before_minutes=15,
    )

    appointment = await service.create_appointment(
        sample_profile.user_id, sample_group.group_id, appt_data
    )

    assert appointment.appointment_id is not None
    assert appointment.title == "Team Meeting"
    assert appointment.remind_enabled is True
    assert appointment.remind_before_minutes == 15


@pytest.mark.asyncio
async def test_get_appointment(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    appt_data = AppointmentCreate(title="Test Appt")
    created = await service.create_appointment(
        sample_profile.user_id, sample_group.group_id, appt_data
    )

    fetched = await service.get_appointment(created.appointment_id)

    assert fetched.appointment_id == created.appointment_id
    assert fetched.title == "Test Appt"


@pytest.mark.asyncio
async def test_get_appointment_not_found(tenant_db):
    service = SocialService(tenant_db)

    with pytest.raises(HTTPException) as exc:
        await service.get_appointment("non-existent-appointment-id")

    assert exc.value.status_code == 404
    assert "Cuộc hẹn không tồn tại" in exc.value.detail


@pytest.mark.asyncio
async def test_get_group_appointments(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    await service.create_appointment(
        sample_profile.user_id,
        sample_group.group_id,
        AppointmentCreate(title="Appt 1"),
    )
    await service.create_appointment(
        sample_profile.user_id,
        sample_group.group_id,
        AppointmentCreate(title="Appt 2"),
    )

    appointments = await service.get_group_appointments(sample_group.group_id)

    assert len(appointments) == 2


@pytest.mark.asyncio
async def test_update_appointment(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    created = await service.create_appointment(
        sample_profile.user_id,
        sample_group.group_id,
        AppointmentCreate(title="Original Title"),
    )

    updated = await service.update_appointment(
        sample_profile.user_id,
        created.appointment_id,
        AppointmentCreate(title="Updated Title", remind_enabled=False),
    )

    assert updated.title == "Updated Title"
    assert updated.remind_enabled is False


@pytest.mark.asyncio
async def test_update_appointment_unauthorized(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    # Create appointment by profile 1
    created = await service.create_appointment(
        sample_profile.user_id,
        sample_group.group_id,
        AppointmentCreate(title="Original Title"),
    )

    # Create another profile
    profile2 = Profile(profile_id="profile-2", user_id=2, nickname="User 2")
    tenant_db.add(profile2)
    await tenant_db.commit()

    # Try to update by profile 2
    with pytest.raises(HTTPException) as exc:
        await service.update_appointment(
            profile2.user_id,
            created.appointment_id,
            AppointmentCreate(title="Hacked Title"),
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_appointment(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    created = await service.create_appointment(
        sample_profile.user_id,
        sample_group.group_id,
        AppointmentCreate(title="To Delete"),
    )

    await service.delete_appointment(sample_profile.user_id, created.appointment_id)

    # Verify deleted
    with pytest.raises(HTTPException) as exc:
        await service.get_appointment(created.appointment_id)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_appointment_unauthorized(tenant_db, sample_profile, sample_group):
    service = SocialService(tenant_db)

    # Create appointment by profile 1
    created = await service.create_appointment(
        sample_profile.user_id,
        sample_group.group_id,
        AppointmentCreate(title="Protected Appt"),
    )

    # Create another profile
    profile2 = Profile(profile_id="profile-2", user_id=2, nickname="User 2")
    tenant_db.add(profile2)
    await tenant_db.commit()

    # Try to delete by profile 2
    with pytest.raises(HTTPException) as exc:
        await service.delete_appointment(profile2.user_id, created.appointment_id)

    assert exc.value.status_code == 403
