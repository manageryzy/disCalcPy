<?php
	if(!defined('IN_SERVER')){
		echo 'Access denied!!!';
		die;
	}
	
	class Widget{
		var $__OriPara;
		
		function Widget($para = NULL){
			$this->$__OriPara = $para;
		}
		
		function dispose(){
			echo $this->render();
		}
		
		function render(){
			return '<h3>Widget rendered</h3>';
		}
	}