var current_chart_plot;

function tab_select() {
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
};

function tab_in() {
    if ($(this).hasClass("tab_selected"))
    {
        return;
    }

    $(this).css("cursor", "pointer");
};

function tab_out() {
    if ($(this).hasClass("tab_selected"))
    {
        return;
    }

    $(this).css("cursor", "auto");
};

function window_resize() {
    // If the window is resized, then we'll need to redraw the current chart.
    redraw_chart(window.current_chart_plot);

    // TODO Need to also update anything else that we're drawing... when we're
    // drawing it anyway.
}

function add_actions() {
    // Window
    $(window).resize(window_resize);

    // Tabs
    $(".tab").click(tab_select);
    $(".tab_selected").click(tab_select);
    $(".tab").hover(tab_in, tab_out);
    $(".tab_selected").hover(tab_in, tab_out);
};

// main
$().ready(function() {
    // Register action/event handlers.
    add_actions();

    // Only run updates on the current data every 30 seconds so we're not
    // hammering the server.
    var interval_id = window.setInterval(update_current_stats, 30000);

    // Initialize timezone-js
    timezoneJS.timezone.zoneFileBasePath = "energymon/static/tz";
    timezoneJS.timezone.init();

    // Update current stats and chart to get things rolling.
    update_current_stats();
});
