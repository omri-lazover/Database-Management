CREATE VIEW TotalOrders as
(SELECT *
FROM RecordOrders RO
UNION
SELECT *
FROM RecordReturns RR);



CREATE VIEW maxDuration as
SELECT genre, max(duration) AS maxDuration
FROM Programs P inner join RecordReturns PR on P.title = PR.title
    inner join Households H on H.hID = PR.hID
WHERE P.genre like 'A%' and H.ChildrenNum=0
GROUP BY P.genre;


CREATE VIEW MaxDurationTitle as
SELECT DISTINCT P.title
FROM Programs P inner join RecordReturns RR on P.title = RR.title
inner join Households H on H.hID = RR.hID inner join maxDuration mD on P.genre = mD.genre
WHERE mD.maxDuration=P.duration and ChildrenNum=0;

CREATE VIEW GoodGrade as
SELECT PR.title, PR.hID, PR.rank
FROM ProgramRanks PR, RecordReturns RR
WHERE PR.hID=RR.hID and PR.title=RR.title
UNION
SELECT PR.title, PR.hID, PR.rank
FROM ProgramRanks PR, RecordOrders RO
WHERE PR.hID=RO.hID and PR.title=RO.title;

--count how much good grades there are for each program
CREATE VIEW GoodGradesCount as
SELECT GG.title, count(GG.rank) as RankNum
FROM GoodGrade GG
GROUP BY GG.title;

--programs with at least 3 good grades
CREATE VIEW EnoughGoodGrades as
SELECT title
FROM GoodGradesCount GGC
WHERE RankNum>=3;

CREATE VIEW tenOrMoreOrders as
SELECT P.title, count(DISTINCT RR.hID) as familiesOrdered
FROM Programs P inner join RecordReturns RR on P.title = RR.title
inner join Households H on H.hID = RR.hID
GROUP BY P.title
HAVING count(DISTINCT RR.hID)>=10;


--more than half the families that returned have at least 8 wealth

CREATE VIEW RichFamilies as
SELECT hID
FROM Households H
WHERE netWorth>=8;

--how much rich families returned each movie
CREATE VIEW RichFamiliesReturned as
SELECT RR.title, count(DISTINCT RR.hID) as RichReturned
FROM RecordReturns RR, RichFamilies RF, tenOrMoreOrders TMO
WHERE RR.hID= RF.hID and TMO.title=RR.title
GROUP BY RR.title;

--how much families returned each movie
CREATE VIEW TotalReturned as
SELECT RR.title, count(DISTINCT RR.hID) as TotalReturns
FROM RecordReturns RR, Households H, tenOrMoreOrders TMO
WHERE RR.hID= H.hID and TMO.title=RR.title
GROUP BY RR.title;






