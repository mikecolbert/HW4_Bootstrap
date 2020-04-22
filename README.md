# HW4 - WTForms
Using WTForms with Flask to create a web form.


```
USE msci3300;

DROP TABLE IF EXISTS `colbert_friends`;

CREATE TABLE colbert_friends (
friendid int(11) NOT NULL AUTO_INCREMENT,
first_name varchar(255),
last_name varchar(255), 
PRIMARY KEY (`friendid`)) ENGINE=InnoDB AUTO_INCREMENT=1;

INSERT INTO colbert_friends (first_name, last_name) VALUES ('Mike', 'Colbert');

SELECT * FROM colbert_friends;
```
