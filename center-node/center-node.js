var net = require('net');
var fs = require('fs');

var deal = {
  '0':{
    'worker ping':function(socket){
      socket.write('server ping\n');
      return '1';
    },
    'worker finish':function(socket){
      socket.write('server ping\n');
      return 'save'
    }
  },
  '1':{
    'ok':function(socket){
      socket.write('null\n');
      return '2';
    },
  },
  '2':{
    'ok':function(socket){
      socket.end()
      return '0';
    }
  }
};

var chatServer = net.createServer();  
chatServer.on('connection', function(socket) {  
  // 1 - text 2 - uuid 3 - length 4 - hex
  var mode = 1;
  var state = '0';
  var bufferLength,recvLength = 0;
  // var theBuffer = new Buffer('');
  var fileName = './res/'+(Date.now() / 1000)+'.res';
  
  socket.on('data',function(buffer){
    if(mode == 1){
      var clientString = buffer.toString();
      var sp = clientString.split('\n');
      if(typeof(deal[state][sp[0]]) == 'undefined'){
        console.error('undefined deal function!');
        socket.end();
      }
      else{
        var res = deal[state][sp[0]](socket);
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
      console.log(buffer.toString())
    }
    else if(mode == 3){
      bufferLength = parseInt(buffer.toString());
      console.log(buffer.toString())
      mode = 4
      
    }
    else if(mode == 4){
      // theBuffer = Buffer.concat([theBuffer,buffer]);
      fs.writeFileSync(fileName, buffer, {flag:'a'}); 
      recvLength += buffer.length
      console.log(recvLength);
      if(recvLength >= bufferLength){
        console.log('save file to ' + fileName);
        socket.write('ok\n');
        socket.end();
      }
    }
  });
  
  socket.on('error',function(err){
    console.error('socket error :' + err);
  });
  
});  
  
chatServer.listen(8899);  