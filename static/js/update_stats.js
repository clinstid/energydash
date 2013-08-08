/* ==========================================================================
 * file: update_stats.js
 * description: Functions to update stats and charts for energydash web app.
 * ==========================================================================
 * Copyright 2013 Chris Linstid
 *  
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================================== */

function handle_current_state(data)
{
    // console.log(data);
    var response = jQuery.parseJSON(data);
    $("#current #current_text #usage").text(response.usage);
    $("#current #current_text #temp_f").text(response.temp_f);
    $("#current #current_text_title #date").text(response.date);
}

function handle_last_hour(data)
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
    window.charts["last_hour"] = $.plot("#last_hour_chart", plot_data, options);
}

function handle_last_7_days(data)
{
    var plot_data = jQuery.parseJSON(data);
    // console.log("Local timezone is %s", local_timezone);
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
    window.charts["last_7_days"] = $.plot("#last_7_days_chart", plot_data, options);
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

function update_last_hour()
{
    $.get(base_url + "last_hour", handle_last_hour);
}

function update_last_7_days()
{
    $.get(base_url + "last_7_days", handle_last_7_days);
}

function update_current_stats()
{
    $.get(base_url + "current_state", handle_current_state);
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
    update_last_hour();
    update_last_7_days();
    update_last_24_hours();
    update_dow();
    update_hod();
}
