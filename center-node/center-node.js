var net = require('net');
var fs = require('fs');
var readline = require('readline');

var conf,tasks = [],taskCalc = [],nodes;

taskCalc['len'] = 0;

var deepCopy = function (source) {
  var result = {};
  for (var key in source) {
    result[key] = typeof source[key] ==='object'? deepCopy(source[key]): source[key];
  }
  return result;
}

String.prototype.trim = function () {
  return this.replace(/(^\s*)|(\s*$)/g, "");
}
String.prototype.ltrim = function () {
  return this.replace(/(^\s*)/g, "");
}
String.prototype.rtrim = function () {
  return this.replace(/(\s*$)/g, "");
}

var Nodes = function(){
  var n = Object();
  var nodeMap = [];
  var length = 0;
  
  n.addNode = function(UUID,IP){
    if(typeof(nodeMap[UUID])=='undefined'){
      //new node
      var node = new Object();
      node.ip = IP;
      node.active = Date.now();
      nodeMap[UUID] = node;
      length ++;
    }
    else{
      //update node
      nodeMap[UUID].active = Date.now();
    }
  };
  
  n.clean = function(){
    for(var UUID in nodeMap){
      if((Date.now() - nodeMap[UUID].active)>conf.timeout){
        if(typeof(taskCalc[UUID])!='undefined'){
          console.log('released a tast at ' + UUID + ' @ ' + nodeMap[UUID].ip + ' last active ' + nodeMap[UUID].active);  
          tasks.push(taskCalc[UUID]);
          taskCalc.splice(UUID, 1);    
          taskCalc['len']=taskCalc['len']+1;   
        }
      }
    }
  };
  
  n.length = function(){
    return length;
  };
  
  n.liveCount = function(){
    var count = 0;
    for(var UUID in nodeMap){
      if((Date.now() - nodeMap[UUID].active)/1000 < conf.timeout){
        count++;
      }
    }
    return count;
  };
  
  n.workingCount = function(){
    var count = 0;
    
    for(var UUID in nodeMap){
      if(typeof(taskCalc[UUID])!='undefined'){
        count ++;
      }
    }
    return count;
  };
  
  n.getNode = function(){
    return nodeMap;
  }
  
  return n;
};
nodes = Nodes();

var chatServer = net.createServer();  
chatServer.on('connection', function(socket) {  
  // 1 - text 2 - uuid 3 - length 4 - hex
  var ip = socket.remoteAddress;
  var mode = 1;
  var state = '0';
  var uuid;
  var bufferLength,recvLength = 0;
  // var theBuffer = new Buffer('');
  var fileName = './res/'+(Date.now() / 1000) + '-' + Math.round(Math.random()*10000) +'.res';
  
  var deal = {
    '0':{
      'worker ping':function(){
        socket.write('server ping\n');
        nodes.addNode(uuid,ip);
        return '1';
      },
      'worker finish':function(){
        socket.write('server ping\n');
        return 'save'
      }
    },
    '1':{
      'ok':function(){
        if(tasks.length <= 0 || typeof(taskCalc[uuid])!= 'undefined'){
          socket.write('null\n');
          return '2';
        }
        else{
          var obj = tasks.pop();
          taskCalc[uuid] = obj;
          taskCalc['len']=taskCalc['len']+1;
          var json = JSON.stringify(obj);
          socket.write(json.length + '\n');
          socket.write(json);
          return '2';
        }
      },
    },
    '2':{
      'ok':function(){
        socket.end()
        return '0';
      }
    }
  };
  
  socket.on('data',function(buffer){
    if(mode == 1){
      var clientString = buffer.toString();
      var sp = clientString.split('\n');
      if(typeof(sp[1]) != 'undefined' && sp[1]!=''){
        uuid = sp[1];
      }
      if(typeof(deal[state][sp[0]]) == 'undefined'){
        console.error('undefined deal function!');
        console.error('state: ' + state + 'sp: ' + sp);
        socket.end();
      }
      else{
        var res = deal[state][sp[0]]();
        if(res == 'save'){
          mode = 2;
        }
        else{
          state = res;
        }
      }
    }
    else if(mode == 2){
      mode = 3
      uuid = buffer.toString()
      uuid = uuid.trim()
    }
    else if(mode == 3){
      bufferLength = parseInt(buffer.toString());
      //console.log(buffer.toString())
      mode = 4  
    }
    else if(mode == 4){
      // theBuffer = Buffer.concat([theBuffer,buffer]);
      fs.writeFileSync(fileName, buffer, {flag:'a'}); 
      recvLength += buffer.length
      if(recvLength >= bufferLength){
        console.log('save file to ' + fileName);
        socket.write('ok\n');
        socket.end();
        console.log('uuid: '+ uuid + ' @ ' + ip +' calc finished');
        taskCalc[uuid] = undefined;
        taskCalc.splice(uuid, 1);  
        taskCalc['len']=taskCalc['len']-1;
      }
    }
  });
  
  socket.on('error',function(err){
    console.error('socket error :' + err);
  });
  
});  

