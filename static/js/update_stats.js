function handle_current_state(data)
{
    // console.log(data);
    var response = jQuery.parseJSON(data);
    $("#current #current_text #usage").text(response.usage);
    $("#current #current_text #temp_f").text(response.temp_f);
    $("#current #current_text_title #date").text(response.date);
}

function handle_current_chart(data)
{
    var usage_data = jQuery.parseJSON(data);
    var plot_data = [{ 
                        data: usage_data
    }];
    // console.log("Local timezone is %s", local_timezone);
    var options = { 
                    xaxis: 
                    { 
                        mode: "time", 
                        timezone: local_timezone,
                    },
                    grid:
                    {
                        autoHighlight: true,
                        hoverable: true,
                        borderColor: "rgb(235, 235, 235)",
                    },
    };
    window.charts["current_chart"] = $.plot("#current_chart", plot_data, options);
}

function handle_content_chart()
{
    console.log("%s", arguments.callee.name);
}

function handle_last_24_hours(data)
{
    var response = jQuery.parseJSON(data);
    var options = 
    { 
        legend:
        {
            position: "nw",
        },
        xaxis: 
        { 
            mode: "time", 
            timezone: local_timezone,
        },
        grid:
        {
            autoHighlight: true,
            hoverable: true,
            borderColor: "rgb(235, 235, 235)",
        },
        yaxes:
        [
            {},
            {
                position: "right"
            }
        ]
    };
    window.charts["last_24_hours_chart"] = $.plot("#last_24_hours_chart", 
                                                  response['chart_data'], 
                                                  options);

    $("#last_24_hours_usage_min").text(response.min_usage);
    $("#last_24_hours_usage_max").text(response.max_usage);
    $("#last_24_hours_usage_avg").text(response.avg_usage);
    $("#last_24_hours_tempf_min").text(response.min_tempf);
    $("#last_24_hours_tempf_max").text(response.max_tempf);
    $("#last_24_hours_tempf_avg").text(response.avg_tempf);
}

function redraw_chart(name, chart_plot)
{
    chart_plot.resize();
    chart_plot.setupGrid();
    chart_plot.draw();
}

function update_current_chart()
{
    $.get(base_url + "current_chart", handle_current_chart);
}

function update_current_stats()
{
    $.get(base_url + "current_state", handle_current_state);
    update_current_chart();
}

function handle_hod(data)
{
    var response = jQuery.parseJSON(data);
    // console.log(usage_data);
    var options = 
    { 
        legend:
        {
            position: "nw",
        },
        grid:
        {
            autoHighlight: true,
            hoverable: true,
            borderColor: "rgb(235, 235, 235)",
        },
        yaxes:
        [
            {},
            {
                position: "right"
            }
        ]
    };
                    
    window.charts["hod"] = $.plot("#hod_chart", response, options);
}

function update_hod()
{
    $.get(base_url + "hod", handle_hod);
}

function handle_dow(data)
{
    var response = jQuery.parseJSON(data);
    // console.log(usage_data);
    var options = 
    { 
        legend:
        {
            position: "nw",
            noColumns: 7
        },
        grid:
        {
            autoHighlight: true,
            hoverable: true,
            borderColor: "rgb(235, 235, 235)",
        },
    };
                    
    window.charts["dow"] = $.plot("#dow_chart", response, options);
}

function update_dow()
{
    $.get(base_url + "dow", handle_dow);
}

function update_last_24_hours()
{
    $.get(base_url + "last_24_hours", handle_last_24_hours);
}

function update_content_stats()
{
    update_last_24_hours();
    update_dow();
    update_hod();
}
