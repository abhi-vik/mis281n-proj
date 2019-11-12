DROP PROCEDURE IF EXISTS giftpoints;

$$

CREATE PROCEDURE giftpoints(IN giverid INTEGER, IN receiverid INTEGER, IN amount INTEGER, IN message VARCHAR(255))
BEGIN

UPDATE giftables set balance=(balance-amount) WHERE userid = giverid;

UPDATE redeemables set balance=(balance+amount) WHERE userid = receiverid;

INSERT INTO gifts (giverid, receiverid, date, amount, message) VALUES (giverid, receiverid, NOW(), amount, message);
END;

$$

CREATE OR REPLACE VIEW MONTH_POINT_USAGE AS
SELECT GivenOut.MONTH, GivenOut.YEAR, SUM(GivenOut.GIVEN_OUT) AS MONTH_GIVEN_OUT, SUM(CashedIn.CASHED_IN) AS MONTH_CASHED_IN
FROM
((SELECT giverid, SUM(amount) AS GIVEN_OUT, MONTH(date) AS MONTH, YEAR(date) AS YEAR
  FROM gifts
  GROUP BY giverid, MONTH(date), YEAR(date)) AS GivenOut
JOIN
 (SELECT receiverid, SUM(amount) AS CASHED_IN, MONTH(date) AS MONTH, YEAR(date) AS YEAR
 FROM gifts
 GROUP BY receiverid, MONTH(date), YEAR(date)) AS CashedIn
ON GivenOut.giverid = CashedIn.receiverid)
GROUP BY GivenOut.MONTH, GivenOut.YEAR
ORDER BY GivenOut.YEAR, GivenOut.MONTH asc;

$$

CREATE OR REPLACE VIEW USER_POINT_USAGE AS
SELECT users.username, GivenOut.GIVEN_OUT, CashedIn.CASHED_IN
FROM users JOIN
((SELECT giverid, SUM(amount) AS GIVEN_OUT
  FROM gifts
  GROUP BY giverid) AS GivenOut
JOIN
 (SELECT receiverid, SUM(amount) AS CASHED_IN
 FROM gifts
 GROUP BY receiverid) AS CashedIn
ON GivenOut.giverid = CashedIn.receiverid)
ON users.id = CashedIn.receiverid
ORDER BY CashedIn.CASHED_IN desc;

$$

CREATE OR REPLACE VIEW NOT_GIVEOUT AS
SELECT users.username, giftables.balance
FROM giftables JOIN users ON giftables.userid = users.id
WHERE balance != 0
ORDER BY balance DESC;

$$

CREATE OR REPLACE VIEW REDEMPTION AS
SELECT redemptions.id AS TRANSACID, redemptions.date AS DATE, CardRedemption.userid AS USERID, CardRedemption.CARDS_REDEMPTION AS CARDS_REDEMPTIONS
FROM redemptions JOIN
(SELECT MONTH(date), userid, SUM(cards) AS CARDS_REDEMPTION
 FROM redemptions
 WHERE MONTH(date) <= TIMESTAMPADD(MONTH, -2, NOW())
 GROUP BY userid, MONTH(date)) AS CardRedemption
ON redemptions.userid = CardRedemption.userid
ORDER BY DATE, USERID;