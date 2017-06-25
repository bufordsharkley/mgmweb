console.log('hey');
var friendstxt = null;

var friendsArray = [];
var friendsArrayIndex = 0;


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


getJSON('/friends.txt', function(data){
    if (data){
        // note: hardcoded line indices. nope.
        for (var ii=4; ii < data.length - 3; ii++){
            var friendline = removeComments(data[ii]);
            var split = friendline.split(',');
            var name = split.slice(0, -1).join(',');
            var url = split[split.length - 1].replace(/^\s+|\s+$/g, '');
            friendsArray.push([name, url]);
        }
        shuffle(friendsArray);
        insertIntoDOM();
        //var url = url + '/friends.txt';
        /*var callback = function(d){ console.log(d); alert(d.attribute_name)};*/
        //J50Npi.getJSON(url, {}, callback);
        //jsonphack.getJSON(url);
        /*
        jsonphack.getJSON(url + '/friends.txt');
        console.log(name);
        console.log(url);
        console.log(friendstxt);
        */
    }
});

function insertFirst(){
    var ii = 0;
}

function insertIntoDOM(){
    while (true){
        // add to the webring (for now, don't verify)
        document.getElementById('friendstxt_webring_name').innerHTML = friendsArray[friendsArrayIndex][0];
        document.getElementById('friendstxt_webring_url').innerHTML = friendsArray[friendsArrayIndex][1];
        document.getElementById('friendstxt_webring_url').href = friendsArray[friendsArrayIndex][1];
        break;
    }
}



function friendstxt_carousel(direction){
    if (direction === 'left') {
        friendsArrayIndex--;
        if (friendsArrayIndex < 0){
            friendsArrayIndex = friendsArray.length - 1;
        }
        insertIntoDOM();
    } else if (direction === 'right') {
        friendsArrayIndex++;
        if (friendsArrayIndex >= friendsArray.length){
            friendsArrayIndex = 0;
        }
        insertIntoDOM();
    } else {
        console.log('huh?');
    }
}


function shuffle(array) {
  // adapted from http://stackoverflow.com/a/2450976
  var c = array.length, t, r;
  while (0 !== c) {
    r = Math.floor(Math.random() * c);
    c -= 1;
    t = array[c];
    array[c] = array[r];
    array[r] = t;
  }
  return array;
}

function removeComments(string){
    return string.split('#')[0];
}

/*
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
*/

var jsonphack = {
    currentScript: null,
    getJSON: function(url, callback) {
      console.log("running jsonhack on " + url);
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
