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
    // console.log(usage_data);
    var plot_data = [{ 
                        color: "#33b5e5", 
                        data: usage_data
    }];
    // console.log("Local timezone is %s", local_timezone);
    var options = { 
                    series: 
                    { 
                        lines: 
                        { 
                            fillColor: "#004e6b", 
                            fill: false
                        },
                        highlightColor: "$33b5e5",
                    },
                    xaxis: 
                    { 
                        mode: "time", 
                        timezone: local_timezone,
                    },
                    grid:
                    {
                        borderColor: "rgb(235, 235, 235)",
                    },
    };
    window.current_chart_plot = $.plot("#current #current_chart", plot_data, options);
}

function redraw_chart(chart_plot)
{
    chart_plot.resize();
    chart_plot.setupGrid();
    chart_plot.draw();
}

function update_current_chart()
{
    $.get("/energymon/current_chart", handle_current_chart);
}

function update_current_stats()
{
    $.get("/energymon/current_state", handle_current_state);
    update_current_chart()
}

