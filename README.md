# Data Management MIS281N mid-term project

DDL:

```
CREATE TABLE users (
        id INTEGER NOT NULL, 
        username VARCHAR(255) NOT NULL, 
        password VARCHAR(255) NOT NULL, 
        admin BOOLEAN NOT NULL, 
        PRIMARY KEY (id), 
        UNIQUE (username)
)

CREATE TABLE giftables (
        userid INTEGER NOT NULL, 
        balance INTEGER NOT NULL, 
        PRIMARY KEY (userid), 
        FOREIGN KEY(userid) REFERENCES users (id)
)

CREATE TABLE redeemables (
        userid INTEGER NOT NULL, 
        balance BIGINT NOT NULL, 
        PRIMARY KEY (userid), 
        FOREIGN KEY(userid) REFERENCES users (id)
)

CREATE TABLE gifts (
        id INTEGER NOT NULL, 
        giverid INTEGER NOT NULL, 
        receiverid INTEGER NOT NULL, 
        date DATETIME NOT NULL, 
        amount INTEGER NOT NULL, 
        message VARCHAR(255), 
        PRIMARY KEY (id), 
        FOREIGN KEY(giverid) REFERENCES users (id), 
        FOREIGN KEY(receiverid) REFERENCES users (id)
)

CREATE TABLE redemptions (
        id INTEGER NOT NULL, 
        userid INTEGER NOT NULL, 
        date DATETIME NOT NULL, 
        cards INTEGER NOT NULL, 
        PRIMARY KEY (id), 
        FOREIGN KEY(userid) REFERENCES users (id)
)
```
