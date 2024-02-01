let temp_col_sel_choices = new Map();

async function show_table(table_name, component_id, context, table_transient_id) {
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
    style_table_preview_as_selected(component_id, table_transient_id);
    // add the table being shown as the temporary table choice for the component being interacted
    temp_col_sel_choices.set(component_id, new Map());
    temp_col_sel_choices.get(component_id).set("table", table_name);
}

function hide_full_table(component_id, table_transient_id) {
    const full_table_div = document.getElementById(`table_select_full_table_${component_id}_table_${table_transient_id}`);
    full_table_div.remove();
    // unstyle the preview of the table as selected
    const button = get_table_select_button(component_id, table_transient_id);
    button.classList.remove("table_select_button_selected");
}

function style_table_preview_as_selected(component_id, table_id) {
    // find the dom element to style
    const button = get_table_select_button(component_id, table_id);
    // style it
    button.classList.add("table_select_button_selected");
}

function get_table_select_button(component_id, table_transient_id) {
    const table_select_div_id = `table_select_${component_id}_table_${table_transient_id}`;
    const table_select_div = document.getElementById(table_select_div_id);
    return table_select_div.querySelector("button.table_select_button");
}

function toggle_table_cell_selected_status(node) {
    const selected_class_name = "col_sel_selected_column";
    if (node.classList.contains(selected_class_name)) {
        node.classList.remove(selected_class_name);
    } else {
        node.classList.add(selected_class_name);
    }
}

// Toggles a column as being selected or not selected within a column selector's full table view
// Adds the column name to the list of temporary choices for the relevant column
function toggle_column_selection(col_name, col_index, component_id) {
    console.log(`toggle_column_selection: ${col_name}`)
    // query select all the cells in this column
    const col_cells = document.querySelectorAll(`th.col_${col_index}, td.col_${col_index}`)
    // toggle them as being selected
    for (const node of col_cells) {
        toggle_table_cell_selected_status(node);
    }
    // add the column name to the list of temporary choices
    const temp_choices = temp_col_sel_choices.get(component_id);
    if (temp_choices.has("columns")) {
        const columns = temp_choices.get("columns");
        if (columns.has(col_name)) {
            columns.delete(col_name);
        } else {
            columns.add(col_name);
        }
    } else {
        temp_choices.set("columns", new Set([col_name]));
    }
}