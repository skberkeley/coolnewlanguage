async function show_table(table_name, component_id) {
    // get the html for the table
    const response = await fetch(`/_get_table?table=${table_name}`);
    const table_html = await response.text();
    // inject it into the dom
    const column_selector_div = document.getElementById(component_id);
    column_selector_div.insertAdjacentHTML("afterend", table_html);
}