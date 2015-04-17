console.log('hey');
var friendstxt = null;

function getJSON(path, callback) {
    var xmlhttp = new XMLHttpRequest();                 
    xmlhttp.overrideMimeType('application/json');  
    xmlhttp.onreadystatechange = function() {
        ready = (xmlhttp.readyState == 4 && xmlhttp.status == 200);
        callback(ready ? xmlhttp.responseText.split("\n") : false);
    };
    xmlhttp.open('GET', path, true);
    xmlhttp.send();
};


getJSON('friends.txt', function(data){
    if (data){
        // note: hardcoded line indices. nope.
        for (var ii=4; ii < data.length - 3; ii++){
            var friendline = removeComments(data[ii]);
            var split = friendline.split(',');
            var name = split.slice(0, -1).join(',');
            var url = split[split.length - 1].replace(/^\s+|\s+$/g, '');
            var url = url + '/friends.txt';
            var callback = function(d){ console.log(d); alert(d.attribute_name)};
            J50Npi.getJSON(url, {}, callback);
            /*
            jsonphack.getJSON(url + '/friends.txt');
            console.log(name);
            console.log(url);
            console.log(friendstxt);
            */
        }
    }
});

function removeComments(string){
    return string.split('#')[0];
}

var J50Npi = {  
    currentScript: null,  
    getJSON: function(url, data, callback) {
      var src = url + (url.indexOf("?")+1 ? "&" : "?");
      var head = document.getElementsByTagName("head")[0];
      var newScript = document.createElement("script");
      var params = [];
      var param_name = ""

      this.success = callback;
      data["callback"] = "J50Npi.success";
      for(param_name in data){  
          params.push(param_name + "=" + encodeURIComponent(data[param_name]));  
      }
      src += params.join("&")

      newScript.type = "text/javascript";  
      newScript.src = src;

      if(this.currentScript) head.removeChild(this.currentScript);
      head.appendChild(newScript);
      this.currentScript = newScript;
    },
    success: null
}; 

var jsonphack = {  
    currentScript: null,  
    getJSON: function(url, callback) {
      var head = document.getElementsByTagName("head")[0];
      var newScript = document.createElement("script");

      newScript.type = "text/javascript";  
      newScript.src = url;

      if(this.currentScript) head.removeChild(this.currentScript);
      head.appendChild(newScript);
      this.currentScript = newScript;
    },
    success: null
}; 
var url = "http://thisisalan.com/friends.txt"
