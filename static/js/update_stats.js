function handle_current_state(data)
{
    console.log(data);
    response = jQuery.parseJSON(data);
    $("#footer #date").text(response.date);
    $("#footer #usage").text(response.usage);
    $("#footer #temp_f").text(response.temp_f);
}

function update_current_stats()
{
    $.get("/current_state", handle_current_state);
}
