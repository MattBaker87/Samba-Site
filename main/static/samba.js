// add close-message handlers to alert messages
$(function() {
    $('.alert-message a.close').click(function() {
        elt = $(this)
        while (elt.parent) {
            elt = elt.parent()
            if (elt.is('.alert-message')) {
                elt.fadeOut({ duration:"fast", queue:false });
                return false;
            }
        }
    });
});

// display a lights-out dialogue box
$(function() {
    // Set up structure to put a message box in the centre of a dimmed screen
    $("body").prepend('<div id="dim"><div id="msgbox"></div></div>');
    $("#dim").css({ position:"absolute", top:0, left:0, width:"100%", height:$(document).height(), "z-index":20000,
                        background:'url("http://buildinternet.com/live/lightsout/dim.png")',
                        display:"none", "text-align":"left" });
    $("#msgbox").css({ position:"fixed", width:940, "z-index":200,
                        top:$(window).height()/2, left:"50%"});
    $("#msgbox").css({ "margin-left":-$("#msgbox").width()/2 });
    
    // When an alertdim link is clicked dim the screen and get the required form from the server
    $(".alertdim").click(function(){
        var self = this;
        $("#msgbox").load($(this).attr("href") + " form:eq(0)", function() {
            $("#msgbox").css({ "margin-top":-$("#msgbox").height()/2 });        // centre the alert box vertically
            $("#msgbox .closedim").click(function() {                           // set up close links
        		$("#dim").fadeOut(function() {$("#msgbox").empty();});
        		return false;
        	});
        	$("#msgbox").submit(function(){
        	    var action = $("#msgbox form").attr("action") ? $("#msgbox form").attr("action") !== "" : $(self).attr("href");
        	    $.ajax({
        	        type: 'POST',
        	        url: action,
        	        data: $("#msgbox form").serialize(),
        	        success: function(data) {
        	            if ($(data).find("form .clearfix.error").length) {
                            $("#msgbox form").replaceWith($(data).find("form:eq(0)"));
                            $("#msgbox .closedim").click(function() {                           // set up close links
                        		$("#dim").fadeOut(function() {$("#msgbox").empty();});
                        		return false;
                        	});
                        } else {
                            $("#dim").fadeOut(function() {location.reload();});
                        }
                    },
        	        dataType: 'html'
        	    })
        	    return false;
        	})
        });
     	$("#dim").fadeIn();
		return false;
	});
    
    // Take care of window resizing
	$(window).bind("resize", function(){
	 	$("#dim").css("height", $(document).height());
	 	$("#msgbox").css("top", $(window).height()/2);
	});
});