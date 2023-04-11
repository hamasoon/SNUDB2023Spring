Terms
-----
### 1. Integrity Constraints
- Integrity


### 2.

Operartions
-----------
- Create Table
```sql
CREATE TABLE student(
    ID          CHAR(5),
    name        VARCHAR(20) NOT NULL,
    dept_name   VARCHAR(20),
    salary      NUMERIC(8, 2),
    PRIMARY KEY(ID),
    FOREIGN KEY(dept_name) REFERENCES department
)

CREATE TABLE movie_revenue (
    mov_id    INT,
    revenue   INT,
    FOREIGN KEY (mov_id) REFERENCES movie(mov_id)
)

CREATE TABLE teaches(
    ID	    		varchar(5), 
	course_id		varchar(8),
	sec_id			varchar(8), 
	semester		varchar(6),
	year			numeric(4,0),
	primary key (ID, course_id, sec_id, semester, year),
	foreign key (course_id,sec_id, semester, year) references section
		on delete cascade,
	foreign key (ID) references instructor
	    on delete cascade
	)
```
- select, from, where, rename - so used to... i will skip this
- 