
var Tools = {
    toID : function(str1,str2,str3,new_delimiter){
        var delimiter = '-';
        if (new_delimiter != null) delimiter = new_delimiter;
        if (str3 != null) return '#' + str1 + delimiter + str2 + delimiter + str3;
        if (str2 != null) return '#' + str1 + delimiter + str2;
        return '#' + str1;
    },
    
}    


var Search = {
    
    init : function() {

        $('.search-add').each(function(i){
            $(this).attr('data-index',i);
        });
        
        $('body').click(function(e) {
        
            if($(e.target).parents('.search-add').length > 0 || $(e.target).is('.search-add')) {
                var container = $(e.target).parents('.search-add');
                var f = $(container).find('.options');
                
                $('.search-add').each(function(i,t){
                    if ( i != parseInt($(container).attr('data-index')) ) {
                        $(t).find('.options').hide();
                        $('.search-add span.opened').removeClass('opened');
                    }
                });
                $(container).find('.options').show();
                $(container).find('label>span').addClass('opened');
            }
            else {
                $('.search-add .options').hide();
                $('.search-add span.opened').removeClass('opened');
            }
        });
        
    },
    
    checkbox_handlers : function() {
        $('.search-add').each(function(i){
            // Handle previous searchs and checking "All"
            if( $(this).find('input[type=checkbox]:checked').length == 0) {
                $(this).find('input[type=checkbox]:first').prop('checked',true);
            }
            
            // Handle if "All" item is clicked, to uncheck/check others
            $(this).find('input[type=checkbox]:first').change(function(){
                if ($(this).is(':checked'))
                    $(this).parents('.search-add').find('input[type=checkbox]:gt(0)').prop('checked',false);
            });
            
            // Handle if one item is clicked, to uncheck "All"
            $(this).find('input[type=checkbox]:gt(0)').change(function(){
                $(this).parents('.search-add').find('input[type=checkbox]:first').prop('checked',false);
            });
        });
    },
    
    date_adjuster : function() {
        $('#start_date').change(function(){
            var start = $(this).val();
            
            $('#end_date option').each(function(i){
                if (i != 0 && $(this).val() <= start)
                    $(this).hide();
                else
                    $(this).show();
            });
        });
    },
    
    advanced : function() {
        var original_label = $('#advanced-search').html();
        
        // init
        if(!$('#advanced-options').is(':hidden')) {
            $('#advanced-search').html('Basic Search');
            $('#search-mode').val('advanced');
        }
        
        $('#advanced-search').click(function(){
            if($('#advanced-options').is(':hidden'))
                $('#advanced-options').animate({
                    opacity: 1.0,
                    height: "toggle"
                },400, function(){
                    $('#advanced-search').html('Basic Search');
                    $('#search-mode').val('advanced');
                });
            else
                $('#advanced-options').animate({
                    opacity: 0.0,
                    height: "toggle"
                },200, function(){
                    $('#advanced-search').html(original_label);
                    $('#search-mode').val('basic');
                });
        });

    },
    
    modes : function() {
        
        // Handle other modes.
        var GetParam = function(sParam) {
            var sPageURL = window.location.search.substring(1),
                sURLVariables = sPageURL.split('&'),
                sParameterName,
                i;
            for (i = 0; i < sURLVariables.length; i++) {
                sParameterName = sURLVariables[i].split('=');

                if (sParameterName[0] === sParam) {
                    return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
                }
            }
            return '';
        };
        
        var mode = GetParam('mode');
        if (mode != '' && mode != null)
            $('#search-mode').val(mode);
    },

}

 
var Facets = {

    is_loaded : false,
    _facets : {},

    
    load : function(data) {
        if (!this.is_loaded) {
            this.is_loaded = true;
            $.extend(true, this._facets, data.facets);
            this.create_facet();
            this.facet_pinner();
            this.clear_more_options();
        }
    },
    
    
    create_facet : function() {
        var self = this;
        var row = 0;
        var MAX_ROWS = 13;
        $.each(this._facets, function(k, v) {
            var heading = $('<div>').addClass('facet-heading').html(v.clean_name);
            var ul = $('<ul>');
            for (var i in v.data) {
                //row++;
                if (v.data[i].count > 0) { 
                    var facet = self._facet_click_handler($('<span>').addClass('facet ' + self.make_target(v.data[i].facet))
                                                                     .html(v.data[i].facet), v.name, v.data[i].id);
                    var count = $('<span>').addClass('count').html(' (' + v.data[i].count + ')');
                    var li = $('<li>').append(facet).append(count);
                    $(ul).append(li);
                    row++;
                    
                    if (MAX_ROWS == row) {
                        $(ul).addClass('minimize');
                        var d = $('<div>').addClass('more').html('More Options <b>&#x25BE;</b>').click(function(){
                            $('#facet-list .minimize').find('li').show();
                            $(this).parents('.minimize').removeClass('minimize');
                            $(this).remove();
                        });
                        $(ul).append(d);
                    }
                    if (MAX_ROWS < row) { 
                        $(li).hide();
                    }
                }
            }
            
            row = 0;
            if ($(ul).html().indexOf('li') != -1)
                $('#facet-list').append(heading).append(ul);
                
        });
    },
    
    
    clear_more_options : function() {
        $('#facet-list ul').each(function(){
            if ($(this).find('.pinned').length > 0) {
                $(this).removeClass('minimize');
                $(this).find('.more').remove();
            }
        });
    },
    
    
    _facet_click_handler : function(selector, name, value) {
        return $(selector).click(function(){
            var input = $('<input>').prop({'type':'checkbox','value':value,'name':name,'checked':true}).addClass('ignore');
            $('#search form').append(input);
            $('#search form').trigger('submit');
        });
    },
    
    
    // Below is for the pinning of the facets in horizontal bar
    
    facet_pinner : function() {
        var self = this;
        $('#search form').find('input,select').each(function(i,t){
            if( $(this).is('input[type=checkbox]') ) {
                if( $(this).is(':checked') && $(this).attr('data-no-facet') != '1' )
                    self._create_facet_pin($.trim($(this).parent().text()), 'checkbox', 'input[value="' + $(this).val() + '"]');
            }
            if( $(this).is('select') ) {
                if( $(this).find('option:selected').attr('data-no-facet') != '1' ) {
                    var selected = $(this).find('option:selected');
                    self._create_facet_pin($(this).attr('data-label') + $(selected).val(), 'select', 'select#' + $(this).attr("id"));
                }
            }
        });
    },
    
    
    _create_facet_pin : function(label, type, target) {
        var facet = $('<span>').attr('data-target',target)
                               .attr('data-type',type)
        .html(label + ' &#215;').click(function(){
            var targeting = $(this).attr('data-target');
            var type = $(this).attr('data-type');
            if (type == 'checkbox')
                $(targeting).prop('checked', false);
            if (type == 'select') {
                $(targeting).find('option').prop('selected', false);
            }
            
            $('#search form').trigger('submit'); // redo search
        });
        
        // Change facet link to gray
        $('.' + this.make_target(label)).off('click').addClass('pinned').click(function(e){
            $(facet).trigger('click');
        });
        
        // Add facet pin
        $('#facets').show().append(facet);
        
    },
    
    
    make_target : function(s) {
        s = s.toLowerCase().replace(/\s+/g, '-');
        s = s.toLowerCase().replace(/\'/g, '-apostrophe-');
        return s.toLowerCase().replace(/\&/g, '-amp-');
    }
    
}


var DataTableExpanders = {

    row_data : [],
    cols : 0,

    draw : function(){
        var self = this;
        $('#search-results-table tbody tr').each(function(i){
            $(this).attr('data-isopen',0);
            self.cols = $(this).find('td').length;
            var id = $(this).find('td').first().text();
            
            self.attach_expander_logic(this,id);
            self.create_row(this,id);
            self.add_row_content(Tools.toID('expand',id), self.row_data[i]);
        });
        self.row_data = []; // clear for next set
    },
    
    attach_expander_logic : function(row, id){
        $(row).click(function(){
            var ltd = $(this).find('td').last().attr('data-open','expand-'+id);
            var status = $(row).attr('data-isopen');
            var e = $('#search-results-table tbody').find(Tools.toID($(ltd).attr('data-open')));
            if (status == 0) {
                $(row).attr('data-isopen',1);
                $(e).show();
                resizeIframe($(e).find('iframe')[0], e);
                    
            } else {
                resetIframe($(e).find('iframe')[0], e);
                $(row).attr('data-isopen',0);
                $(e).hide();
            }
            //
        });
    },
    
    create_row : function(row,id){
        var tr = $('<tr>').attr('id','expand-'+id).addClass('expander');
        var td = $('<td>').attr('colspan',(this.cols-1));
        $(tr).html(td);
        $(row).after(tr);
    },
    
    
    add_row_content : function(selector,data) {
        var self = this;
        var html = $('#record-template').html();
        $(selector).find('td').html(html);
        
        if (data == null || data == undefined)
            return;
        
        var src =  $(selector).find('iframe').attr('data-src');
        $(selector).find('iframe').attr('data-src', src + data._case.id);
       
        if (data._case.notes.toLowerCase().indexOf('incompetent') != -1 ||  
            data._case.notes.toLowerCase().indexOf('state general hospital') != -1
        ){
            // These records can't be added to cart. 
            console.log("Private Record");
            $(selector).find('input[name="basket.add"]').remove();
        }
        else {
            // Add Basket Handler
            $(selector).find('span.private').remove();
            $(selector).find('input[name="basket.add"]').each(function(){
                var case_id = data._entity.case_id;
                    $(this).attr('data-record',case_id);
                
                if (Basket.in_basket(case_id)) {
                    $(this).addClass('red');
                    $(this).removeClass('orange');
                    $(this).val('Remove from cart');
                }
                
                $(this).click(function(){
                    self.handle_basket_buttons(case_id);
                    if (Basket.in_basket(case_id)) 
                        Basket.remove(case_id);
                    else 
                        Basket.add(case_id,case_id);
                });
                
            });
        }
    },
    
    
    handle_basket_buttons : function (id) {
        $('#search-results-table input[name="basket.add"][data-record="'+id+'"]').each(function(){
            if( Basket.in_basket(id)) {
                $(this).removeClass('red');
                $(this).addClass('orange');
                $(this).val('Add to cart');
            }
            else {
                $(this).addClass('red');
                $(this).removeClass('orange');
                $(this).val('Remove from cart');
            }
        });
    },
    
    is_empty : function (data) {
        data = $.trim(data);
        return (data == '' || data == '0' || data == 0 || data == null)
    }

}

$.cookie.json = true; // Setup Cookies
var Basket = {
    
    name : 'basket',
    
    add : function(key,value) {
        var items = this.items();
        items[key] = value; // key=case_id, value=case_id | why? this is faster than array's
        $.cookie(this.name, items);
        this.update();
    },
    
    items : function() {
        var content = $.cookie(this.name);
        if (content == null)
            return {}
        return content;
    },
    
    items_as_array : function() {
        var content = $.cookie(this.name);
        var results = [];
        for (var i in content)
            results.append(content[i]);
        return results;
    },
    
    in_basket : function(data) {
        var content = this.items();
        for (var i in content)
            if (i == data)
                return true;
        return false;
    },
    
    remove : function(data) {
        var items = this.items();
        delete items[data];
        $.cookie(this.name, items);
        this.update();
    },
    
    clear : function () {
        $.removeCookie(this.name);
        this.update();
    },
    
    update : function () {
        var count = Object.keys(this.items()).length;
        $('#cart-count').html(count);
        if (count > 0) {
            $('#cart-count').addClass('b');
            $('#checkout-link').show();
        }
        if (count == 1)
            $('#cart-items').html('Item');
        else
            $('#cart-items').html('Items');
            
    }   
}
