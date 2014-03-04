function loadForFrontPage() {
  $('.initiator').on('mouseenter mouseleave', function(e) {
    if (e.type === "mouseleave"){
      loadSummary('default');
    }else{
      loadSummary(this.id);
    }
    //$('.receiver').trigger(e.type);
  })  
}

function loadSummary(button) {
  $.getJSON($SCRIPT_ROOT + "/_frontpagedescriptions/" + button + "/", function(data) {
    var summary = data.summary;
    var htmlsummary = new Array();
    for (i=0; i < summary.length; i++){
      if (summary[i].length == 0) {
        htmlsummary.push('<br/>');
      }else{
        htmlsummary.push(summary[i]);
      }
    }
    $("#frontpageimage").attr("src",data.img);
    $("#summary").html(htmlsummary.join(''));
    /*var splash_height = $('#splash').height();
    console.log(splash_height);
    if ( splash_height < 650 ) {
       $('#splash').attr("height", splash_height);
    }*/
  });
}


