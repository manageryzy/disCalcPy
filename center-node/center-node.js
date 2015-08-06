var net = require('net');
var fs = require('fs');
var readline = require('readline');
var http = require('http');
var url=require('url');
var formidable = require('formidable');
var util = require('util');

var conf,tasks = [],taskCalc = [];

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

String.prototype.format = function (args) {
  if (arguments.length > 0) {
    var result = this;
    if (arguments.length == 1 && typeof (args) == "object") {
      for (var key in args) {
        var reg = new RegExp("({" + key + "})", "g");
        result = result.replace(reg, args[key]);
      }
    }
    else {
      for (var i = 0; i < arguments.length; i++) {
        if (arguments[i] == undefined) {
          return "";
        }
        else {
          var reg = new RegExp("({[" + i + "]})", "g");
          result = result.replace(reg, arguments[i]);
        }
      }
    }
    return result;
  }
  else {
    return this;
  }
} 

// Array.prototype.remove=function(dx)
// {

//   if(isNaN(dx)||dx>this.length){return false;}
//   for(var i=0,n=0;i<this.length;i++)
//   {
//       if(this[i]!=this[dx])
//       {
//           this[n++]=this[i]
//       }
//   }
//   this.length-=1
// }


var loadTasks = function(){
  var scanConf = function(){
    fs.readdir('./tasks',function(err,files){
      if(err){
        console.log('error in reading conf ' + err);
        return;
      }
      
      files.forEach(function(file){
        fs.stat('./tasks/' + file, function(err, stat){
          if(err){console.log(err); return;}
          if(stat.isDirectory()){                 
              // 如果是文件夹遍历
          }else{
              // 读出所有的文件
              console.log('configure file found:' + './conf/' + file);
              loadTaskConf('./tasks/' + file);
              console.log(tasks.length + ' tasks loaded!');
          }               
        });
      });
    });
  };
  
  var loadTaskConf = function(path){
    var json = fs.readFileSync(path,{encoding:'utf8'});
    var conf = JSON.parse(json);
    
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

var loadConf = function(){
  var json = fs.readFileSync('./conf.json',{encoding:'utf8'});
  conf = JSON.parse(json);
}

var Nodes = function(){
  //工作节点类
  var nodes_list = [];
  
  this.newNode = function(ip,uuid){
    var obj = new Object();
    obj.ip = ip;
    obj.uuid = uuid;
    obj.lastActive = new Date();
    nodes_list.push(obj);
  }
  
  this.getNodes = function(){
    return nodes_list;
  }
  
  this.getNodeByUUID = function(uuid){
    var res = [];
    for(var node in nodes_list){
      if(nodes_list[node].uuid == uuid){
        res.push(nodes_list[node]);
      }
    }
    return res;
  }
  
  this.getNodeByIP = function(ip){
    var res = [];
    for(var node in nodes_list){
      if(nodes_list[node].ip == ip){
        res.push(nodes_list[node]);
      }
    }
    return res;
  }
  
  this.removeNodeByUUID = function(uuid){
    var found = false;
    for(var i = 0;i<nodes_list.length;i++){
      if(nodes_list[i].uuid == uuid){
        found = true;
      }
      
      if(found){
        nodes_list[i] = nodes_list[i+1];
      }
    }
    if(found){
      nodes_list.length -= 1;
    }
  }
}

var Jobs = function(){
  //任务类
  var jobs_list = [];
  
  this.newJob = function(jobid,parmeter){
    var obj = new Object();
    obj.jobid = jobid;
    obj.parmeter = parmeter;
    obj.calced = false;
    obj.nodeID = '';
    jobs_list.push(obj);
  }
  
  this.getJobs = function(){
    return jobs_list;
  }
  
  this.getFinishedList = function(){
    var res = [];
    for(var i in jobs_list){
      if(jobs_list[i].calced == true){
        res.push(jobs_list[i]);
      }
    }
    return res;
  }
  
  this.getUnfinishedList = function(){
    var res = [];
    for(var i in jobs_list){
      if(jobs_list[i].calced == false){
        res.push(jobs_list[i]);
      }
    }
    return res;
  }
  
  this.findJobsByJobID = function(id){
    var res = [];
    for(var i in jobs_list){
      if(jobs_list[i].jobid == id){
        res.push(jobs_list[i]);
      }
    }
    return res;
  }
  
  this.findJobsByUUID = function(uuid){
    var res = [];
    for(var i in jobs_list){
      if(jobs_list[i].nodeID == uuid){
        res.push(jobs_list[i]);
      }
    }
    return res;
  }
}

var Computers = function(){
  //计算机类，用来记录关于节点类型分发
  var proxy_node_list = [];//
  var worker_node_list = [];
  
  var assignCount = Infinity;
  var assignProxy = '';
  
  this.newComputer = function(ip,info){
    
    
    var obj = new Object();
    obj.ip = ip;
    obj.info = info;
    
    if(assignCount >= conf.assignCount){
      assignProxy = ip;
      assignCount = 0;
      obj.type = 'proxy';
      obj.proxy = '';
      proxy_node_list.push(obj)
    }  
    else{
      assignCount ++ ;
      obj.type = 'worker';
      obj.proxy = assignProxy;
      worker_node_list.push(obj);
    }
  }
  
  this.getProxyNodes = function(){
    return proxy_node_list;
  }
  
  this.getProxyNodesByIP = function(ip){
    var res = [];
    for(var i in proxy_node_list){
      if(proxy_node_list[i].ip == ip){
        res.push(proxy_node_list[i]);
      }
    }
    return res;
  }
  
  this.getWorkerNodes = function(){
    return worker_node_list;
  }
  
  this.getWorkerNodesByIP = function(ip){
    var res = [];
    for(var i in worker_node_list){
      if(worker_node_list[i].ip == ip){
        res.push(worker_node_list[i]);
      }
    }
    return res;
  }
  
  this.getWorkerNodesByPorxy = function(ip){
    var res = [];
    for(var i in worker_node_list){
      if(worker_node_list[i].porxy == ip){
        res.push(worker_node_list[i]);
      }
    }
    return res;
  }
  
  this.getNodesByIP = function(ip){
    return this.getProxyNodesByIP(ip).concat(this.getWorkerNodesByIP(ip));
  }
  
  this.getComputers = function(){
    return proxy_node_list.concat(worker_node_list);
  }
}

var nodes = new Nodes();
var jobs = new Jobs();
var computers = new Computers();

var monitor = function(){
  //TODO:
  // console.log('*************************');
  // console.log(new Date().toLocaleString());
  // console.log(tasks.length + ' tasks left!');
  // console.log(taskCalc['len'] + ' tasks calculating!');
  // console.log(nodes.length() + ' nodes known');
  // console.log(nodes.liveCount() + ' nodes is alive');
  // console.log(nodes.workingCount() + ' nodes is working!');
  // console.log('*************************\n');
}

var monitord = function(){
  monitor();
  setTimeout(monitord, 1000*60);
}

var cleaner = function(){
  //TODO:
  // setTimeout(cleaner, conf.timeout * 1000);
  // console.log('*************************');
  // console.log('GC running!');
  // nodes.clean();
  // console.log('*************************\n');
}

var rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

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
      monitor();
    break;
    default:
      console.log('type help to get help');
    break;
  }
  console.log('------------------------\n');
});

