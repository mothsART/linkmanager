var nb_links;
var search_links;
var search_tags = '';
var initial_links = [];

/* Position fixed on all dialogs
describe here : http://stackoverflow.com/questions/2657076/jquery-ui-dialog-fixed-positioning#answer-9242751
*/
$.ui.dialog.prototype._oldinit = $.ui.dialog.prototype._init;
$.ui.dialog.prototype._init = function() {
    $(this.element).parent().css('position', 'fixed');
    $(this.element).dialog("option",{
        resizeStop: function(event,ui) {
            var position = [(Math.floor(ui.position.left) - $(window).scrollLeft()),
                            (Math.floor(ui.position.top) - $(window).scrollTop())];
            $(event.target).parent().css('position', 'fixed');
            // $(event.target).parent().dialog('option','position',position);
            // removed parent() according to hai's comment (I didn't test it)
            $(event.target).dialog('option','position',position);
            return true;
        }
    });
    this._oldinit();
};
initial_links.push({
    'title': '', 'url': '', 'real_url': '',
    'tags': '', 'author': '',
    'priority': 1, 'description': ''
});
var links_status = [];
links_status.push({
    'title': null, 'url': null, 'tags': null,
    'priority': null, 'description': null
});
var new_links = JSON.parse(JSON.stringify(initial_links));
var dialogs = {};

function add_widget_event(){
    $("#add-widget input, #add-widget textarea").bind('input', function(){
        adapt_form(input=this, add=true);
    });
    $("#add-widget .tagit").tagit({
        // Options
        fieldName: "tags",
        availableTags: suggest_callback,
        autocomplete: {delay: 0, minLength: 1},
        showAutocompleteOnFocus: false,
        removeConfirmation: false,
        caseSensitive: true,
        allowDuplicates: false,
        allowSpaces: false,
        readOnly: false,
        tagLimit: null,
        singleField: false,
        singleFieldDelimiter: ',',
        singleFieldNode: null,
        tabIndex: null,
        placeholderText: null,
        afterTagAdded: function(evt, ui){
            tag_update(evt, ui, remove=false, add=true);
        },
        beforeTagRemoved: function(evt, ui){
            tag_update(evt, ui, remove=true, add=true);
        },
    });
}
var original_add_widget = $('#add-widget').clone();
add_widget_event();

// Change Edit Mode
$("#editmode").click(function(){
    editmode = $(this).hasClass('active');
    if(editmode == false){
        $(this).addClass('active');
        $('.glyphicon-plus').removeClass('hidden');
        $('td:nth-child(3)').removeClass('hidden');
        _.map(links_status, function(key){
            key['priority'] = null;
            return key;
        });
        show_links(_.clone(_.rest(new_links)));
    }
    else {
        $(this).removeClass('active');
        $('.glyphicon-plus').addClass('hidden');
        $('td:nth-child(3)').addClass('hidden');
        show_links(_.clone(_.rest(initial_links)));
    }
    if ($(this).hasClass('server_mode')) { return; }
    $.ajax({
        url: './editmode',
        type: "POST",
        data: {editmode: $(this).hasClass('active')},
        dataType: "json",
    });
});

// show an add widget
function add_widget(){
    create_root_node('dialog-add-link', 'Add a link ?');
    dialogs['dialog-add-link'].dialog("open");
}

// Add a link
function add_link(){
    new_link = new_links[0];
    $.post(
        "./add",
        {
            link: new_link['url'],
            title: new_link['title'],
            newlink: new_link['url'],
            priority: new_link['priority'],
            tags: new_link['tags'].join(' '),
            description: new_link['description']
        }
    ).done(function(value){
        show_links(_.clone(_.rest(initial_links)));

        $('#nb-links strong:first').text(nb_links + 1);

        // table = $('#add-widget').before(
        //     '<small class="update">URL\'s properties update</small>'
        // );
        // update_message = table.next();
        // setTimeout(function(){
        //     update_message.addClass('disappear');
        // }, 1);
        $('#add-widget').addClass('hidden');
        //setTimeout(function(){
        //     update_message.remove();
        // }, 1000);
    }, "json");
}

