-- import database
create database db_theatre1;

use db_theatre1;

set foreign_key_checks=0;

create table halls (hall_id int, class varchar(10), no_of_seats int, primary key(hall_id,class));

create table movies (movie_id int primary key, movie_name varchar(40), length int, language varchar(10), show_start date, show_end date);

create table price_listing (price_id int primary key, type varchar(3), day varchar(10), price int);

create table shows (show_id int primary key, movie_id int, hall_id int, type varchar(3), time int, Date date, price_id int, 
	foreign key(movie_id) references movies(movie_id), foreign key(hall_id) references halls(hall_id), foreign key(price_id) references price_listing(price_id) on update cascade);


create table types(movie_id int primary key,type1 varchar(3),type2 varchar(3),type3 varchar(3),
	foreign key(movie_id) references movies(movie_id) on delete cascade);  

create table booked_tickets (ticket_no int, show_id int, seat_no int,staff_id int, primary key(ticket_no,show_id,staff_id), 
	foreign key(show_id) references shows(show_id) on delete cascade, foreign key(staff_id) references staffs(staff_id) on delete cascade);

create table staffs (staff_id int primary key, staff_name varchar(40), date_of_birth date, gender varchar(10), citizen_id int, position varchar(20), phone_number int, email varchar(40), staff_address varchar(50), staff_salary varchar(20));

create table members (member_id int primary key, member_name varchar(40), date_of_birth date, gender varchar(10), citizen_id int,  phone_number int, email varchar(40), member_type varchar(20));

desc halls;
desc movies;
desc price_listing;
desc shows;
desc booked_tickets;

set foreign_key_checks=1;

insert into halls values
(1, "gold", 20), 
(1, "standard", 55), 
(2, "gold", 25), 
(2, "standard", 70), 
(3, "gold", 25), 
(3, "standard", 70);

insert into price_listing values
(1, "2D", "Monday", 40000),
(2, "3D", "Monday", 50000),
(3, "4DX", "Monday", 60000),
(4, "2D", "Tuesday", 40000),
(5, "3D", "Tuesday", 50000),
(6, "4DX", "Tuesday", 60000),
(7, "2D", "Wednesday", 35000),
(8, "3D", "Wednesday", 45000),
(9, "4DX", "Wednesday", 55000),
(10, "2D", "Thursday", 40000),
(11, "3D", "Thursday", 50000),
(12, "4DX", "Thursday", 60000),
(13, "2D", "Friday", 40000),
(14, "3D", "Friday", 50000),
(15, "4DX", "Friday", 60000),
(16, "2D", "Saturday", 50000),
(17, "3D", "Saturday", 60000),
(18, "4DX", "Saturday", 70000),
(19, "2D", "Sunday", 50000),
(20, "3D", "Sunday", 60000),
(21, "4DX", "Sunday", 70000);

select * from halls;
select * from price_listing;

delimiter //

create trigger get_price
after insert on halls
for each row
begin

UPDATE shows s, price_listing p 
SET s.price_id=p.price_id 
WHERE p.price_id IN 
(SELECT price_id 
FROM price_listing p 
WHERE dayname(s.Date)=p.day AND s.type=p.type);

end; //

delimiter ;

delimiter //

create procedure delete_old()
begin

	declare curdate date;
set curdate=curdate();

DELETE FROM shows 
WHERE datediff(Date,curdate)<-7;

DELETE FROM shows 
WHERE movie_id IN 
(SELECT movie_id 
FROM movies
WHERE datediff(show_end,curdate)<-7);

DELETE FROM movies 
WHERE datediff(show_end,curdate)<-7;

end; //

delimiter ;
