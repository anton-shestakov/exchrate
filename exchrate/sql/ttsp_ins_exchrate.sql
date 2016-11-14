USE FRD
GO
IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'ttsp_ins_exchrate' AND type = 'P' AND uid = USER_ID('dbo'))
	DROP PROCEDURE ttsp_ins_exchrate
GO
CREATE PROCEDURE ttsp_ins_exchrate
 @exchrates xml
,@updexisting	char(1) = 'N'
,@rows_affected int out
AS

	SET NOCOUNT ON
	SET XACT_ABORT ON
	
	DECLARE @err int
	
	BEGIN TRY
	
		CREATE TABLE #tmp_exchrate
		(
		 exchdate		datetime
		,exchsrc		int
		,fromcurr		int
		,tocurr			int
		,exchrate		numeric(35,15)
		)
		
		BEGIN TRANSACTION
		
		
		INSERT #tmp_exchrate
		SELECT T.c.value('exchDate[1]', 'date') as exchdate
		      ,T.c.value('exchSource[1]', 'int') as exchsrc
			  ,T.c.value('fromCurr[1]', 'int') as fromcurr
			  ,T.c.value('toCurr[1]', 'int') as tocurr
			  ,T.c.value('exchRate[1]', 'numeric(35,15)') as exchrate
		FROM @exchrates.nodes('/exchRates/exchRate') T(c)
		
		
		IF @updexisting = 'Y' BEGIN
			DELETE tt_exchrate
			FROM   #tmp_exchrate t
			      ,tt_exchrate e
			WHERE  t.exchdate = e.exchdate
			AND	   t.exchsrc = e.exchsrc
			AND    t.fromcurr = e.fromcurr
			AND	   t.tocurr = e.tocurr
		END 
		ELSE BEGIN
			DELETE #tmp_exchrate
			FROM   #tmp_exchrate t
			      ,tt_exchrate e
			WHERE  t.exchdate = e.exchdate
			AND	   t.exchsrc = e.exchsrc
			AND    t.fromcurr = e.fromcurr
			AND	   t.tocurr = e.tocurr			
		END
		
		INSERT tt_exchrate
		(
		 exchdate
		,exchsrc
		,fromcurr
		,tocurr
		,exchrate
		)
		SELECT exchdate
		      ,exchsrc
		      ,fromcurr
		      ,tocurr
		      ,exchrate
		FROM #tmp_exchrate
		
		SET @rows_affected = @@ROWCOUNT
		
		COMMIT TRANSACTION
	END TRY
	
	BEGIN CATCH
		SELECT @err = @@ERROR
		IF @@TRANCOUNT != 0 ROLLBACK TRAN
		/* log error to audit table */
	END CATCH

GO