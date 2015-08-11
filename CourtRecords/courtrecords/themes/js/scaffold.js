


var Scaffold = {
    
    deletion_warning : function() {

        // Thread to capture any live changes
        setInterval(function(){
            $('.warning').each(function(i,t){
                $(t).removeClass('warning');
                $(t).addClass('warning-ready');
                $(t).click(function(e){
                    var r = confirm("Are you sure?");
                    if (!r) {
                        e.preventDefault();
                        return false;
                    }
                });
            });
        },1000);

    },
    
    validator_email : function () {
        var isEmail = function(email) {
              var regex = /^([a-zA-Z0-9_\.\-\+])+\@uwosh.edu/;
              return regex.test(email);
        }
        $(".email-validator").change(function(){
            if(!isEmail($(this).val())) 
                $(this).val('');
        });
    },
    
    validator_numbers : function () {
        $('.number-validator').keyup(function(){
            if ($(this).is('input')) {
                var v = $(this).val();
                $(this).val(v.replace(/[^0-9]/, ''));
            }
            if ($(this).is('textarea')) {
                var t = $(this).text();
                $(this).text(t.replace(/[^0-9]/, ''));
            }
        });
        $('.number-validator').change(function(){
            if ($(this).is('input')) {
                var v = $(this).val();
                $(this).val(v.replace(/[^0-9]/, ''));
            }
            if ($(this).is('textarea')) {
                var t = $(this).text();
                $(this).text(t.replace(/[^0-9]/, ''));
            }
        });
    },
    
    validator_currency : function () {
        $('.price-validator').number( true, 2 );
    },
    
}


// Init
$(document).ready(function(){
    Scaffold.deletion_warning();
    Scaffold.validator_email();
    Scaffold.validator_numbers();
    Scaffold.validator_currency();
    
    var use_editor = jQuery('#form-use_editor').find('option:selected').val();
    
    if (use_editor == 1 || use_editor == '1') {
        tinymce.init({
            selector : ".mce-content-body",
            menubar : false,
            toolbar: "undo redo  | bold italic underline | alignleft aligncenter alignright | bullist numlist | removeformat",
            height : 200,
            content_css : domain + '/themes/css/tinymce.css'
            
        });
    }
    
});




