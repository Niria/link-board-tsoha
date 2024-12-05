# Tasklist

## Features
- User profile page
    - Public/private and if profile private hide user from follower lists?
    - Profile tab (bio, like/follower count, registration date)
    - Favourite categories tab
- Admin
    - Delete category
- Thread search

## Technical
- Installation
    - Look into psycopg2 install issue
- Database
    - Indexes
    - Check that composite primary keys actually make sense
    - Add error handling for failed DB requests
    - On update trigger to set updated_at timestamp on category, thread, reply and user tables
- Server
    - Fix crash on category creation when name exists
    - Fix crash when all users have permissions
    - Possibly change reply_like route, thread_id seems so unnecessary
    - Double check that user can't access features when they lack permissions
- Form input validation 
    - Whitespace and special characters
    - WTForms?
- Project file structure cleanup
    - Perhaps split content.py into smaller modules
- Code
  - Unify code, single/double quotation marks etc
- Display weeks/months instead of days for submission age?

## Style
- Button click events fail on the edge due to scale transform
- Modify style of forms
- Go through css classes and combine them if possible
- Flash message style adjustment
- Transitions 

