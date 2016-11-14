USE FRD
GO
IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'tsp_return_param' AND type = 'P' AND uid = USER_ID('dbo'))
	DROP PROCEDURE tsp_return_param
GO
CREATE PROCEDURE tsp_return_param
 @param_value_in int
,@param_value_out int out
AS
SET NOCOUNT ON
SET @param_value_out = @param_value_in
GO