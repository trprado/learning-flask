drop table if exists user;
drop table if exists post;

create table user (
    id integer primary key autoincrement,
    email text unique not null,
    password text not null,
    name text not null,
    created timestamp not null default current_timestamp
);

create table post (
    id integer primary key autoincrement,
    user_id integer not null,
    title text not null,
    body text not null,
    created timestamp not null default current_timestamp,
    foreign key (user_id) references user(id)
);