var TemplateLoader = function(){
  var templates = [];
  this.loadTemplate = function(path,callback) {
    if(typeof(templates[path])==="undefined"){
      fs.readFile(path,"binary",function(err,data){
        if(err){
          console.log(err);
          return;
        }
        
        templates[path] = data;
        callback(data);
      });
    }
    else{
      callback(templates[path]);
    }
  }
  
  this.loadTemplateSync = function(path){
    if(typeof(templates[path])==="undefined"){
      templates[path] = fs.readFileSync(path,"binary");
    }
    
    return templates[path];
  }
  
  return this;
}

var templateLoader = TemplateLoader();

var View = function(){
  this.index = function(request,response){
    response.writeHead(200,{'Content-Type': 'text/html'});
    templateLoader.loadTemplate('./template/head.html',function(head){
      templateLoader.loadTemplate('./template/index.html',function(index){
        templateLoader.loadTemplate('./template/footer.html',function(footer){
          response.write(head+index+footer,"binary");
          response.end();
        });
      });
      
    })
  }
  
  this.computers_list = function(request,response){
    response.writeHead(200,{'Content-Type': 'text/html'});
    var head = templateLoader.loadTemplateSync('./template/head.html');
    var table_head = templateLoader.loadTemplateSync('./template/computer_list_start.html');
    var table_repeat = templateLoader.loadTemplateSync('./template/computer_list_repeat.html');
    var table_end = templateLoader.loadTemplateSync('./template/computer_list_end.html');
    var footer = templateLoader.loadTemplateSync('./template/footer.html');
    
    var data = '';
    
    var computers_list = computers.getComputers();
    for(var i in computers_list){

      data+=table_repeat.format({"ip":'<a href="/computers/'+computers_list[i].ip+'">'+computers_list[i].ip+'</a>',
        "type": computers_list[i].type,
        "proxy": computers_list[i].proxy,
        "data":computers_list[i].info})
    }
    
    response.write(head + table_head + data + table_end + footer,"binary");
    response.end();
  }
  
  this.computer = function(ip,request,response){
    response.writeHead(200,{'Content-Type': 'text/html'});
    response.end();
  }
  
  this.nodes_list = function(request,response){
    response.writeHead(200,{'Content-Type': 'text/html'});
    response.end();
  }
  
  this.node = function(ip,request,response){
    response.writeHead(200,{'Content-Type': 'text/html'});
    response.end();
  }
  
  this.tasks = function(request,response){
    response.writeHead(200,{'Content-Type': 'text/html'});
    response.end();
  }
  return this;
}
var view = View();