// Create if not exist a root Node Dialog
function create_root_node(id, title) {
    if (!$('#' + id).length) {
        var div = $('<div></div>').attr('id', id).attr('title', title);
        $('body').prepend(div);
        if (id === "dialog-confirm-deletion") {
            // Delete dialog
            dialogs[id] = $('#' + id).dialog({
                autoOpen: false,
                height: 50,
                width: 250,
                modal: true,
                resizable: false,
                open: function(){
                    $('.ui-widget-overlay').bind('click', function(){
                        $('#' + id).dialog('close');
                    })
                },
                buttons: {
                    "Confirm deletion": function() {
                        link = $(this).data('link');
                        result_index = $(this).data('result_index');
                        $.post(
                            "./delete",
                            {link: link}
                        ).done(function(value){
                            initial_links.splice(result_index, 1);
                            links_status.splice(result_index, 1);
                            new_links.splice(result_index, 1);
                            show_links(_.clone(_.rest(initial_links)));
                            $('#nb-links strong:first').text(nb_links - 1);
                        }, "json");
                        $(this).dialog("close");
                    },
                    Cancel: function() {
                        $(this).dialog("close");
                    }
                },
                show: {effect: 'fade', duration: 400},
                hide: {effect: 'fade', duration: 400}
            });
            return id;
        }
        edit = $("#editmode").hasClass('active');
        add_link = {'link': '', 'title': ''}
        html = show_link(0, add_link, 0, 0);
        table = $($(html).children()[1]).children()[0];
        //$(table).children().children().last().addClass('add-hidden');
        $('#' + id).append(table);
        dialogs[id] = $('#' + id).dialog({
            autoOpen: false,
            height: 400,
            width: 550,
            modal: true,
            dialogClass: "add-dialog",
            open: function(){
                $('.ui-widget-overlay').bind('click', function() {
                    $('#' + id).dialog('close');
                })
            },
            // buttons: {
            //     "Confirm addition": function() {
            //         console.log($(this));
            //         new_link = new_links[0];
            //         $.post(
            //             "./add",
            //             {
            //                 link: new_link['url'],
            //                 title: new_link['title'],
            //                 newlink: new_link['url'],
            //                 priority: new_link['priority'],
            //                 tags: new_link['tags'].join(' '),
            //                 description: new_link['description']
            //             }
            //         );
            //     },
            //     "Cancel": function() {
            //         $('#' + id).dialog('close');
            //     }
            // },
            show: {effect: 'fade', duration: 400},
            hide: {effect: 'fade', duration: 400}
        });
        $("#dialog-add-link input, #dialog-add-link textarea").bind('input', function(){
            adapt_form(input=this, add=true);
        });

        $("#dialog-add-link .tagit").tagit({
            // Options
            fieldName: "tags",
            availableTags: suggest_callback,
            autocomplete: {delay: 0, minLength: 1},
            showAutocompleteOnFocus: false,
            removeConfirmation: false,
            caseSensitive: true,
            allowDuplicates: false,
            allowSpaces: false,
            readOnly: !edit,
            tagLimit: null,
            singleField: false,
            singleFieldDelimiter: ',',
            singleFieldNode: null,
            tabIndex: null,
            placeholderText: null,
            afterTagAdded: function(evt, ui){
                if(edit == true) tag_update(evt, ui, remove=false, add=true);
            },
            beforeTagRemoved: function(evt, ui){
                if(edit == true) tag_update(evt, ui, remove=true, add=true);
            },
        });
    }
    return id;
}

// Delete a link
function del(button, link){
    table_tr = $(button).parents().eq(1);
    result_index = parseInt(table_tr[0].id.slice(8));
    create_root_node('dialog-confirm-deletion', 'Confirm deletion ?');
    var data = dialogs["dialog-confirm-deletion"].data();
    data.link = link;
    data.result_index = result_index;
    if(deleteDialog){
        dialogs["dialog-confirm-deletion"].dialog("open");
        return;
    }
    $.post(
        "./delete",
        {link: link}
    ).done(function(value){
        initial_links.splice(result_index, 1);
        links_status.splice(result_index, 1);
        new_links.splice(result_index, 1);
        show_links(_.clone(_.rest(initial_links)));
        $('#nb-links strong:first').text(nb_links - 1);
    }, "json");
}

