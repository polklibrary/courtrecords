
$(document).ready(function(){

    // Required for the UWO theme
    $('#titanServicesLink').hover(
        function(){ //over
            $("#titanServicesLinks").fadeIn(300);
        },
        function(){ //out
            $("#titanServicesLinks").fadeOut(200);
        }
    ); 
    
});


function autoResize(obj, row, animate) {
    $(window).resize(function() {
        resizeIframe(obj, row, animate);
    });
}



// Loads iframes and then resizes itself to fit
function resizeIframe(obj, row, animate) {
    // Load Iframe Content
    $(obj).attr('src', $(obj).attr('data-src')).load(function(){
        obj.style.width = $(obj).parents('.irecord').innerWidth() + 'px';
        var height = obj.contentWindow.document.body.scrollHeight + 'px';
        
        if (animate == null) {
            $(obj).animate({
                height: height
            }, 200, function() {
                if (row != null)
                    $(row).find('.add-to-basket').removeClass('hide');
            });
        }
        else
            obj.style.height = height;
    });
}

// Resets resizeIframe()
function resetIframe(obj, row) {
    $(obj).css('height', '0px');
    if (row != null)
        $(row).find('.add-to-basket').addClass('hide');
}

