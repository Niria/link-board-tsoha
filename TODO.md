# Tasklist

## Features
- Link thumbnails
- User thread/reply edit
- User permissions
- Admin user
    - Delete/hide threads
    - Delete/hide replies
    - Create/hide category
    - Change category permissions
    - Grant/revoke user access permissions
    - Grant/revoke user posting permissions
- User profile page
    - Public/private and if profile private hide user from follower lists?
    - Profile tab (bio, like/follower count, registration date)
    - Followers tab
- User favourite categories
- User followers/following
- Thread search


## Technical
- Make sure display_name is shown instead of username
- Form input validation
- Better error handling via flash messages
- Project file structure cleanup
- DB indexing
- Combine thread page queries (thread, replies) into one query
- Likes/comments db count with aggregate instead of subquery
- Combine index and category templates?
- Clean up reply_like route, thread_id seems so unecessary
- Display weeks/months instead of days for submission age?


## Style
- Reply tree links/chains between parent-child
- Go through css classes and combine them if possible
- Transitions 

