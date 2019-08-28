
var Themer = {
    
    Backgrounds : [
        '1.jpg',
        '2.jpg',
        '3.jpg',
        '4.jpg',
        '5.jpg',
        '6.jpg',
        '7.jpg',
        '8.jpg',
        '9.jpg',
    ],
    
    init : function(){
        var bk = this.Backgrounds[Math.floor(Math.random()*this.Backgrounds.length)];
        var url = 'url(/themes/images/backgrounds/' + bk + ')';
        $('html').css('background-image', url);
    },
}
Themer.init();




var QuickSearch = {
    
    init : function() {
        var self = this;
        $('.manage-quick-search-button').click(function() {
            self._construct();
        });
        
    },
    
    _construct : function(){
        var iframe = $('<iframe>').attr({'id':'quick-search', 'src': window.domain + '/manage/search'}).addClass('popup-iframe');
        var backdrop = $('<div>').attr({'id':'backdrop'}).html('Click outside the box to close').click(function(){
            $('#quick-search').remove();
            $('#backdrop').remove();
        });
        $('body').append(backdrop).append(iframe);
    },
    
    quick : function(query, callback){
        $.get(window.domain + '/manage/search/quick', query, function(data){
            callback(data);
        });
    },
    
    update : function() {
        var current_height = $('body').prop('scrollHeight');
        $('#quick-search', window.parent.document).height(current_height + 'px');
    }
    
}


if( $.cookie != undefined)
    $.cookie.json = true; // Setup Cookies

var StickyFields = {
    name : 'sticky',
    
    
    stickify : function(id) {
        var self = this;
        $(id).change(function(){
            var content = '';
            if($(this).is('input'))
                content = $(this).val();
            if($(this).is('select'))
                content = $(this).find('option:selected').val();
            if($(this).is('textarea'))
                content = $(this).text();
            self.remove(id);
            self.add(id,content);
        });
    },
    
    load_any_stickies : function() {
        var content = this.items();
        for (var selector in content) {
            if($(selector).is('input'))
                $(selector).val(content[selector]);
            if($(selector).is('textarea'))
                $(selector).text(content[selector]);
            if($(selector).is('select'))
                $(selector).find('option[value="'+content[selector]+'"]').attr('selected', true);
        }
    },
    
    add : function(key, value) {
        var items = this.items();
        items[key] = value; // key=case_id, value=case_id | why? this is faster than array's
        $.cookie(this.name, items);
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
    
    is_sticky : function(data) {
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
    },
    
    clear : function () {
        $.removeCookie(this.name);
    },
    
    make_sticky : function() {
        $.cookie(this.name, items);
    }

}