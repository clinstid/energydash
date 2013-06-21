function handle_current_state(data)
{
    /*console.log(data);*/
    var response = jQuery.parseJSON(data);
    $("#current #current_text #date").text(response.date);
    $("#current #current_text #usage").text(response.usage);
    $("#current #current_text #temp_f").text(response.temp_f);
}

function handle_current_chart(data)
{
    var usage_data = jQuery.parseJSON(data);
    /* console.log(usage_data); */
    var plot_data = [ { color: "#33b5e5", data: usage_data } ];
    var options = { 
                    series: 
                    { 
                        lines: 
                        { 
                            fillColor: "#004e6b", 
                            fill: false, 
                        },
                        highlightColor: "$33b5e5",
                    },
                    xaxis: 
                    { 
                        mode: "time", 
                        timezone: "browser" 
                    },
                    grid:
                    {
                        borderColor: "black",
                    },
    };
    $.plot("#current #current_chart", plot_data, options);
}

function update_current_chart()
{
    $.get("/current_chart", handle_current_chart);
}

function update_current_stats()
{
    $.get("/current_state", handle_current_state);
    update_current_chart()
}

