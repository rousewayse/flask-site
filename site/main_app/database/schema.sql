PRAGMA foreign_keys=on;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username VARCHAR(32) NOT NULL UNIQUE,
	pass_hash TEXT NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	active BOOLEAN NOT NULL DEFAULT TRUE	
);

DROP TABLE IF EXISTS user_info;

CREATE TABLE user_info (
	user_id INTEGER NOT NULL UNIQUE,
	fst_name VARCHAR(255) NOT NULL,
	snd_name VARCHAR(255) NOT NULL,
	thrd_name VARCHAR(255),
	birth_date DATETIME NOT NULL, 
	email VARCHAR(255) CHECK (email LIKE '_%@_%._%') UNIQUE,
	FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS students;

CREATE TABLE  students (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL UNIQUE,
	group_id INTEGER,
	cource INTEGER NOT NULL DEFAULT 1 CHECK (cource BETWEEN 1 AND 6),
	directory TEXT NOT NULL, 
	degree VARCHAR(255) NOT NULL, 
	form VARCHAR(255) NOT NULL CHECK ( form IN  ('fulltime', 'distant', 'mixed')),
	fee BOOLEAN NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
	FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE SET NULL
);

DROP TABLE IF EXISTS teachers;

CREATE TABLE teachers (
	id INTEGER NOT NULL PRIMARY KEY,
	user_id INTEGER NOT NULL,
	degree VARCHAR(255) NOT NULL,
	faculty_id INTEGER,
	FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
	FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE SET NULL
);

DROP TABLE IF EXISTS groups;

CREATE TABLE groups (
	id INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT,
	title  VARCHAR(255) UNIQUE,
	faculty_id INTEGER,
	FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE SET NULL
);

DROP TABLE IF EXISTS faculty;

CREATE TABLE faculty (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	title VARCHAR(255) NOT NULL UNIQUE
);

DROP TABLE IF EXISTS classes;

CREATE TABLE classes(
	id INTEGER NOT NULL PRIMARY KEY,
	group_id INTEGER NOT NULL,
	teacher_id INTEGER,
	title VARCHAR(255) NOT NULL, 
	FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
	FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
	UNIQUE(group_id, title)
);


DROP TABLE IF EXISTS stuff;

CREATE TABLE stuff(
	id INTEGER NOT NULL PRIMARY KEY,
	user_id INTEGER  NOT NULL,
	FOREIGN KEY (user_id)  REFERENCES user(id) ON DELETE CASCADE
);


