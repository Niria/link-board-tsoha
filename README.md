# Link Board | Tsoha

Link Board is an app where users can post links to news, articles and pictures. Links 
submitted by users start a new discussion thread where other users can participate. The board 
is divided into categories for all the various topics and each link submission belongs to one
of these categories.


## Planned Features

- [x] User can create an account, sign in and out
- [ ] User can edit their profile
- [ ] User profiles can be set to either public or private
- [x] User can view public profiles of other users
- [x] Threads and replies submitted by users can be seen on their profile page
- [x] User can view all the public discussion threads on the home page
- [x] User can select categories to filter threads to their liking
- [x] User can write messages in threads as a reply to another message or the main post
- [x] User can post links and create new threads accompanying them
- [x] User can like threads and replies
- [x] User can edit the title and content of their own threads
- [x] User can edit the content of their replies
- [x] User can choose favourite categories
- [x] User can follow other users
- [ ] User can search thread titles and messages using a keyword search function
- [x] Admin can create new public and private categories for links
- [x] Admin can grant/revoke private category access permissions for users
- [x] Admin can edit and hide/soft delete threads/messages submitted by users

Ticked features in the list above have been implemented. Check `TODO.md` for up to date tasklist.


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

The testdata scripts include one admin user and 4 normal users:

| username | password | role  |
|----------|----------|-------|
| user1    | password | admin | 
| user2    | password | user  |
| user3    | password | user  |
| user4    | password | user  |
| user5    | password | user  |