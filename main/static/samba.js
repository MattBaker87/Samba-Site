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
$(function lightsOut() {
    // Set up structure to put a message box in the centre of a dimmed screen
    $("body").prepend('<div id="dim"><div id="msgbox"></div></div>');
    $("#dim").css({ position:"absolute", top:0, left:0, width:"100%", height:$(document).height(), "z-index":20000,
                        background:'url("http://buildinternet.com/live/lightsout/dim.png")',
                        display:"none", "text-align":"left" });
    $("#msgbox").css({ position:"fixed", width:940, "z-index":30000,
                        top:$(window).height()/2, left:"50%"});
    $("#msgbox").css({ "margin-left":-$("#msgbox").width()/2 });
    // Take care of window resizing
	$(window).bind("resize", function(){
	 	$("#dim").css("height", $(document).height());
	 	$("#msgbox").css("top", $(window).height()/2);
	});
    
    // When an alertdim link is clicked...
    $(".alertdim").click(function(){
        var self = this;
        // load new content from the server into the message box...
        $("#msgbox").load($(this).attr("href") + " form:eq(0)", function() {
            $("#msgbox").css({ "margin-top":-$("#msgbox").height()/2 });
            $("#msgbox .closedim").click(function() {
        		$("#dim").fadeOut(function() {$("#msgbox").empty();});
        		return false;
        	});
        	// hijack the new form's submit method...
        	$("#msgbox").submit(function(){
        	    // disable any more submits
        	    $("#msgbox form [type=submit]").attr("disabled", "disabled")
        	    // set the action path of the form
        	    var action = $("#msgbox form").attr("action")
        	    action = action ? action !== "" : $(self).attr("href")
                // post form to the server
        	    $.ajax({
        	        type: 'POST',
        	        url: action,
        	        data: $("#msgbox form").serialize(),
        	        success: function(data) {
        	            if ($(data).find(".clearfix.error").length) {
                            $("#msgbox form").replaceWith($(data).find("form:eq(0)"));
                            $("#msgbox .closedim").click(function() {
                        		$("#dim").fadeOut(function() {$("#msgbox").empty();});
                        		return false;
                        	});
                        } else {
                            $("#dim").fadeOut(function() {
                                $("body").empty().prepend($(data).filter(function(i) {return $(this).is("div");}));
                                $(lightsOut());
                            });
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
});