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
var menu_is_on = false;

function menu_off(menu)
{
    var menu = $(".header_menu");
    menu.css("display", "none");
    window.menu_is_on = false;
    menu_img_normal();
}

function update_menu_position()
{
    var menu = $(".header_menu");
    new_left = $("div#header_menu_button").offset().left;
    menu.css("left", new_left);
    console.log("Moving menu to %d", new_left);
}

function menu_on(event)
{
    var menu = $(".header_menu");
    menu.css("display", "block");
    update_menu_position(menu);
    window.menu_is_on = true;
    menu_img_hl();
    event.stopPropagation();
}

function turn_menu_off_if_on()
{
    if (window.menu_is_on)
    {
        menu_off();
    }
}

function menu_toggle(event)
{
    if (window.menu_is_on)
    {
        menu_off();
    }
    else
    {
        menu_on(event);
    }
}

function menu_img_hl()
{
    $("img#header_menu_img").attr("src", images_url + "/menu_highlighted.png");
    $("div#header_menu_button").css("background", "rgb(82, 82, 82)");
}

function menu_img_normal()
{
    if (!window.menu_is_on)
    {
        $("img#header_menu_img").attr("src", images_url + "/menu.png");
        $("div#header_menu_button").css("background", "rgb(63, 63, 63)");
    }
}

function window_resize() 
{
    // Just in case the menu is active, fix its position.
    update_menu_position()

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

    // Setup menu
    $("div#header_menu_button").hover(menu_img_hl, menu_img_normal);
    $("div#header_menu_button").click(menu_toggle);
    $("body").click(turn_menu_off_if_on);
    //$("div#header").click(turn_menu_off_if_on);
    //$("div.header_menu").click(turn_menu_off_if_on);

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
