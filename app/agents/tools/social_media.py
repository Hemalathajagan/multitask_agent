import httpx
import logging

logger = logging.getLogger(__name__)


async def post_to_instagram(image_url: str, caption: str) -> str:
    """Post an image to Instagram using the Meta Graph API.

    Args:
        image_url: Public URL of the image to post.
        caption: Caption text for the Instagram post.
    """
    try:
        from app.config import get_settings
        settings = get_settings()

        if not settings.instagram_access_token or not settings.instagram_business_account_id:
            return "Error: Instagram API credentials not configured. Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID in .env"

        account_id = settings.instagram_business_account_id
        token = settings.instagram_access_token

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Create media container
            create_resp = await client.post(
                f"https://graph.facebook.com/v18.0/{account_id}/media",
                params={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": token,
                }
            )
            create_data = create_resp.json()
            if "error" in create_data:
                return f"Instagram API error: {create_data['error'].get('message', 'Unknown error')}"

            container_id = create_data.get("id")
            if not container_id:
                return f"Failed to create media container: {create_data}"

            # Step 2: Publish the container
            publish_resp = await client.post(
                f"https://graph.facebook.com/v18.0/{account_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": token,
                }
            )
            publish_data = publish_resp.json()
            if "error" in publish_data:
                return f"Instagram publish error: {publish_data['error'].get('message', 'Unknown error')}"

            post_id = publish_data.get("id", "unknown")
            logger.info(f"Instagram post published: {post_id}")
            return f"Successfully posted to Instagram! Post ID: {post_id}"

    except Exception as e:
        return f"Failed to post to Instagram: {str(e)}"


async def post_to_twitter(text: str) -> str:
    """Post a tweet to Twitter/X using the Twitter API v2.

    Args:
        text: The tweet text (max 280 characters).
    """
    try:
        from app.config import get_settings
        settings = get_settings()

        if not settings.twitter_api_key or not settings.twitter_access_token:
            return "Error: Twitter API credentials not configured. Set TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET in .env"

        import hashlib
        import hmac
        import time
        import base64
        import urllib.parse
        import uuid

        # OAuth 1.0a signature
        method = "POST"
        url = "https://api.twitter.com/2/tweets"
        oauth_nonce = uuid.uuid4().hex
        oauth_timestamp = str(int(time.time()))

        oauth_params = {
            "oauth_consumer_key": settings.twitter_api_key,
            "oauth_nonce": oauth_nonce,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": oauth_timestamp,
            "oauth_token": settings.twitter_access_token,
            "oauth_version": "1.0",
        }

        # Create signature base string (OAuth 1.0a)
        sorted_params = "&".join(f"{k}={urllib.parse.quote(v, safe='')}" for k, v in sorted(oauth_params.items()))
        base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
        signing_key = f"{urllib.parse.quote(settings.twitter_api_secret, safe='')}&{urllib.parse.quote(settings.twitter_access_token_secret, safe='')}"

        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        ).decode()

        oauth_params["oauth_signature"] = signature
        auth_header = "OAuth " + ", ".join(
            f'{k}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(oauth_params.items())
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={"text": text[:280]},
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                }
            )
            data = response.json()

            if response.status_code in (200, 201):
                tweet_id = data.get("data", {}).get("id", "unknown")
                logger.info(f"Tweet posted: {tweet_id}")
                return f"Successfully posted to Twitter! Tweet ID: {tweet_id}"
            else:
                error_msg = data.get("detail", data.get("title", str(data)))
                return f"Twitter API error ({response.status_code}): {error_msg}"

    except Exception as e:
        return f"Failed to post to Twitter: {str(e)}"


async def post_to_linkedin(text: str) -> str:
    """Post a text update to LinkedIn using the UGC API.

    Args:
        text: The post content text.
    """
    try:
        from app.config import get_settings
        settings = get_settings()

        if not settings.linkedin_access_token or not settings.linkedin_person_id:
            return "Error: LinkedIn API credentials not configured. Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID in .env"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.linkedin.com/v2/ugcPosts",
                json={
                    "author": f"urn:li:person:{settings.linkedin_person_id}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": text},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                },
                headers={
                    "Authorization": f"Bearer {settings.linkedin_access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                }
            )

            if response.status_code in (200, 201):
                post_id = response.headers.get("x-restli-id", "unknown")
                logger.info(f"LinkedIn post published: {post_id}")
                return f"Successfully posted to LinkedIn! Post ID: {post_id}"
            else:
                data = response.json()
                error_msg = data.get("message", str(data))
                return f"LinkedIn API error ({response.status_code}): {error_msg}"

    except Exception as e:
        return f"Failed to post to LinkedIn: {str(e)}"


async def post_to_facebook(message: str) -> str:
    """Post a message to a Facebook Page using the Graph API.

    Args:
        message: The post content text.
    """
    try:
        from app.config import get_settings
        settings = get_settings()

        if not settings.facebook_access_token or not settings.facebook_page_id:
            return "Error: Facebook API credentials not configured. Set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://graph.facebook.com/v18.0/{settings.facebook_page_id}/feed",
                params={
                    "message": message,
                    "access_token": settings.facebook_access_token,
                }
            )
            data = response.json()

            if "error" in data:
                return f"Facebook API error: {data['error'].get('message', 'Unknown error')}"

            post_id = data.get("id", "unknown")
            logger.info(f"Facebook post published: {post_id}")
            return f"Successfully posted to Facebook! Post ID: {post_id}"

    except Exception as e:
        return f"Failed to post to Facebook: {str(e)}"
