$(document).ready(function(){

	// slide down sub menu bar from head_panel
	$('#head_panel_main').mouseover(function() {

		$('#submenu').slideDown('slow', function() {
		});

	});

	// hide sub menu when mouse leave
	$('#mouseleave').mouseleave(function() {

		$('#submenu').hide('slow');
		});
	

});

