function loadForFrontPage() {
  loadAllDescriptions();
  $('.initiator').on('mouseenter mouseleave', function(e) {
    if (e.type === "mouseleave"){
      loadSummary('default');
    }else{
      loadSummary(this.id);
    }
    //$('.receiver').trigger(e.type);
  })  
}

function loadAllDescriptions() {
  $.getJSON($SCRIPT_ROOT + "/_frontpagedescriptions/", function(data) {
    window.descriptions = data;
  });
}


function loadSummary(button) {
    var data = descriptions[button];
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
}


