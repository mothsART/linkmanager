var search_links;
var initial_links = [];
initial_links.push({
    'title': '', 'url': '',
    'tags': '',
    'priority': 1, 'description': ''
});
var links_status = [];
links_status.push({
    'title': null, 'url': null, 'tags': null,
    'priority': null, 'description': null
});
var new_links = JSON.parse(JSON.stringify(initial_links));

$("#add-widget input, #add-widget textarea").bind('input', function(){
    adapt_form(input=this, add=true);
});
$(".tagit").tagit({
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
// URL identifier
// see https://gist.github.com/dperini/729294 and http://mathiasbynens.be/demo/url-regex
// same as http://bootstrapvalidator.com
var re_weburl = new RegExp(
  "^" +
    // protocol identifier
    "(?:(?:https?|ftp)://)" +
    // user:pass authentication
    "(?:\\S+(?::\\S*)?@)?" +
    "(?:" +
      // IP address exclusion
      // private & local networks
      "(?!(?:10|127)(?:\\.\\d{1,3}){3})" +
      "(?!(?:169\\.254|192\\.168)(?:\\.\\d{1,3}){2})" +
      "(?!172\\.(?:1[6-9]|2\\d|3[0-1])(?:\\.\\d{1,3}){2})" +
      // IP address dotted notation octets
      // excludes loopback network 0.0.0.0
      // excludes reserved space >= 224.0.0.0
      // excludes network & broacast addresses
      // (first & last IP address of each class)
      "(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])" +
      "(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}" +
      "(?:\\.(?:[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))" +
    "|" +
      // host name
      "(?:(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)" +
      // domain name
      "(?:\\.(?:[a-z\\u00a1-\\uffff0-9]-*)*[a-z\\u00a1-\\uffff0-9]+)*" +
      // TLD identifier
      "(?:\\.(?:[a-z\\u00a1-\\uffff]{2,}))" +
    ")" +
    // port number
    "(?::\\d{2,5})?" +
    // resource path
    "(?:/\\S*)?" +
  "$", "i"
);

// find key by value on an associate array
function findKey(obj, value){
  var key;
  _.each(obj, function (v, k){
    if (v === value){
      key = k;
    }
  });
  return key;
}

// GET Edit mode
$.ajax({
    url: 'editmode',
    type: "GET",
    dataType: "json",
}).done(function(value){
    if(value['editmode'] == true){
        $('#editmode').addClass('active');
    }
});

// Change Edit Mode
$("#editmode").click(function(){
    $.post(
        "editmode",
        {editmode: $(this).hasClass('active')}
    ).done(function(value){
        if(value['editmode'] == true){
            $('#editmode').addClass('active');
            $('.glyphicon-plus').removeClass('hidden');
            $('td:nth-child(3)').removeClass('hidden');
            _.map(links_status, function(key){
                key['priority'] = null;
                return key;
            });
            show_links(_.clone(_.rest(new_links)));
        }
        else {
            $('#editmode').removeClass('active');
            $('.glyphicon-plus').addClass('hidden');
            $('td:nth-child(3)').addClass('hidden');
            show_links(_.clone(_.rest(initial_links)));
        }
    }, "json");
});

// show an add widget
function add_widget(){
    if(!$('#add-widget').hasClass('hidden')){
        $('#add-widget').addClass('hidden');
        return;
    }
    $('#add-widget').removeClass('hidden');
}

// Add a link
function add(button, link){
    console.log('add');
}

// Delete a link
function del(button, link){
    table_tr = $(button).parents().eq(1);
    result_index = parseInt(table_tr[0].id.slice(8));
    $.post(
        "delete",
        {link: link}
    ).done(function(value){
        initial_links.splice(result_index, 1);
        links_status.splice(result_index, 1);
        new_links.splice(result_index, 1);
        show_links(_.clone(initial_links));
    }, "json");
}

// Update a link
function update(button, link){
    table_tr = $(button).parents().eq(5);
    result_index = parseInt(table_tr[0].id.slice(8));
    new_link = new_links[result_index];
    $.post(
        "update",
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
        show_links(_.clone(initial_links));
        table = $($($(
            '#link_nb_' + parseInt(result_index + 1)
        )[0].childNodes[1])[0].firstChild).after(
            '<small class="update">URL\'s properties update</small>'
        );
        update_message = table.next();
        setTimeout(function(){
            update_message.addClass('disappear');
        }, 1);
        setTimeout(function(){
            update_message.remove();
        }, 2000);
    }, "json");
}

// Reset : give initial link values
function reset(button, add){
    table_tr = $(button).parents().eq(5);
    console.log(add);
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
    show_links(_.clone(_.rest(new_links)));
}

// Show Links : with edit mode or not
function show_links(links){
    var items = [];
    edit = $("#editmode").hasClass('active');
    // remove last searching results
    $("#search-list").remove();
    var len = _.size(links);
    var inc = 0;
    _.each(_.range(len), function(l) {
        var url;
        link = _.min(links, function(l){
            return parseInt(l.priority);
        });
        var hidden = '';
        var url = link.url;
        var title = link.title;
        var tr = '<tr id="link_nb_<%= nb %>"><td><%= nb %></td><td>';
        tags = _.map(link.tags, function(value) { return '<li>' + value + '</li>'; }).join('');
        if(edit == true) {
            tr += '<table>';
            // TITLE
            var label = '<label>Title :</label></td><td>';
            if (title == ''){
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
            tr += '<input class="form-control" type="url" value="<%= link %>"></input></td></tr>';

            // PRIORITY
            hidden = ' hidden';
            if(links_status[inc]['priority'] == true){
                hidden = '';
            }
            tr += '<tr><td><label>Priority order :<sup> *</sup></label></td>';
            tr += '<td><div class="input-update' + hidden + '"><div class="glyphicon glyphicon-refresh"></div></div>';
            tr += '<input class="form-control" type="number" min="1" max="10" value="<%= priority %>"></input></td></tr>';

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
            tr += '<tr class="hidden"><td></td><td><input onclick="update(this, \'<%= link %>\');" type="submit" value="update" />';
            tr += '<input onclick="reset(this);" type="reset" value="reset" /></td></tr>';
            tr += '</table>';

            tr += '</td><td>';
            tr += '<button onclick="del(this, \'<%= link %>\');" title="delete" class="glyphicon glyphicon-minus">';
            tr += '</button></td></tr>';
        }
        else {
            $('#add-widget').addClass('hidden');
            tr += '<a href="<%= link %>"><%= title %></a>';
            tr += '<ul><li>Ordre de priorité : <strong><%= priority %></strong></li>';
            tr += '<li><span>Tags :</span><ul class="readonly tagit">' + tags + '</ul></li>';
            tr += '<li>Description : <strong><%= description %></strong></li></ul>';
            if(title == '') {
                title = url;
            }
        }
        html = _.template(
            tr, {
                nb: l + 1,
                link: url, title: title,
                priority: link.priority,
                description: link.description
            }
        )
        items.push(html);
        delete links[inc];
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

// Interactively show error(s)/warning(s)/update(s) and reset/submit buttons
function adapt_form(input, add){
    var tr = $(input).parents().eq(1);
    var table_tr = tr.parents().eq(3);
    if(add == true){
        var result_index = 0;
    }
    else{
        var result_index = parseInt(table_tr[0].id.slice(8));
    }
    var error_help = $(input).parent().children().filter('small')[0];
    var input_update = $(input).parent().children().filter('.input-update');

    if ($(input).attr('type') == 'url'){
        links_status[result_index]['url'] = false;
        if(re_weburl.test($(input).val())){
            tr.removeClass('has-error');
            if(error_help != undefined){
                error_help.remove();
            }
            if(initial_links[result_index]['url'] == $(input).val()){
                input_update.addClass('hidden');
                links_status[result_index]['url'] = null;
            }
            else{
                links_status[result_index]['url'] = true;
                input_update.removeClass('hidden');
                input_update = $($(input).parent()[0].firstChild);
            }
        }
        else{
            if(error_help == undefined){
                input_update.addClass('hidden');
                input_update.before('<small>URL invalid</small>');
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
                input_update.before('<small>Invalid number (between 1 and 10)</small>');
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
                input_update.before('<small>blank title (can be difficult to identify an URL)</small>');
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
    tr = tr.parent().children().filter(':last');
    show_buttons(tr, result_index);
}

function show_buttons(tr, result_index){
    //Show reset and validate buttons
    var submit_button = tr.children().filter(':last').children().filter(':first');
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
    }
    console.log(link_values);
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
    console.log(add);
    console.log(result_index);
    console.log(tags);
    inter = _.intersection(initial_links[result_index]['tags'], tags);
    var tag_up = $(ul_tagit.parent()[0].firstChild);
    links_status[result_index]['tags'] = null;
    if (tags.toString() == ''){
        $(ul_tagit).addClass('has-error');
        tag_up.before('<small>requires at least one tag</small>');
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

// Search Links
$('#searchform').bind('submit', function(event) {
    var link = $(this).attr('action');

    $.ajax({
        url: link,
        data: $('.ui-autocomplete-input').val(),
        dataType: "json",
        // beforeSend: function(){
        //       $('#loading').show();
        //     },
        // }
    }).done(function(links) {
        console.log(initial_links);
        initial_links = [];
        initial_links.push({
            'title': '', 'url': '',
            'tags': '',
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
                'title': link.title, 'url': url,
                'tags': link.tags,
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
    });
    return false;
});


// AutoSuggestion
$.fn.LMSuggest = function(opts){
    opts = $.extend({service: 'web', secure: false}, opts);

    opts.source = function(request, response){
        $.ajax({
            url: 'suggest',
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
        url: 'suggest',
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
