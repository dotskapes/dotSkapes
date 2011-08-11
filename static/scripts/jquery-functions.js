$(document).ready(function(){

	$('#head_panel_main').mouseover(function() {
	  $('#submenu').slideDown('slow', function() {

	  });
	});

	$('#head_panel').mouseleave(function() {
	  $('#submenu').hide('slow');
	});

});

