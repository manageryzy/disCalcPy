<?php
	//此文件是根据类名和对象参数加载对象的东西。和typecho的设计很像，应该说根本就是参考typecho做的
	
	if(!defined('IN_SERVER')){
		echo 'Access denied!!!';
		die;
	}
	
	class loadclass_helper{
		//已经加载的类
		protected static $_loaded_class = array('core');
		
		//已经加载的对象
		protected static $_obj_pool = array();
		
		//从包数组获得类名
		static function getClassName($packageArray){
			if(sizeof($packageArray) == 0)
				throw new Exception('object packageArray :' + print_r($packageArray,true) + ' is not acceptable');
				
			$res = '';
			
			for($i = sizeof($packageArray)-1;$i>0;$i--){
				$res = $res.$packageArray[$i].'_';
			}

			return $res.$packageArray[0];
		}
		
		//从包数组获得包路径
		static function getClassPath($packageArray){
			if(sizeof($packageArray) == 0)
				throw new Exception('object packageArray :' + print_r($packageArray,true) + ' is not acceptable');
			
			$res = './src';
			
			for($i = sizeof($packageArray)-1;$i>=0;$i--){
				$res = $res.'/'.$packageArray[$i];
			}
			
			return $res.'.php';
		}
		
		//从对象字符串获得包数组
		static function getPackageArray($package){
			$package = strtolower($package);
			return explode('_',$package);
		}
 
 		//对象池中没有对象就在这里创建
 		protected static function _newObj($objString){
			$className = substr($objString,0,strpos($objString,'@'));
			$packageArray = self::getPackageArray($objString);
			 
			//检测文件是否被加载过，如果没加载则读入
			if(!isset(self::$_loaded_class[$className])){
				require(self::getClassPath($packageArray));
				$_loaded_class[$className] = true; 
			}
			 
			$obj = new $className($objString);
			
			if($obj == NULL){
				throw new Exception('loadclass_helper::_newObj got NULL at ' + $objString);
			}
			
			self::$_obj_pool[$objString] = $obj;
			return $obj;
		}
		
		//工厂方法
		static function factory($objString){
			if(isset(self::$_obj_pool[$objString])){
				return self::$_obj_pool[$objString];
			}else{
				return self::_newObj($objString);
			}
		}
	}
	
	