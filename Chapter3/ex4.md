> Consider the insurance database of Figure 3.17, where the primary keys
> are underlined. Construct the following SQL queries for this relational database.

--------------------------------

a. Find the total number of people who owned cars that were involved in accidents in 2017.
<br>

Note: This is not the same as the total number of accidents in 2017. We must count people
with several accidents only once. Furthermore, note that the question asks for owners, 
and it might be that the owner of the car was not the driver actually involved in the 
accident. 

```sql
SELECT COUNT( DISTINCT drive_id)
WHERE accident as a, owns as o, participated as p
FROM a.report_number = p.report_number
    and p.license_plate = o.license_plate
    and a.year = '2017'
```

b. Delete all year-2010 cars belonging to the person whose ID is '12345'.

```sql
```

Note: The _owns_, _accident_ and _participated_ records associated with the 
deleted cars still exist. (If you want the corresponding rows in _owns_ and 
_participated_ to also be deleted you can use **ON CASCADE DELETE** on the schema
of the tables).