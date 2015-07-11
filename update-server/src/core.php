<?php
	if(!defined('IN_SERVER')){
		echo 'Access denied!!!';
		die;
	}
	
	require('helper/loadclass.php');
	
	class Core{
		var $router;
		
		function Core(){
			if(!defined('DB_INITED')){
				echo 'Database not inited!';
				die;
			}
			
			loadclass_helper::init();
		}
		
		//注册API应用程序的路由
		function regApiRouter(){
			$this->router = array(
				//注册计算节点，只是方便管理和统计
				'reg' => 'reg_api_slave_widget@',
				//计算节点的主控程序获得控制信息
				'getCommand' => 'getCommand_api_slave_widget@',
			);
		}
		
		//注册管理页面的路由
		public function regAdminRouter(){
			$this->router = array(
			);
		}
		
		//分发路由
		public function dispatch(){
			if(!isset($_REQUEST['do'])){
				echo 'Access denied!!!';
				die;
			}
			
			if(isset($this->router[$_REQUEST['do']])){
				loadclass_helper::factory($this->router[$_REQUEST['do']]).dispatch();
			}else{
				echo 'Unkown method';
				die;
			}
		}
	}
?>