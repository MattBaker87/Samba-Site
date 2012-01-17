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

// Following two functions are put together because they're used on the instruments page together
$(function() {
    // display a lights-out dialogue box
    function lightsOut() {
        // Set up structure to put a message box in the centre of a dimmed screen
        $("body").prepend('<div id="dim"><div id="msgbox"></div></div>');
        $("#dim").css({ position:"absolute", top:0, left:0, width:"100%", height:$(document).height(), "z-index":20000,
                            background:'url("http://www.sambatage.com/static/dim.png")',
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
            $.get($(this).attr("href"), function(data) {
                $("#msgbox").prepend($("form:eq(0)", $(data)));
                $("#msgbox").css({ "margin-top":-$("#msgbox").height()/2 });
                // hijack cancellation
                $("#msgbox .closedim").click(function() {
            		$("#dim").fadeOut(function() {$("#msgbox").empty();});
            		return false;
            	});
            	// hijack the new form's submit method...
            	$("#msgbox").children().submit(function(){
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
                                    lightsOut();
                                    writeNote();
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
    };

    // display a form to write a note, and submit that note
    function writeNote(){
        if (!$("tr.writenote").find("form").length) {
            // set up ajax call to display the write-note form
            var original = $("tr.writenote").clone()
            $("a", $("tr.writenote")).click(function() {
                var self = this;
                $.get($(this).attr("href"), function(data) {
                    $("tr.writenote").replaceWith($("tr.writenote", $(data)));
                    // hijack cancellation
                    $("tr.writenote a.error").click(function() {
                        $("tr.writenote").replaceWith(original);
                        writeNote();
                        return false;
                    })
                    // hijack form submission
                    $("tr.writenote").submit(function() {
                        $("tr.writenote [type=submit]").attr("disabled", "disabled");
                        var action = $("tr.writenote form").attr("action");
                	    action = action ? action !== "" : $(self).attr("href");
                	    $.ajax({
                	        type: 'POST',
                	        url: action,
                	        data: $("tr.writenote form").serialize(),
                	        success: function(data) {
                	            // get the table in the new html
                	            var temp = $(data).find("tr.writenote");
                	            while (!temp.is("table")) {
                	                temp = temp.parent()
                	            }
                	            // get the table in the old html
                	            var temp2 = $("tr.writenote");
                	            while (!temp2.is("table")) {
                	                temp2 = temp2.parent()
                	            }
                	            temp2.replaceWith(temp)
                	            writeNote();
                            },
                	        dataType: 'html'
                	    })
                	    return false;
                    })
                })
            return false;
            })
        }
    }

    lightsOut();
    writeNote();
})