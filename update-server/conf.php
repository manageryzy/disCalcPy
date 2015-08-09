<?php
function GetIP(){
if(!empty($_SERVER["HTTP_CLIENT_IP"])){
  $cip = $_SERVER["HTTP_CLIENT_IP"];
}
elseif(!empty($_SERVER["HTTP_X_FORWARDED_FOR"])){
  $cip = $_SERVER["HTTP_X_FORWARDED_FOR"];
}
elseif(!empty($_SERVER["REMOTE_ADDR"])){
  $cip = $_SERVER["REMOTE_ADDR"];
}
else{
  $cip = "无法获取！";
}
return $cip;
}

$ip = GetIP();
$ip_a = explode('.',$ip);

$ip_a[3] = floor($ip_a[3]/25 + 1);
$ip = join('.',$ip_a);

echo "{\"ip\":\"$ip\",\"port\":8899}"
?>