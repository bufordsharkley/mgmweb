console.log('hey');

function getJSON(path, callback) {

    var xmlhttp = new XMLHttpRequest();                 
    xmlhttp.overrideMimeType('application/json');  

    xmlhttp.onreadystatechange = function() {
        ready = (xmlhttp.readyState == 4 && xmlhttp.status == 200);
        callback(ready ? xmlhttp.responseText : false);
    };

    xmlhttp.open('GET', path, true);
    xmlhttp.send();

};


getJSON('friends.txt', function(data){
console.log(data)});


var jsonphack = {  
    currentScript: null,  
    getJSON: function(url) {
      var head = document.getElementsByTagName("head")[0];
      var newScript = document.createElement("script");

      newScript.type = "text/javascript";  
      newScript.src = url;

      if(this.currentScript) head.removeChild(currentScript);
      head.appendChild(newScript); 
    },
    success: null
}; 
var url = "http://thisisalan.com/friends.txt"
