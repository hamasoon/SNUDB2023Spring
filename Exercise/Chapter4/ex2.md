> Write the following queries in SQL: 
> <br>
> a. Display a list of all instructors, showing each instructor's ID and the number of sections
> taught. Make sure to show the number of sections as 0 for instuctors who have not taught any
> section. Your query should use an outer join, and should not use subqueries. <br>
> b. Write the same query as in part a, but using a scalar subquery and not using outer join. <br>
> c. Display the list of all course sections offered in Spring 2018, along with the ID and name
> of each instructor teaching the section. If a section has more than one instructor, that section
> should appear as many times in the result as it has instructors. If a section does not have 
> any instructor, it should still appear in the result with the instructor name set to "-". <br>
> d. Display the list of all departments, with the total number of instructors, in each department,
> without using subqueries. Make sure to show departments that have no instructors, and list those 
> departments with an instructor count of zero. <br> 

--------------------------------

a. Display a list of all instructors, showing each instructor's ID and the number of sections
taught. Make sure to show the number of sections as 0 for instuctors who have not taught any
section. Your query should use an outer join, and should not use subqueries

```sql
SELECT ID, COUNT(sec_id)
FROM instructor AS I LEFT OUTER JOIN teaches AS T USING (ID)
GROUP BY ID
```

The above query should not be written using COUNT(*) since that would count null values also. 
It could be written using any attribute from _teaches_ which does not occur in _instructor_, 
which would be correct although it may be confusing to the reader. (Attributes that occur in 
_instructor_ would not be null even if the instructor has not taught any section.)

b. Write the same query as in part a, but using a scalar subquery and not using outerjoin.

```sql
SELECT ID, (
  	SELECT COUNT(sec_id)
	FROM teaches AS T
	WHERE I.ID = T.ID
)
FROM instructor AS I
```

d. Display the list of all departments, with the total number of instructors, in each department,
without using subqueries. Make sure to show departments that have no instructors, and list those 
departments with an instructor count of zero.

```sql
SELECT dept_name, COUNT(ID)
FROM department AS D NATURAL LEFT OUTER JOIN instructor AS I
GROUP BY(dept_name)
```