// Update a link
function update(button, link){
    table_tr = $(button).parents().eq(5);
    result_index = parseInt(table_tr[0].id.slice(8));
    new_link = new_links[result_index];
    $.post(
        "./update",
        {
            link: link,
            title: new_link['title'],
            newlink: new_link['url'],
            priority: new_link['priority'],
            tags: new_link['tags'].join(' '),
            description: new_link['description']
        }
    ).done(function(value){
        links_status[result_index] = {
            'title': null, 'url': null, 'tags': null,
            'priority': null, 'description': null
        }
        initial_links[result_index] = _.clone(new_links[result_index]);
        // Update link visualisation
        html = show_link(result_index - 1, new_link, len, result_index);

        table_tr.replaceWith(html);
        // if properties on a link value was change
        var input_update;
        $("#responses input, #responses textarea").bind('input', function(){
            adapt_form(input=this, add=false);
        });

        $("#responses .tagit").tagit({
            // Options
            fieldName: "tags",
            availableTags: suggest_callback,
            autocomplete: {delay: 0, minLength: 1},
            showAutocompleteOnFocus: false,
            removeConfirmation: false,
            caseSensitive: true,
            allowDuplicates: false,
            allowSpaces: false,
            readOnly: !edit,
            tagLimit: null,
            singleField: false,
            singleFieldDelimiter: ',',
            singleFieldNode: null,
            tabIndex: null,
            placeholderText: null,
            afterTagAdded: function(evt, ui){
                if(edit == true) tag_update(evt, ui, remove=false, add=false);
            },
            beforeTagRemoved: function(evt, ui){
                if(edit == true) tag_update(evt, ui, remove=true, add=false);
            },
        });
        $('.readonly').tagit({
            readOnly: true
        });

        table = $($($(
            '#link_nb_' + parseInt(result_index)
        )[0].childNodes[1])[0].firstChild).after(
            '<small class="update">URL\'s properties update</small>'
        );
        update_message = table.next();
        setTimeout(function(){
            update_message.addClass('disappear');
        }, 1);
        setTimeout(function(){
            update_message.remove();
        }, 1000);
    }, "json");
}

