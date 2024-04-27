INSERT INTO auth_user (username, first_name, last_name, email, password)
SELECT username, first_name, last_name, email, password
FROM register_accountholder
WHERE username NOT IN (SELECT username FROM auth_user);
