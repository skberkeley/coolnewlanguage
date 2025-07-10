import glob
import os

import coolNewLanguage.src as hilt

from autotda.autofeat_class import TDA


autofeat = TDA()
autofeat.set_base_table(base_table="credit/table_0_0.csv", target_column="class")

tool = hilt.Tool('autotda')

HEATMAP_FILENAME = "heatmap.pdf"

def repository_selection():
    """
    Stage to select dataset repository and matcher
    """
    repositories = [name for name in os.listdir('./hci-auto-feat/data/benchmark')]
    repository = hilt.SelectorComponent(
        repositories, label="Select a dataset repository:"
    )
    matcher_names = ["Jaccard", "Coma"]
    matcher = hilt.SelectorComponent(
        matcher_names, label="Select a matcher:"
    )

    if tool.user_input_received():
        autofeat.set_dataset_repository(dataset_repository=[repository.value])
        autofeat.find_relationships(matcher=matcher.value.lower())
        autofeat.display_best_relationships()

        heat_map_content = hilt.UserContent(
            content_name="relationships", content_file_path=f"hci-auto-feat/{HEATMAP_FILENAME}", content_type=hilt.ContentTypes.PDF
        )
        tool.save_content(heat_map_content)
        hilt.results.show_results(heat_map_content, "Best relationships found:")


tool.add_stage('repository_selection', repository_selection)


def set_base_table():
    """
    Stage to set the base table and target column
    """
    base_table = hilt.SelectorComponent(
        autofeat.get_tables_repository(), label="Choose the base table"
    )
    target_column = hilt.UserInputComponent(
        str, label="Enter the target column name (e.g., 'class'):"
    )

    if tool.user_input_received():
        autofeat.set_base_table(base_table=base_table.value, target_column=target_column.value)
        hilt.results.show_results(f"Base table set to: {base_table.value} with target column: {target_column.value}")


tool.add_stage('set_base_table', set_base_table)


def compute_join_trees():
    """
    Stage to compute join trees based on the relationships found
    """
    non_null_ratio = hilt.UserInputComponent(
        float, label="Value in [0.0, 1.0], like 0.65"
    )
    top_k_features = hilt.UserInputComponent(
        int, label="Max number of features to select, like 15"
    )
    top_k_trees = hilt.UserInputComponent(
        int, label="Max number of trees to output, like 4. -1 for all"
    )

    if tool.user_input_received():
        tool.state['num_trees'] = top_k_trees.value

        autofeat.compute_join_trees(top_k_features=top_k_features.value, non_null_threshold=non_null_ratio.value)

        autofeat.display_join_trees(top_k=top_k_trees.value if top_k_trees.value != -1 else None)

        tree_contents = []
        for f in sorted(glob.glob("join_trees_*.pdf")):
            tree_id = f.split("join_trees_")[1].split(".pdf")[0]
            jointrees_content = hilt.UserContent(
                content_name=f"join_trees_{tree_id}", content_file_path=f,
                content_type=hilt.ContentTypes.PDF
            )
            tool.save_content(jointrees_content)
            tree_contents.append(jointrees_content)
        hilt.results.show_results(*tree_contents, results_title="Computed jointrees:")


tool.add_stage('compute_join_trees', compute_join_trees)


def choose_tree():
    """
    Stage to choose a join tree for further processing
    """
    sorted_trees = sorted(autofeat.trees, key=lambda x: x.rank, reverse=True)[:tool.state['num_trees']]
    for t in sorted_trees:
        content = hilt.UserContent(
            content_name=f"join_trees_{t.id}",
            content_file_name=f"join_trees_{t.id}.pdf",
            content_type=hilt.ContentTypes.PDF
        )
        hilt.PDFViewerComponent(content)
    tree_names = [str(t.id) for t in sorted_trees]
    selected_tree = hilt.SelectorComponent(
        tree_names, label="Select a join tree id to work with:"
    )

    if tool.user_input_received():
        tool.state['chosen_tree'] = selected_tree.value
        content = hilt.UserContent(
            content_name=f"join_trees_{selected_tree.value}",
            content_file_name=f"join_trees_{selected_tree.value}.pdf",
            content_type=hilt.ContentTypes.PDF
        )
        hilt.results.show_results(content, results_title="Selected join tree:")


tool.add_stage('choose_tree', choose_tree)

if __name__ == "__main__":
    tool.run()