var loadTasks = function(){
  var scanConf = function(){
    fs.readdir('./conf',function(err,files){
      if(err){
        console.log('error in reading conf ' + err);
        return;
      }
      
      files.forEach(function(file){
        fs.stat('./conf/' + file, function(err, stat){
          if(err){console.log(err); return;}
          if(stat.isDirectory()){                 
              // 如果是文件夹遍历
          }else{
              // 读出所有的文件
              console.log('configure file found:' + './conf/' + file);
              loadConf('./conf/' + file);
              console.log(tasks.length + ' tasks loaded!');
          }               
        });
      });
    });
  };
  
  var loadConf = function(path){
    var json = fs.readFileSync(path,{encoding:'utf8'});
    conf = JSON.parse(json);
    
    for(var eta in conf.eta){
      for(var lmbda in conf.lambda){
        for(var WEParaQ in conf.WEParaQ){
          for(var SmPa in conf.SmPa){
            var work = deepCopy(conf);
            work.eta = conf.eta[eta];
            work.lmbda = conf.lambda[lmbda];
            work.WEParaQ = conf.WEParaQ[WEParaQ];
            work.SmPa = conf.SmPa[SmPa];
            tasks.push(work);
          }
        }
      }
    }
  }
  
  scanConf();
};

var monitor = function(){
  setTimeout(monitor, 1000*60);
  console.log('*************************');
  console.log(new Date().toLocaleString());
  console.log(tasks.length + ' tasks left!');
  console.log(taskCalc['len'] + ' tasks calculating!');
  console.log(nodes.length() + ' nodes known');
  console.log(nodes.liveCount() + ' nodes is alive');
  console.log(nodes.workingCount() + ' nodes is working!');
  console.log('*************************\n');
}

var cleaner = function(){
  setTimeout(cleaner, conf.timeout * 1000);
  console.log('*************************');
  console.log('GC running!');
  nodes.clean();
  console.log('*************************\n');
}
  
loadTasks();
chatServer.listen(8899);  
setTimeout(function() {
  monitor();
  cleaner();
}, 5000);


var rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('type help to get help!\n');

rl.on('line', function (cmd) {
  console.log('------------------------\n');
  switch(cmd){
    case 'help':
      console.log('help \t get document');
      console.log('tasks \t show left tasks');
      console.log('working \t show calculating tasks');
      console.log('nodes \t show all known nodes');
    break;
    case 'tasks':
      console.log('list of undone tasks:');
      console.log(tasks);
    break;
    case 'working':
      console.log('list of calculating tasks:');
      console.log(taskCalc);
    break;
    case 'nodes':
      console.log('list of nodes:');
      console.log(nodes.getNode());
    break;
    case 'monitor':
      console.log('*************************');
      console.log(new Date().toLocaleString());
      console.log(tasks.length + ' tasks left!');
      console.log(taskCalc['len'] + ' tasks calculating!');
      console.log(nodes.length() + ' nodes known');
      console.log(nodes.liveCount() + ' nodes is alive');
      console.log(nodes.workingCount() + ' nodes is working!');
      console.log('*************************\n');
    break;
    default:
      console.log('type help to get help');
    break;
  }
  console.log('------------------------\n');
});