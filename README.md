# Link Board | Tsoha

Link Board is an app where users can post links to news, articles and pictures. Links 
submitted by users start a new discussion thread where other users can participate. The board 
is divided into categories for all the various topics and each link submission belongs to one
of these categories.


## Features

### User can
- [x] Create an account, sign in and out
- [x] Edit their own profile
- [x] Set their profile public or private
- [x] View public profiles of other users
- [x] View threads and replies submitted by users on their profile page
- [x] View all the public discussion threads on the home page
- [x] Select categories to filter threads to their liking
- [x] Search for users, categories and threads
- [x] Submit links which creates a new discussion thread
- [x] Choose to fetch a thumbnail for their link submission
- [x] Write messages in threads as a reply to the thread or another comment
- [x] Edit the link, title, message and thumbnail of their own threads
- [x] Edit their own replies
- [x] Choose favourite categories
- [x] Like threads and replies
- [x] Follow other users which highlights their threads and replies

### Admin can
- [x] Create new public and private categories for links
- [x] Edit category name, description and privacy status
- [x] Grant and revoke private category access permissions for users
- [x] Edit and hide/soft delete threads/messages submitted by users

Check `TODO.md` for up to date tasklist.


## Installation
### Environment
Clone the repository and navigate to it
```
$ git clone git@github.com:Niria/link-board-tsoha.git
$ cd link-board-tsoha/
```

Create an `.env`-file and then add the following content. You can name the database however you wish as long as you use the same name in the database section that follows this part:
```
DATABASE_URI=postgresql:///<new-db-name>
SECRET_KEY=<secret-key>
```

Create a virtual environment and install dependencies:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt
```
If you run into issues when installing `psycopg2` you can try using `psycopg2-binary` instead.


### Database
If postgres isn't already up and running, start it manually or run the following tsoha start-up script:
```
$ start-pg.sh
```

Define the database schema with the following commands:
```
$ psql
user=# CREATE DATABASE <new-db-name>;
user=# \q
$ psql -d <new-db-name> < schema.sql
```

With the schema in place you can insert some data to the database using either `testdata_random.sql` or `testdata_static.sql`. The first one inserts a lot of random data and the second one adds a small amount of fairly static data to the DB. Do **not** use both of them at once:
```
$ psql -d <new-db-name> < testdata_random.sql
```
or:
```
$ psql -d <new-db-name> < testdata_static.sql
```

If you wish to do testing without predefined data you should first register and then update your `user_role` from 0 to 1 to access admin features:
```
$ psql -d <new-db-name> 
user=#\ UPDATE users SET user_role=1 WHERE id=<your-user-id>;
```


You can reset the database with `cleandb.sql`, but be sure to define the **schema** again afterwards:
```
$ psql -d <new-db-name> < cleandb.sql
$ psql -d <new-db-name> < schema.sql
```

You can access the new database with `$ psql -d <new-db-name>` or:
```
$ psql
user=# \c <new-db-name>
```


### Running the app

You can now start the app with:
```
$ flask run
```

## Usage

### Users
The testdata scripts include one admin user and 4 normal users:

| username | password | role  |
|----------|----------|-------|
| user1    | password | admin | 
| user2    | password | user  |
| user3    | password | user  |
| user4    | password | user  |
| user5    | password | user  |