// Reset : give initial link values
function reset(button, add){
    table_tr = $(button).parents().eq(5);
    if(add == true){
        result_index = 0;
    }
    else{
        result_index = parseInt(table_tr[0].id.slice(8));
    }
    new_links[result_index] = _.clone(initial_links[result_index]);
    links_status[result_index] = {
        'title': null, 'url': null, 'tags': null,
        'priority': null, 'description': null
    }
    if(result_index == 0) {
        $('#add-widget').replaceWith(original_add_widget.clone());
        $('#add-widget').removeClass('hidden');
        add_widget_event();
    }
    else{
        show_links(_.clone(_.rest(new_links)));
    }
}
// Show individual link
function show_link(l, link, len, inc){
    var url;
    var hidden = '';
    var url = link.url;
    var title = link.title;
    var tr = '<tr id="link_nb_<%= nb %>"><td><div><%= nb %></div></td><td>';
    tags = _.map(link.tags, function(value) { return '<li>' + value + '</li>'; }).join('');
    if(edit == true) {
        tr += '<table>';
        // TITLE
        var label = '<label>Title :</label></td><td>';
        if (title == '' && inc != 0){
            tr += '<tr class="has-warning"><td>' + label;
            tr += '<small>blank title (can be difficult to identify an URL)</small>';
        }
        else {
            tr += '<tr><td>' + label;
        }
        if(_.isNull(links_status[inc]['title'])){
            hidden = ' hidden';
        }
        tr += '<div class="input-update' + hidden +'"><div class="glyphicon glyphicon-refresh"></div></div>';
        tr += '<input class="form-control" value="<%= title %>"></input></td></tr>';

        // URL
        hidden = ' hidden';
        if(links_status[inc]['url'] == true){
            hidden = '';
        }
        if(links_status[inc]['url'] == false){
            tr += '<tr class="has-error"><td><label>Link :</label></td><td>';
            tr += '<small>URL invalid</small>';
        }
        else{
            tr += '<tr><td><label>Link :<sup> *</sup></label></td><td>';
        }
        tr += '<div class="input-update' + hidden +'"><div class="glyphicon glyphicon-refresh"></div></div>';
        tr += '<input class="form-control" type="url" value="<%= real_url %>"></input></td></tr>';

        // PRIORITY
        hidden = ' hidden';
        if(links_status[inc]['priority'] == true){
            hidden = '';
        }
        tr += '<tr><td><label>Priority order :<sup> *</sup></label></td>';
        tr += '<td><div class="input-update' + hidden + '"><div class="glyphicon glyphicon-refresh"></div></div>';
        tr += '<input type="number" data-show-clear="false" data-show-caption="true" value="<%= priority %>" class="rating" min="0" max="10" data-step="1" data-stars="10" data-size="xs" /></td></tr>';
        //tr += '<input class="form-control" type="number" min="1" max="10" value="<%= priority %>"></input></td></tr>';

        // TAGS
        hidden = ' hidden';
        if(links_status[inc]['tags'] == true){
            hidden = '';
        }
        tr += '<tr><td><label>Tags :<sup> *</sup></label></td><td>';
        has_error = '';
        if(links_status[inc]['tags'] == false){
            tr += '<small>requires at least one tag</small>';
            has_error = ' has-error';
        }
        tr += '<div class="tags-update' + hidden + '"><div class="glyphicon glyphicon-refresh"></div></div>';
        tr += '<ul class="tagit' + has_error + '">' + tags + '</ul>';
        tr += '</td></tr>';

        // DESCRIPTION
        hidden = ' hidden';
        if(links_status[inc]['description'] == true){
            hidden = '';
        }
        tr += '<tr class="last-tr"><td><label>Description :</label></td><td>';
        tr += '<div class="input-update' + hidden + '"><div class="glyphicon glyphicon-refresh"></div></div>';
        tr += '<textarea class="form-control"><%= description %></textarea></td></tr>';
        tr += '<tr class="hidden"><td></td><td>';

        tr += '<input class="add-or-update-button" onclick="update(this, \'<%= link %>\');" type="submit" value="update" />';
        tr += '<input class="reset-button" onclick="reset(this);" type="reset" value="reset" /></td></tr>';

        tr += '</table>';

        tr += '</td><td>';
        tr += '<button onclick="del(this, \'<%= link %>\');" title="delete" class="glyphicon glyphicon-minus">';
        tr += '</button></td></tr>';
    }
    else {
        tr += '<a href="<%= link %>"><%= title %></a>';
        if(url != link.real_url){
            tr += '<ul><li>Real URL : <strong><a href="<%= real_url %>"><%= real_url %></a></strong></li>';
        }
        tr += '<li>Priority order : <strong><%= priority %></strong></li>';
        tr += '<li><span>Tags :</span><ul class="readonly tagit">' + tags + '</ul></li>';
        tr += '<li>Description : <strong><%= description %></strong></li></ul>';
        if(title == '') {
            title = url;
        }
    }

    // $( "#create-user" ).button().on( "click", function() {
    //   dialog.dialog( "open" );
    // });
    real_url = link.real_url;
    if (!link.real_url){
        real_url = url;
    }
    return _.template(
        tr, {
            nb: l + 1, title: title,
            link: url, real_url: real_url,
            priority: link.priority,
            description: link.description
        }
    );
}
// Show Links : with edit mode or not
function show_links(links){
    var items = [];
    edit = $("#editmode").hasClass('active');
    // remove last searching results
    $("#search-list").remove();
    var len = _.size(links);
    var inc = 1;
    _.each(_.range(len).reverse(), function(l) {
        link = _.max(links, function(l){
            return parseInt(l.priority);
        });
        html = show_link(len - l - 1, link, len, inc);
        items.push(html);
        delete links[inc - 1];
        inc += 1;
    });
    //nb of results
    if (items.length == 0){
        $('#nb-results').text('no results');
        $('#nb-results').addClass('text-danger');
        $('#nb-results').removeClass('text-success');
        $('#searchbar-sucess').addClass('has-error');
        $('#searchbar-sucess').removeClass('has-success');
        $('.has-feedback .form-control-feedback').css('z-index', 1);
    }
    else {
        $('#nb-results').text(items.length + ' results');
        $('#nb-results').addClass('text-success');
        $('#nb-results').removeClass('text-danger');
        $('#searchbar-sucess').removeClass('has-error');
        $('#searchbar-sucess').addClass('has-success');
        $('.has-feedback .form-control-feedback').css('z-index', 3);
    }
    if(edit == false) {
        $('#add-widget').addClass('hidden');
    }
    // no results : don't show legend
    if(len == 0){return};
    // Results
    edit_class = '';
    $('#legend').addClass('hidden');
    if(edit == true) {
        edit_class = ' edit-table';
        $('#legend').removeClass('hidden');
    }
    $("<table/>", {
        "class": "table table-bordered table-striped" + edit_class,
        "id": "search-list",
        html: items.join("")
    }).appendTo("#responses");

    // if properties on a link value was change
    var input_update;
    $("#responses input, #responses textarea").bind('input', function(){
        adapt_form(input=this, add=false);
    });

    $("#responses .tagit").tagit({
        // Options
        fieldName: "tags",
        availableTags: suggest_callback,
        autocomplete: {delay: 0, minLength: 1},
        showAutocompleteOnFocus: false,
        removeConfirmation: false,
        caseSensitive: true,
        allowDuplicates: false,
        allowSpaces: false,
        readOnly: !edit,
        tagLimit: null,
        singleField: false,
        singleFieldDelimiter: ',',
        singleFieldNode: null,
        tabIndex: null,
        placeholderText: null,
        afterTagAdded: function(evt, ui){
            if(edit == true) tag_update(evt, ui, remove=false, add=false);
        },
        beforeTagRemoved: function(evt, ui){
            if(edit == true) tag_update(evt, ui, remove=true, add=false);
        },
    });
    $('.readonly').tagit({
        readOnly: true
    });
}

