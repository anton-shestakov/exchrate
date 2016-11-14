use FRD
GO
/* exchange rate table */
IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'tt_exchrate' AND type = 'U' AND uid = USER_ID('dbo'))
	DROP TABLE tt_exchrate
GO
CREATE TABLE tt_exchrate
(
	 exchdate				datetime			not null /* date of exchange rate */
	,exchsrc				int					not null /* exchange rate source */
	,fromcurr				int					not null /* from currency */
	,tocurr					int					not null /* to currency */
	,exchrate				float						/* exchange rate from fromcurr to tocurr */
	,crdate					datetime			default getdate()		/* timestamp when record was added */
	,PRIMARY KEY(exchdate, exchsrc, fromcurr, tocurr)
)
GO
