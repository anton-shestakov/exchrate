USE FRD
GO
IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'tsp_select_param' AND type = 'P' AND uid = USER_ID('dbo'))
	DROP PROCEDURE tsp_select_param
GO
CREATE PROCEDURE tsp_select_param
 @param_value int
AS
SET NOCOUNT ON
SELECT @param_value
GO