function tooltip(type, value){
    t = '<div class="tooltip top glyphicon glyphicon-<%= type %>-sign" role="tooltip">';
    t +=    '<div class="tooltip-arrow"></div>';
    t +=    '<div class="tooltip-inner">';
    t +=        '<%= value %>';
    t +=    '</div>';
    t += '</div>';
    return _.template(t, {type: type, value: value});
}

// Interactively show error(s)/warning(s)/update(s)
function adapt_form(input, add){
    var tr = $(input).parents().eq(1);
    var table_tr = tr.parents().eq(3);
    if(add){
        var result_index = 0;
    }
    else{
        var result_index = parseInt(table_tr[0].id.slice(8));
    }
    var error_help = $(input).parent().children().filter('small')[0];
    var input_update = $(input).parent().children().filter('.input-update');

    if ($(input).attr('type') == 'url'){
        links_status[result_index]['real_url'] = false;
        if(re_weburl.test($(input).val())){
            tr.removeClass('has-error');
            if(error_help != undefined){
                error_help.remove();
            }
            if(initial_links[result_index]['real_url'] == $(input).val()){
                input_update.addClass('hidden');
                links_status[result_index]['real_url'] = null;
            }
            else{
                links_status[result_index]['real_url'] = true;
                input_update.removeClass('hidden');
                input_update = $($(input).parent()[0].firstChild);
            }
        }
        else{
            if(error_help == undefined){
                input_update.addClass('hidden');
                input_update.before(tooltip('exclamation', 'URL invalid'));
            }
            tr.addClass('has-error');
            $(tr.parent()[0].lastChild).addClass('hidden');
        }
        new_links[result_index]['url'] = $(input).val();
    }
    else if($(input).attr('type') == 'number'){
        links_status[result_index]['priority'] = false;
        if(_.contains(_.range(1, 11), parseInt($(input).val()))){
            if(error_help != undefined){
                error_help.remove();
            }
            tr.removeClass('has-error');
            input_update.addClass('hidden');
            links_status[result_index]['priority'] = null;
            if(initial_links[result_index]['priority'] != $(input).val()){
                input_update.removeClass('hidden');
                links_status[result_index]['priority'] = true;
            }
        }
        else{
            tr.addClass('has-error');
            input_update.addClass('hidden');
            if(error_help == undefined){
                input_update.before(tooltip('exclamation', 'Invalid number (between 1 and 10)'));
            }
        }
        if($(input).val() != ''){
            new_links[result_index]['priority'] = $(input).val();
        }
    }
    else if($(input).get(0).tagName == 'TEXTAREA'){
        links_status[result_index]['description'] = true;
        input_update.removeClass('hidden');
        if(initial_links[result_index]['description'] == $(input).val()){
            input_update.addClass('hidden');
            links_status[result_index]['description'] = null;
        }
        new_links[result_index]['description'] = $(input).val();
    }
    else{
        links_status[result_index]['title'] = null;
        tr.removeClass('has-warning');
        if (error_help != undefined){
            error_help.remove();
        }
        input_update.addClass('hidden');
        if ($(input).val() == ''){
            if(error_help == undefined){
                input_update.before(tooltip('warning', 'can be difficult to identify an URL'));
                //input_update.before('<small>blank title (can be difficult to identify an URL)</small>');
            }
            tr.addClass('has-warning');
            if(initial_links[result_index]['title'] != ''){
                input_update.removeClass('hidden');
                links_status[result_index]['title'] = true;
            }
        }
        else if (initial_links[result_index]['title'] != $(input).val()){
            input_update.removeClass('hidden');
            links_status[result_index]['title'] = true;
        }
        new_links[result_index]['title'] = $(input).val();
    }
    if(add){
        tr = tr.parent().parent();
        console.log(tr);
        show_buttons(tr, result_index);
    }
    else{
        tr = tr.parent().children().filter(':last');
        show_buttons(tr, result_index);
    }
}

