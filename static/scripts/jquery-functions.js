$(document).ready(function(){

	// slide down sub menu bar from head_panel
	$('#head_panel_main').mouseover(function() {
		$('#submenu').slideDown('slow', function() {
		});
		$('#submenu_docs').slideUp('slow');
	});

	// hide sub menu when mouse leave
	$('#mouseleave').mouseleave(function() {
		$('#submenu').slideUp('slow');
	});



	// slide down sub menu bar from head_panel
	$('#head_panel_docs').mouseover(function() {
		$('#submenu_docs').slideDown('slow', function() {
		});
		$('#submenu').slideUp('slow');
	});


	// hide sub menu when mouse leave
	$('#mouseleave').mouseleave(function() {
		$('#submenu_docs').slideUp('slow');
	});

	// toggle display method on team/index.html
	$("#toggle_display").click(function () {
		$("#sortbygroup").toggle();
		$("#sortbyname").toggle();
		$("#listbygroup").toggle();
		$("#listbyname").toggle();
	});

});

