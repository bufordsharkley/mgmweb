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
            var url = split[split.length - 1];
            jsonphack.getJSON(url + '/friends.txt');
            console.log(name);
            console.log(url);
            console.log(friendstxt);
        }
    }
});

function removeComments(string){
    return string.split('#')[0];
}

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
