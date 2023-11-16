async function show_table(table_name, component_id) {
    // get the html for the table
    const response = await fetch(`/_get_table?table=${table_name}`);
    const table_html = await response.text();
    // if a table is already being shown, delete it from the dom
    const column_selector_div = document.getElementById(component_id);
    const next_element = column_selector_div.nextElementSibling;
    if (next_element.classList.contains("result_table")) {
        next_element.remove();
    }
    // inject the table into the dom
    column_selector_div.insertAdjacentHTML("afterend", table_html);
}