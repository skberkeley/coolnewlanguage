async function show_table(table_name, component_id, context) {
    // get the html for the table
    const response = await fetch(`/_get_table?table=${table_name}&context=${context}&component_id=${component_id}`);
    const table_html = await response.text();
    // if a table is already being shown, delete it from the dom
    const table_selector_div = document.getElementById(`table_select_${component_id}`);
    const next_element = table_selector_div.nextElementSibling;
    if (next_element !== null && next_element.classList.contains("table_select_full_table")) {
        next_element.remove();
    }
    // inject the table into the dom
    table_selector_div.insertAdjacentHTML("afterend", table_html);
}

function hide_full_table(component_id) {
    // button is the button clicked to hide the table
    const full_table_div = document.getElementById(`table_select_full_table_${component_id}`);
    full_table_div.remove();
}

function confirm_table_choice(table_name, component_id) {
    // set the relevant input's value
    const input = document.getElementById(`input_${component_id}`);
    input.value = table_name;
    // hide the table
    hide_full_table(component_id);
}