function loadForFrontPage() {
  console.log("update");
  $.getJSON($SCRIPT_ROOT + "/_frontpagedescriptions/", function(data) {
    //$("#summary").text(data.defaultsplash.summary);
    /console.log(data.defaultsplash.summary);
  });
}


function loadFlickr() {
  // Receives JSON of many HTML images; simply concatenates.
    $.getJSON($SCRIPT_ROOT + "/api/randomflickr/8/", function(data) {
        if (data["status"] == "OK") {
            var allphotos = "";
            var photo_list = data.photos.photos; // TODO: Fix this in the backend
            for (var i = 0; i < photo_list.length; i++) {
                var photo_html = '<a href="' + photo_list[i].detail
                           + '"><img src="' + photo_list[i].img
                           + '" alt= "' + photo_list[i].alt
                           + '" height=75 width=75 border=0></a>'
                allphotos += photo_html;
            }
            $("#flickr-box").html(allphotos);
        }
        else {
          // TODO: Fail gracefully by displaying an error to the user
        }
    });
}

