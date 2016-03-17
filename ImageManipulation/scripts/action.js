$( document ).ready(function() {
$('#form').submit(function(){
	$("div#runningindicator").show();
    var request = $.ajax({
      url: $('#form').attr('action'),
      type: 'post',
      target: $('#form').attr('target'),
      data : $('#form').serialize(),
      success: function(data){

      },
      error: function(){
      	$("div#runningindicator").hide();
      }
    });
    request.done(function(msg){
    	$("div#runningindicator").hide();
    })
    return true;
});
});

function showValue(identity, newValue) {
	document.getElementById(identity).innerHTML=newValue;
}
