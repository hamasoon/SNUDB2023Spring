> Consider the bank database of Figure 3.18, where the primary keys are underlined. 
> Construct the following SQL queries for this relational database. 
--------------------------------

a. Find the ID of each customer of the bank who has an account but not a loan.

```sql 
(SELECT ID FROM customer)
EXCEPT
(SELECT ID FROM loan)
```

b. Find the ID of each customer who lives on the same street and in the same city 
as customer '12345'

```sql 
SELECT ID
FROM customer as C1, customer as C2
WHERE C1.customer_street = C2.customer_street and
      C1.customer_city = C2.customer_city and
      C2.ID = '12345'
```

Another method (using **scalar subqueries**)

```sql
SELECT ID 
FROM customer 
WHERE customer_street = (SELECT customer_street FROM customer WHERE ID = '12345') AND 
    customer_city = (SELECT customer_city FROM customer WHERE ID = '12345')
```

c. Find the name of each branch that has at least one customer who has an account
in the bank and who lives in "Harrison".

```sql
SELECT DISTINCT branch_name
FROM account, depositor, customer 
WHERE customer.id = depositor.id AND
    depositor.account_number = account.account_number AND
    customer_city = 'Harrison'
```