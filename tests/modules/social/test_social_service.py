import pytest
from sqlalchemy import select
from fastapi import HTTPException

from app.modules.profile.models import Profile
from app.modules.social.models import Connection
from app.modules.social.schemas import SocialPostCreate, CommentCreate
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
        user_id=1, full_name="Test User", slug="test-user", bio="Hello world"
    )
    tenant_db.add(profile)
    await tenant_db.commit()
    await tenant_db.refresh(profile)
    return profile


@pytest.fixture
async def friend_profile(tenant_db):
    """Create a friend profile directly in tenant DB."""
    profile = Profile(user_id=2, full_name="Friend User", slug="friend-user")
    tenant_db.add(profile)
    await tenant_db.commit()
    await tenant_db.refresh(profile)
    return profile


# --- Tests ---


@pytest.mark.asyncio
async def test_create_post(tenant_db, sample_profile):
    service = SocialService(tenant_db)
    data = SocialPostCreate(content="Hello world", privacy="public")

    post = await service.create_post(sample_profile.user_id, data)

    assert post.id is not None
    assert post.profile_id == sample_profile.id
    assert post.content == "Hello world"
    assert post.privacy == "public"


@pytest.mark.asyncio
async def test_get_feed_empty(tenant_db, sample_profile):
    service = SocialService(tenant_db)
    posts = await service.get_feed(sample_profile.user_id)
    assert len(posts) == 0


@pytest.mark.asyncio
async def test_get_feed_own_posts(tenant_db, sample_profile):
    service = SocialService(tenant_db)
    # Create a post
    data = SocialPostCreate(content="My Post", privacy="public")
    await service.create_post(sample_profile.user_id, data)

    posts = await service.get_feed(sample_profile.user_id)
    assert len(posts) == 1
    assert posts[0].content == "My Post"


@pytest.mark.asyncio
async def test_get_feed_with_friend(tenant_db, sample_profile, friend_profile):
    service = SocialService(tenant_db)

    # 1. Create connection
    conn = Connection(
        requester_id=sample_profile.id, receiver_id=friend_profile.id, status="accepted"
    )
    tenant_db.add(conn)
    await tenant_db.commit()

    # 2. Friend creates a post
    friend_post = SocialPostCreate(content="Friend Post", privacy="friends")
    await service.create_post(friend_profile.user_id, friend_post)

    # 3. Friend creates a private post (should not see)
    private_post = SocialPostCreate(content="Secret Post", privacy="private")
    await service.create_post(friend_profile.user_id, private_post)

    # 4. Get Feed
    posts = await service.get_feed(sample_profile.user_id)

    # Expect only the "Friend Post"
    assert len(posts) == 1
    assert posts[0].content == "Friend Post"
    assert posts[0].profile_id == friend_profile.id


@pytest.mark.asyncio
async def test_like_post(tenant_db, sample_profile):
    service = SocialService(tenant_db)

    # Create post
    data = SocialPostCreate(content="Post to like")
    post = await service.create_post(sample_profile.user_id, data)

    # Like
    liked = await service.like_post(sample_profile.user_id, post.id)
    assert liked is True

    # Check state
    # Reload post to check likes count/relationship if modeled, but here we check return value first
    # Or check DB directly
    # Re-like (Unlike)
    liked = await service.like_post(sample_profile.user_id, post.id)
    assert liked is False


@pytest.mark.asyncio
async def test_comment_post(tenant_db, sample_profile):
    service = SocialService(tenant_db)

    # Create post
    data = SocialPostCreate(content="Post to comment")
    post = await service.create_post(sample_profile.user_id, data)

    # Comment
    comment_data = CommentCreate(content="Nice post!")
    comment = await service.comment_post(sample_profile.user_id, post.id, comment_data)

    assert comment.id is not None
    assert comment.content == "Nice post!"
    assert comment.post_id == post.id
    assert comment.author_id == sample_profile.id


@pytest.mark.asyncio
async def test_delete_post(tenant_db, sample_profile):
    service = SocialService(tenant_db)
    data = SocialPostCreate(content="To delete")
    post = await service.create_post(sample_profile.user_id, data)

    await service.delete_post(sample_profile.user_id, post.id)

    # Verify deleted
    with pytest.raises(HTTPException) as exc:
        await service.get_post(post.id)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_unauthorized(tenant_db, sample_profile, friend_profile):
    service = SocialService(tenant_db)
    data = SocialPostCreate(content="Friend's post")
    # Friend creates post
    post = await service.create_post(friend_profile.user_id, data)

    # User tries to delete
    with pytest.raises(HTTPException) as exc:
        await service.delete_post(sample_profile.user_id, post.id)
    assert exc.value.status_code == 403
