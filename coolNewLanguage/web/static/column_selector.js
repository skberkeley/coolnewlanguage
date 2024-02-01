// Maps component ids to maps of {"table": table_name, "columns": Set([column_name, ...])}
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
    const full_table_div = document.getElementById(`column_select_full_table_${component_id}_table_${table_transient_id}`);
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
    node.classList.toggle(selected_class_name);
}

// Toggles a column as being selected or not selected within a column selector's full table view
// Adds the column name to the list of temporary choices for the relevant column
function toggle_column_selection(col_name, col_index, component_id, table_transient_id) {
    console.log(`toggle_column_selection: ${col_name}`)
    // query select all the cells in this column
    const col_cells = document.querySelectorAll(`#column_select_full_table_${component_id}_table_${table_transient_id} .col_${col_index}`);
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

function toggle_column_as_hovered(col_index, component_id, table_transient_id) {
    const col_cells = document.querySelectorAll(`#column_select_full_table_${component_id}_table_${table_transient_id} .col_${col_index}`);
    const hovered_class_name = "col_sel_hovered_column";
    for (const node of col_cells) {
        node.classList.add(hovered_class_name);
    }
}

function toggle_column_as_unhovered(col_index, component_id, table_transient_id) {
    const col_cells = document.querySelectorAll(`#column_select_full_table_${component_id}_table_${table_transient_id} .col_${col_index}`);
    const hovered_class_name = "col_sel_hovered_column";
    for (const node of col_cells) {
        node.classList.remove(hovered_class_name);
    }
}

function confirm_column_choices(component_id, transient_table_id) {
    // Moves transient column choices to confirmed column choices
    const transient_choices = temp_col_sel_choices.get(component_id);
    const table_name_input = document.getElementById(`input_${component_id}_table_name`);
    table_name_input.value = transient_choices.get("table");
    // Remove any existing column choice inputs
    const existing_col_choice_inputs = document.querySelectorAll(`input[name=${component_id}_columns]`);
    for (const input of existing_col_choice_inputs) {
        input.remove();
    }
    // Add new column choice inputs
    for (const col_choice of transient_choices.get("columns")) {
        const input = document.createElement("input");
        input.hidden = true;
        input.name = `${component_id}_columns`;
        input.value = col_choice;
        table_name_input.insertAdjacentElement("afterend", input);
    }
    // Clears transient column choices
    temp_col_sel_choices.delete(component_id);
    // Hides full table view
    hide_full_table(component_id, transient_table_id);
    // Show the confirmed choices
    const selected_table_p = document.getElementById(`col_sel_selected_table_${component_id}`);
    selected_table_p.hidden = false;
    selected_table_p.innerText = `Selected table: ${table_name_input.value}`;
    const selected_columns_p = document.getElementById(`col_sel_selected_columns_${component_id}`);
    selected_columns_p.hidden = false;
    const selected_columns = Array.from(transient_choices.get("columns")).join(", ");
    selected_columns_p.innerText = `Selected columns: ${selected_columns}`;
}