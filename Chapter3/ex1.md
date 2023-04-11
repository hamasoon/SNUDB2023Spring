> Write the following queries in SQL, using the university schema. (We suggest you actually run these queries on a database, using the sample data that we  provide on the website of the book, [db-book.com](https://db-book.com). Instructions for setting up a database, and loading sample data, are provided on the above website.)

a. Find the titles of courses in the Comp. Sci. department that have 3 credits. <br>

```sql
SELECT title
FROM courses
WHERE dept_name = "Comp. Sci" and credits = 3;
```
b. Find the IDs of all students who were taught by an instructor named Einstein; make sure there are no duplicates in the result. <br>

```sql
SELECT DISTINCT takes.ID
FROM takes, instructor, teaches
WHERE takes.course_id = teaches.course_id AND 
    takes.sec_id = teaches.sec_id AND 
    takes.semester = teaches.semester AND 
    takes.year = teaches.year AND 
    teaches.id = instructor.id AND 
    instructor.name = 'Einstein'
```
c. Find the highest salary of any instructor. <br>
```sql
SELECT MAX(salary)
FROM instructor
```
d. Find all instructors earning the highest salary (there may be more than one with the same salary). <br>
```sql
SELECT id, name
FROM instructor
WHERE salary = (SELECT MAX(salary)
                FROM instructor)
```
e. Find the enrollment of each section that was offered in Fall 2017. <br> 
```sql
SELECT course_id, sec_id, COUNT(id)
FROM takes
WHERE semester = 'Fall' AND year = 2017
GROUP BY course_id, sec_id
```
f. Find the maxium enrollment, across all sections, in Fall 2017. <br>
```sql
SELECT MAX(enrollment)
FROM (SELECT course_id, sec_id, MAX(COUNT(id))
FROM takes
WHERE semester = 'Fall' AND year = 2017
GROUP BY course_id, sec_id) as enrollment
```
g. Find the sections that had the maximum enrollment in Fall 2017. <br>