/* ==========================================================================
 * file: main.js
 * description: Main javascript functions for energydash web app.
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

var charts = [];

function tab_select() 
{
    if ($(this).hasClass("tab_selected"))
    {
        return;
    }

    tab_in(this);
    tab_out(this);

    $(".tab_selected").removeClass("tab_selected").addClass("tab");
    $(this).removeClass("tab").addClass("tab_selected");
    $("#total_usage_div").css("display", "none");
    $("#daily_usage_div").css("display", "none");
    $("#monthly_usage_div").css("display", "none");
    var div_id = "#" + $(this).attr('id') + "_div";
    $(div_id).css("display", "block");
}

function tab_in() 
{
    if ($(this).hasClass("tab_selected"))
    {
        return;
    }

    $(this).css("cursor", "pointer");
}

function tab_out() 
{
    if ($(this).hasClass("tab_selected"))
    {
        return;
    }

    $(this).css("cursor", "auto");
}

function window_resize() 
{
    // If the window is resized, then we'll need to redraw the current chart.
    for (name in window.charts)
    {
        redraw_chart(name, window.charts[name]);
    }
}

function add_actions() 
{
    // Window
    $(window).resize(window_resize);

    // Tabs
    /*
    $(".tab").click(tab_select);
    $(".tab_selected").click(tab_select);
    $(".tab").hover(tab_in, tab_out);
    $(".tab_selected").hover(tab_in, tab_out);
    */
}

// main
$().ready(function() {
    // Initialize timezone-js
    timezoneJS.timezone.zoneFileBasePath = tz_url;
    timezoneJS.timezone.defaultZoneFile = ['northamerica'];
    timezoneJS.timezone.init({async: false});

    // Register action/event handlers.
    add_actions();

    // Only run updates on the current data every 30 seconds so we're not
    // hammering the server.
    var current_interval_id = window.setInterval(update_current_stats, 30000);
    var content_interval_id = window.setInterval(update_content_stats, 30000);

    // Update current stats and chart to get things rolling.
    update_current_stats();
    update_content_stats();
})