function show_buttons(tr, result_index){
    // Interactively show reset and validate buttons
    //var submit_button = tr.children().filter(':last').children().filter(':first');
    var submit_button = tr.children().filter('.add-or-update-button');
    var link_values = _.values(links_status[result_index]);
    tr.addClass('hidden');
    submit_button.addClass('hidden');
    if(link_values[1] != false && link_values[2] != false && link_values[3] != false) {
        submit_button.removeClass('hidden');
    }
    if (_.contains(link_values, true)){
        tr.removeClass('hidden');
    }
    if (_.contains(link_values, false)){
        tr.removeClass('hidden');
        submit_button.addClass('hidden');
        return;
    }
    if(
        result_index == 0
    ){
        submit_button.addClass('hidden');
        if(
            new_links[result_index]['url'] != ''
            && new_links[result_index]['tags'] != ''
        ){
            submit_button.removeClass('hidden');
        }
    }
}

function tag_update(evt, ui, remove, add){
    var tag_concern = ui.tag[0].firstChild.innerText;
    var ul_tagit = ui.tag.parent();
    var total = ul_tagit.children().length;
    var tr = ul_tagit.parents().eq(2).children().filter(':last');
    var table_tr = ul_tagit.parents().eq(5);
    if(add == true){
        var result_index = 0;
    }
    else{
        var result_index = parseInt(table_tr[0].id.slice(8));
    }
    var tags = Array();
    ul_tagit.children().each(function(i, j){
        tag = $(j)[0].firstChild.innerText;
        if(i != total - 1){
            tags.push(tag);
        }
    });
    tags = _.compact(tags);
    if (remove == true){
        tags = _.reject(tags, function(tag){ return tag == tag_concern ||  tag == 'No search results.'; });
    }
    inter = _.intersection(initial_links[result_index]['tags'], tags);
    var tag_up = $(ul_tagit.parent()[0].firstChild);
    links_status[result_index]['tags'] = null;
    if (tags.toString() == ''){
        $(ul_tagit).addClass('has-error');
        tag_up.before(tooltip('exclamation', 'requires at least one tag'));
        tag_up.addClass('hidden');
        links_status[result_index]['tags'] = false;
    }
    else if (inter.length != initial_links[result_index]['tags'].length
    || tags.length != initial_links[result_index]['tags'].length){
        $(ul_tagit).removeClass('has-error');

        var error_help = tag_up.parent()[0].firstChild;
        if (error_help.tagName == 'SMALL') {
            error_help.remove();
            $(ul_tagit.parent()[0].firstChild).removeClass('hidden');
        }
        else{
            tag_up.removeClass('hidden');
        }
        links_status[result_index]['tags'] = true;
    }
    else {
        $(ul_tagit).removeClass('has-error');
        tag_up.addClass('hidden');
    }
    new_links[result_index]['tags'] = tags;

    show_buttons($(tr), result_index);
}

