function table_selector_update_column_selectors(table_selector_id, 
    column_selector_ids) {
        //screaming, crying, throwing up
        let table_column_map = JSON.parse(
            document.getElementById(
                table_selector_id + "_table_column_map"
            ).innerText
        );

        let table_selector = document.getElementById(table_selector_id);
        let column_selectors = column_selector_ids.map(id =>
            document.getElementById(id)  
        );

        let columns = table_column_map[table_selector.value];
        for (let column_selector of column_selectors) {
            /* Remove all but the default "select a column" row */
            column_selector.options.length = 1;

            for (let column of columns) {
                column_selector.add(new Option(column, column));
            }
            column_selector.hidden = false;
        }

        console.log(table_selector)
        console.log(column_selectors)
}