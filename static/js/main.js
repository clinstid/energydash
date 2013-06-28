function tab_select() {
    if ($(this).hasClass("tab_selected"))
    {
        return;
    }

    tab_in(this);
    tab_out(this);

    $(".tab_selected").removeClass("tab_selected").addClass("tab");
    $(this).removeClass("tab").addClass("tab_selected");
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

function add_actions() {
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
    update_current_chart();
});
