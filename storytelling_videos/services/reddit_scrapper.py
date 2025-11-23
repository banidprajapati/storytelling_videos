import praw

from storytelling_videos.core.config_core import settings

reddit = praw.Reddit(
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    user_agent=settings.USER_AGENT,
)
sub_reddits = ["technews"]

for name in sub_reddits:
    sub = reddit.subreddit(name)

    for post in sub.hot(limit=5):
        print(f"[{name}] TITLE: {post.title}")
        print(f"[{name}] URL: {post.url}")

        if post.selftext:
            print(f"[{name}] BODY: {post.selftext}")

        post.comments.replace_more(limit=0)

        for comment in post.comments.list():
            print(f"[{name}] COMMENT: {comment.body}")
        print("-" * 80)