var server = http.createServer(function (request, response) {
  var url = request.url.split('/');
  var task = url[1];
  var parm = url[2];
  switch(task){
    case '':
      //index
      view.index(request,response);
    break;
    
    case 'computers':
      if(typeof(parm) === "undefined" || parm == ""){
        //coumputer index
        view.computers_list(request,response);
      }
      else{
        //show single computer info
        view.computer(parm,request,response);
      }
    break;
    
    case 'nodes':
      if(typeof(parm) === "undefined" || parm == ""){
        //coumputer index
        view.nodes_list(request,response);
      }
      else{
        //show single computer info
        view.node(parm,request,response);
      }
    break;
    
    case 'tasks':
      //show tasks list
      view.tasks(request,response);
    break;
    
    // case 'upload':
    //   if (request.method.toLowerCase() == 'post') {
    //     var form = new formidable.IncomingForm();
    //     form.uploadDir = './upload'
    //     form.parse(request, function(err, fields, files) {
    //       response.writeHead(200, {'content-type': 'text/plain'});
    //       response.write('received upload:\n\n');
    //       response.end(util.inspect({fields: fields, files: files}));
    //     });
    //   } 
    // break;
    
    case 'favicon.ico':
      response.writeHead(404);
      response.end();
    break;
    default:
      response.writeHead(302, {'Location': '/'});
      response.write('redirect you to index',"binary");
      response.end();
  }
  
  
});
  
loadConf();
loadTasks();
computers.newComputer('1.0.0.1','');
for(var i=1;i<40;i++)
  computers.newComputer('127.0.0.1','');

setTimeout(function() {
  monitord();
  cleaner();
}, 5000);

console.log('type help to get help!\n');
server.listen(conf.port);