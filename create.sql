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
SELECT year(date) AS year,
    month(date) AS month,
    sum(gifts.amount) AS given,
    sum(gifts.amount) AS received
FROM gifts
GROUP BY year, month
ORDER BY year, month asc;

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
WHERE balance > 0
ORDER BY balance DESC;

$$

CREATE OR REPLACE VIEW REDEMPTION AS
SELECT redemptions.date AS DATE, users.username AS USERNAME, CardRedemption.CARDS_REDEMPTION AS CARDS_REDEMPTIONS
FROM redemptions JOIN
  (SELECT MONTH(date), userid, SUM(cards) AS CARDS_REDEMPTION
   FROM redemptions
   WHERE MONTH(date) <= TIMESTAMPADD(MONTH, -2, NOW())
   GROUP BY userid, MONTH(date)) AS CardRedemption
ON redemptions.userid = CardRedemption.userid
JOIN users ON CardRedemption.userid = users.id
ORDER BY DATE, USERNAME;