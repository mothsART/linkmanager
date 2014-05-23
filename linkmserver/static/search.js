// find key by value on an associate array
function findKey(obj, value) {
  var key;
  _.each(obj, function (v, k) {
    if (v === value) {
      key = k;
    }
  });
  return key;
}

// Search Links
$('#searchform').bind('submit', function(event) {
    var link = $(this).attr('action');

    $.ajax({
        url: link,
        type: "POST",
        data: $('.ui-autocomplete-input').val(),
        dataType: "json",
        // beforeSend: function(){
        //       $('#loading').show();
        //     },
        // }
    }).done(function(links) {
        // remove last searching results
        $("#search-list").remove();
        len = _.size(links);
        var items = [];

        _.each(_.range(len), function(l) {
            var url;
            link = _.min(links, function(l){
                return parseInt(l.priority);
            });
            url = findKey(links, link);
            console.log(link);
            console.log(url);
            var title = link.title;
            if (title == '') {
                title = url;
            }
            var li = '<tr><td><%= nb %></td>';
            li += '<td><a href="<%= link %>"><%= title %></a>';
            li += '<ul><li>ordre de priorité : <strong><%= priority %></strong></li>'
            li += '<li>tags : <strong><%= tags %></strong></li>'
            li += '<li>description : <strong><%= description %></strong></li>'
            li += '</ul></td></tr>';
            items.push(_.template(
                li, {
                    nb: l + 1,
                    link: url, title: title,
                    priority: link.priority,
                    tags: link.tags,
                    description: link.description
                }
            ));
            delete links[url];
        });

        //nb of results
        if (items.length == 0){
            $('#nb-results').text('no results');
            $('#searchbar-sucess').removeClass('has-success');
            $('.has-feedback .form-control-feedback').css('z-index', 1);
        }
        else {
            $('#nb-results').text(items.length + ' results');
            $('#searchbar-sucess').addClass('has-success');
            $('.has-feedback .form-control-feedback').css('z-index', 3);
        }
        // Results
        $( "<table/>", {
            "class": "table table-bordered table-striped",
            "id": "search-list",
            html: items.join("")
        }).appendTo("#responses");
    });

    return false;
});


// AutoSuggestion
$.fn.LMSuggest = function(opts){
    opts = $.extend({service: 'web', secure: false}, opts);

    opts.source = function(request, response){
        $.ajax({
            url: '/suggest',
            dataType: 'json',
            data: {
                tags: request.term,
            },
            success: function(data) {
                response($.map(data, function(item, val){
                    //console.debug(val, item);
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

$("input").LMSuggest();

$("#searchbar" ).click(function() {
    $('#searchbar-sucess').removeClass('has-success');
    $('.has-feedback .form-control-feedback').css('z-index', 1);
});
