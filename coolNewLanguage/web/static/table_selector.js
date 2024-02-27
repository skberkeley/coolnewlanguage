async function table_sel_show_table(table_name, component_id, context, table_transient_id) {
    // get the html for the table
    console.log(table_transient_id)
    const response = await fetch(`/_get_table?table=${table_name}&context=${context}&component_id=${component_id}&table_transient_id=${table_transient_id}`);
    const table_html = await response.text();
    // if a table is already being shown, unstyle its preview and delete it from the dom
    const table_selector_div = document.getElementById(`table_select_${component_id}`);
    const next_element = table_selector_div.nextElementSibling;
    if (next_element !== null && next_element.classList.contains("table_select_full_table")) {
        next_element.remove();
        // get the preview element and unstyle it
        const table_preview = table_selector_div.querySelector("button.table_select_button_selected");
        table_preview.classList.remove("table_select_button_selected");
    }
    // inject the table into the dom
    table_selector_div.insertAdjacentHTML("afterend", table_html);
    // style the preview of the table which was selected
    table_sel_style_table_preview_as_selected(component_id, table_transient_id);
}

function table_sel_hide_full_table(component_id, table_transient_id) {
    const full_table_div = document.getElementById(`table_select_full_table_${component_id}_table_${table_transient_id}`);
    full_table_div.remove();
    // unstyle the preview of the table as selected
    const button = table_sel_get_table_select_button(component_id, table_transient_id);
    button.classList.remove("table_select_button_selected");
}

function table_sel_confirm_table_choice(table_name, component_id, table_transient_id) {
    // set the relevant input's value
    const input = document.getElementById(`input_${component_id}`);
    input.value = table_name;
    // get all table preview checkboxes
    const table_preview_checkboxes = document.querySelectorAll(`input.table_preview_checkbox[data-component-id="${component_id}"]`);
    // check/uncheck them appropriately
    for (const tablePreviewCheckbox of table_preview_checkboxes) {
        tablePreviewCheckbox.checked = tablePreviewCheckbox.id === `table_preview_checkbox_${table_transient_id}_${component_id}`;
    }
    // hide the table
    table_sel_hide_full_table(component_id, table_transient_id);
}

function table_sel_style_table_preview_as_selected(component_id, table_id) {
    // find the dom element to style
    const button = table_sel_get_table_select_button(component_id, table_id);
    // style it
    button.classList.add("table_select_button_selected");
}

function table_sel_get_table_select_button(component_id, table_transient_id) {
    const table_select_div_id = `table_select_${component_id}_table_${table_transient_id}`;
    const table_select_div = document.getElementById(table_select_div_id);
    return table_select_div.querySelector("button.table_select_button");
}
