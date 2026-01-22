import pytest
from fastapi import HTTPException

from app.modules.profile.models import Profile
from app.modules.social.schemas import (
    PostCreate,
    CommentCreate,
    MessageCreate,
    GroupCreate,
)
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
    profile = Profile(
        profile_id="test-profile-1", user_id=1, nickname="Test User", bio="Hello world"
    )
    tenant_db.add(profile)
    await tenant_db.commit()
    await tenant_db.refresh(profile)
    return profile


@pytest.fixture
async def friend_profile(tenant_db):
    """Create a friend profile directly in tenant DB."""
    profile = Profile(profile_id="friend-profile-1", user_id=2, nickname="Friend User")
    tenant_db.add(profile)
    await tenant_db.commit()
    await tenant_db.refresh(profile)
    return profile


# --- Tests ---


@pytest.mark.asyncio
async def test_create_post(tenant_db, sample_profile):
    service = SocialService(tenant_db)
    data = PostCreate(content="Hello world")

    post = await service.create_post(sample_profile.user_id, data)

    assert post.post_id is not None
    assert post.content == "Hello world"


@pytest.mark.asyncio
async def test_get_feed_empty(tenant_db, sample_profile):
    service = SocialService(tenant_db)
    posts = await service.get_feed(sample_profile.user_id)
    assert len(posts) == 0


@pytest.mark.asyncio
async def test_get_feed_own_posts(tenant_db, sample_profile):
    service = SocialService(tenant_db)
    # Create a post
    data = PostCreate(content="My Post")
    await service.create_post(sample_profile.user_id, data)

    posts = await service.get_feed(sample_profile.user_id)
    assert len(posts) == 1
    assert posts[0].content == "My Post"


@pytest.mark.asyncio
async def test_interact_post(tenant_db, sample_profile):
    service = SocialService(tenant_db)

    # Create post
    data = PostCreate(content="Post to like")
    post = await service.create_post(sample_profile.user_id, data)

    # Like
    interaction = await service.interact_post(
        sample_profile.user_id, post.post_id, "like"
    )
    assert interaction.interaction_id is not None

    # Check duplicate
    with pytest.raises(HTTPException) as exc:
        await service.interact_post(sample_profile.user_id, post.post_id, "like")
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_comment_post(tenant_db, sample_profile):
    service = SocialService(tenant_db)

    # Create post
    data = PostCreate(content="Post to comment")
    post = await service.create_post(sample_profile.user_id, data)

    # Comment
    comment_data = CommentCreate(content="Nice post!")
    comment = await service.comment_post(
        sample_profile.user_id, post.post_id, comment_data
    )

    assert comment.comment_id is not None
    assert comment.content == "Nice post!"


@pytest.mark.asyncio
async def test_get_comments(tenant_db, sample_profile):
    service = SocialService(tenant_db)

    # Create post
    data = PostCreate(content="Post")
    post = await service.create_post(sample_profile.user_id, data)

    # Add comments
    comment_data1 = CommentCreate(content="First comment")
    await service.comment_post(sample_profile.user_id, post.post_id, comment_data1)

    comment_data2 = CommentCreate(content="Second comment")
    await service.comment_post(sample_profile.user_id, post.post_id, comment_data2)

    # Get comments
    comments = await service.get_comments(post.post_id)
    assert len(comments) == 2


@pytest.mark.asyncio
async def test_delete_post(tenant_db, sample_profile):
    service = SocialService(tenant_db)
    data = PostCreate(content="To delete")
    post = await service.create_post(sample_profile.user_id, data)

    await service.delete_post(sample_profile.user_id, post.post_id)

    # Verify deleted
    with pytest.raises(HTTPException) as exc:
        await service.get_post(post.post_id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_unauthorized(tenant_db, sample_profile, friend_profile):
    service = SocialService(tenant_db)
    data = PostCreate(content="Friend's post")
    # Friend creates post
    post = await service.create_post(friend_profile.user_id, data)

    # User tries to delete
    with pytest.raises(HTTPException) as exc:
        await service.delete_post(sample_profile.user_id, post.post_id)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_create_group(tenant_db, sample_profile):
    service = SocialService(tenant_db)

    group = await service.create_group(sample_profile.user_id, GroupCreate())

    assert group.group_id is not None
    assert group.profile_id == sample_profile.profile_id


@pytest.mark.asyncio
async def test_send_message(tenant_db, sample_profile):
    service = SocialService(tenant_db)

    msg_data = MessageCreate(content="Hello", receiver_id="some-receiver")
    msg = await service.send_message(sample_profile.user_id, msg_data)

    assert msg.message_id is not None
    assert msg.content == "Hello"
