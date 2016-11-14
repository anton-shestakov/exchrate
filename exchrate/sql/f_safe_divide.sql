use FRD
go
IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'f_safe_divide' AND type = 'FN' AND uid = USER_ID('dbo'))
	DROP FUNCTION f_safe_divide
GO
CREATE FUNCTION f_safe_divide
(
 @num1		NUMERIC(35, 15)
,@num2		NUMERIC(35, 15)
)
RETURNS NUMERIC(35, 15)
AS
BEGIN
	   
	RETURN (CASE WHEN ISNULL(@num2, 0) = 0 THEN 0 ELSE ISNULL(@num1, 0) / @num2 END)
	
	
	
END
go