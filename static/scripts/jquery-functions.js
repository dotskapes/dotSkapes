$(document).ready(function(){

	$('#head_panel_main').mouseover(function() {

		$('#submenu').slideDown('slow', function() {
		});

	});

	$('#mouseleave').mouseleave(function() {

		$('#submenu').hide('slow');
		});

});

