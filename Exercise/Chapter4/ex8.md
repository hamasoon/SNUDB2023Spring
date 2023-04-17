> As discussed in Section 4.4.8, we expect the constraint "an instructor cannot teach
> sections in two different classrooms in a semester in the same time slot" to hold. 
> <br>
> a. Write an SQL query that returns all (_instructor_, _section_) combinations 
> that violate this constraint. <br>
> b. Write an SQL assertion to enforce this constraint (as discussed in Section 4.4.8, 
> current generation database systems do not support assertions, although they are part 
> of the SQL standard). <br> 

--------------------------------

a. Query: 

```sql
SELECT *
FROM instructor NATURAL JOIN teaches NATURAL JOIN section
GROUP BY (id,name,semester,year,time_slot_id)
HAVING COUNT(DISTINCT (building, room_number)) > 1; 
```