<?php
	define('IN_SERVER',true);
	
	require_once('./mysql.inc.php');
	require_once('./src/core.php');
	

	
	$app = new Core();
	$app->regApiRouter();
	$app->dispatch();
	
?>