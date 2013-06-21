// Main
$().ready(function() {
    console.log("Document ready.");
    var interval_id = window.setInterval(update_current_stats, 5000);
    update_current_stats()
    update_current_chart()
});
