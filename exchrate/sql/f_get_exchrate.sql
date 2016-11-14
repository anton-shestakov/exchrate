use FRD
go
IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'f_get_exchrate' AND type = 'FN' AND uid = USER_ID('dbo'))
	DROP FUNCTION f_get_exchrate
GO
CREATE FUNCTION f_get_exchrate
(
 @exchsrc		INT
,@fromcurr		INT
,@tocurr		INT
,@exchdate		DATE
)
RETURNS NUMERIC(35, 15)
AS
BEGIN
	
	DECLARE @exchrate NUMERIC(35,15)
	
	SELECT @exchrate = exchrate
	FROM tt_exchrate
	WHERE exchdate = (SELECT MAX(exchdate)
					  FROM tt_exchrate
					  WHERE exchdate <= @exchdate
					  AND   exchsrc = @exchsrc
					  AND   fromcurr = @fromcurr
					  AND   tocurr = @tocurr)
	AND   exchsrc = @exchsrc
	AND fromcurr = @fromcurr
	AND tocurr = @tocurr
	
	/* if exchange rate is not found then try to cross rate thru UAH (980) */
	IF @exchrate IS NULL BEGIN
		SELECT @exchrate = dbo.f_safe_divide(t1.exchrate, t2.exchrate)
		FROM (	SELECT exchrate
				FROM tt_exchrate
				WHERE exchdate = (SELECT MAX(exchdate)
								  FROM tt_exchrate
								  WHERE exchdate <= @exchdate
								  AND   exchsrc = @exchsrc
								  AND   fromcurr = @fromcurr
								  AND   tocurr = 980)
			    AND exchsrc = @exchsrc
			    AND fromcurr = @fromcurr
			    AND tocurr = 980) t1
			 ,(	SELECT exchrate
				FROM tt_exchrate
				WHERE exchdate = (SELECT MAX(exchdate)
								  FROM tt_exchrate
								  WHERE exchdate <= @exchdate
								  AND   exchsrc = @exchsrc
								  AND   fromcurr = @tocurr
								  AND   tocurr = 980)
				AND exchsrc = @exchsrc
			    AND fromcurr = @tocurr
			    AND tocurr = 980) t2
	END
	
	RETURN ISNULL(@exchrate, 0)
	
END
go