function get_links(){
    var link = $('#searchform').attr('action');
    search_tags = $('.ui-autocomplete-input').val();
    $('#responses').addClass('hidden');
    $.ajax({
        url: link,
        data: search_tags,
        dataType: "json",
        // beforeSend: function(){
        //       $('#loading').show();
        //     },
        // }
    }).done(function(links) {
        $('#responses').removeClass('hidden');
        $('#nb-results').removeClass('hidden');
        add_link_status = _.clone(links_status[0]);
        links_status = [];
        links_status.push(add_link_status);
        initial_links = [];
        initial_links.push({
            'title': '', 'url': '', 'real_url': '',
            'tags': '', 'author': '',
            'priority': 1, 'description': ''
        });
        new_links = [];
        search_links = JSON.parse(JSON.stringify(links));
        len = _.size(search_links);
        _.each(_.range(len), function(l) {
            link = _.min(search_links, function(l){
                return parseInt(l.priority);
            });
            url = findKey(search_links, link);
            initial_links.push({
                'title': link.title, 'url': url, 'real_url': link.real_link,
                'tags': link.tags, 'author': link.author,
                'priority': link.priority, 'description': link.description
            });
            links_status.push({
                'title': null, 'url': null, 'tags': null,
                'priority': null, 'description': null
            });
            delete search_links[url];
        });
        // Deep copy
        new_links = JSON.parse(JSON.stringify(initial_links));
        show_links(_.clone(_.rest(initial_links)));
        $(".rating").rating({});
    });
    return false;
}

// Search Links
$('#searchform').bind('submit', get_links);


// AutoSuggestion
$.fn.LMSuggest = function(opts){
    opts = $.extend({service: 'web', secure: false}, opts);

    opts.source = function(request, response){
        $.ajax({
            url: './suggest',
            dataType: 'json',
            data: {
                tags: request.term,
            },
            success: function(data) {
                response($.map(data, function(item, val){
                    $('#searchbar-sucess').removeClass('has-error');
                    $('#searchbar-sucess').removeClass('has-success');
                    $('.has-feedback .form-control-feedback').css('z-index', 1);
                    return { value: $("<span>").html(val).text() };
                }));
            }
        });
    };
    return this.each(function(){
        $(this).autocomplete(opts);
    });
}

$("#searchbar").LMSuggest();

$("#searchbar").click(function() {
    $('#searchbar-sucess').removeClass('has-success');
    $('#searchbar-sucess').removeClass('has-error');
    $('.has-feedback .form-control-feedback').css('z-index', 1);
});


function suggest_callback(filter) {
    $.ajax({
        url: './suggest',
        dataType: 'json',
        async: false,
        data: {
            tags: filter,
        },
        success: function(data) {
            tags = data;
            return data;
        }
    });
    tags = _.keys(tags);
    tags = _.map(tags, function(value){ return value.replace(/\s+/g, ''); });
    return tags;
}

$("#myTags").tagit({
    // Options
    fieldName: "skills",
    availableTags: suggest_callback,
    autocomplete: {delay: 0, minLength: 1},
    showAutocompleteOnFocus: false,
    removeConfirmation: false,
    caseSensitive: true,
    allowDuplicates: false,
    allowSpaces: false,
    readOnly: false,
    tagLimit: null,
    singleField: false,
    singleFieldDelimiter: ',',
    singleFieldNode: null,
    tabIndex: null,
    placeholderText: null,
});

$(window).ready(function(){
    nb_links = parseInt($('#nb-links strong:first').text());
});
