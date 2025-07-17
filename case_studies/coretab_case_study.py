import coolNewLanguage.src as hilt
from copy import deepcopy
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px
from sklearn.model_selection import train_test_split
from coretab.coreset_algorithms import CoreTabDT, CoreTabXGB
from coretab.tree_plot_utils import plot_coreset, search_for_leaves_with_feature
tool = hilt.Tool('coretab')
CORETAB_DTS = {}
def dataset_upload():
    """
    Stage to upload a dataset for processing
    """
    dataset_name = hilt.UserInputComponent(str, label="Enter a name for the dataset:")
    uploaded_dataset = hilt.FileUploadComponent(
        '.csv', label="Upload a dataset to process:"
    )
    if tool.user_input_received():
        df = pd.read_csv(uploaded_dataset.value)
        tool.tables[dataset_name.value] = df
tool.add_stage('dataset_upload', dataset_upload)
def compute_coreset():
    # normally we could use a ColumnSelectorComponent here, but the coretab demo dataset is huge, ~150MB of csv
    table_name = hilt.UserInputComponent(str, label="Enter the name of the dataset to use for coreset computation:")
    target_col_name = hilt.UserInputComponent(str, label="Enter the target column name for the dataset:")
    coretab_size = hilt.UserInputComponent(int, label="Enter the number of examples to keep for the coreset:")
    coretab_name = hilt.UserInputComponent(str, label="Enter a name for the coreset:")
    if tool.user_input_received():
        df = tool.tables[table_name.value]
        target_col = target_col_name.value
        X_train, X_test, y_train, y_test = train_test_split(
            df.drop(target_col, axis=1),
            df[target_col],
            test_size=0.2,
            shuffle=True
        )
        coretab_dt = CoreTabDT(examples_to_keep=coretab_size.value)
        X_coreset, y_coreset = coretab_dt.create_coreset(X_train, y_train)
        CORETAB_DTS[coretab_name.value] = coretab_dt
        tool.state['X_train'] = X_train
        tool.state['X_test'] = X_test
        tool.state['y_train'] = y_train
        tool.state['y_test'] = y_test
        tool.state['X_coreset'] = X_coreset
        tool.state['y_coreset'] = y_coreset
        plot_coreset(coretab_dt)
        plt.savefig('coreset_plot.jpg', dpi=300, bbox_inches='tight')
        coreset_content = hilt.UserContent(
            content_name="coreset_plot",
            content_file_path='coreset_plot.jpg',
            content_type=hilt.ContentTypes.JPG
        )
        tool.save_content(coreset_content)
        hilt.results.show_results(coreset_content, "Coreset computed and visualized.")
tool.add_stage('compute_coreset', compute_coreset)
# copied from coretab demo.ipynb
def print_precision_recall_guarantees(coretab_dt):
    df_0, df_1 = coretab_dt.get_guarantees(tool.state['X_test'], tool.state['y_test'])
    if df_1 is not None:
        df_vis = pd.concat([df_0.assign(metric='recall', delta_metric=df_0['delta_recall']),
                            df_1.assign(metric='precision', delta_metric=df_1['delta_precision'])])
    else:
        df_vis = df_0.assign(metric='recall', delta_metric=df_0['delta_recall'])
    df_vis.rename(columns={'delta_metric': 'Performace Decrease', 'percent_remained': 'Coreset size'}, inplace=True)
    fig = px.line(df_vis, x='Coreset size', y='Performace Decrease', title='Metrics Decrease vs. Coreset size',
              hover_data='group_id', color='metric', markers=True)
    return fig
def see_precision_recall_guarantees():
    coretab_name = hilt.SelectorComponent(list(CORETAB_DTS.keys()), label="Select the coreset to see precision/recall guarantees:")
    if tool.user_input_received():
        coretab_dt = CORETAB_DTS[coretab_name.value]
        fig = print_precision_recall_guarantees(coretab_dt)
        fig.write_image('coreset_performance.pdf')
        coreset_content = hilt.UserContent(
            content_name="coreset_performance",
            content_file_path='coreset_performance.pdf',
            content_type=hilt.ContentTypes.PDF
        )
        tool.save_content(coreset_content)
        hilt.results.show_results(coreset_content, results_title="Coreset performance guarantees:")
tool.add_stage('see_precision_recall_guarantees', see_precision_recall_guarantees)
# from demo.ipynb
def get_coreset_with_nodes(coretab_dt: CoreTabDT, nodes_to_add: list):
    coretab_dt_copy = deepcopy(coretab_dt)
    coretab_dt_copy.hom_groups_candidates = [c for c in coretab_dt_copy.hom_groups_candidates if not c.key in nodes_to_add]
    coretab_dt_copy.hom_groups = dict()
    coretab_dt_copy.choose_groups(tool.state['y_train'])
    coretab_dt_copy.manually_added_nodes = nodes_to_add
    return coretab_dt_copy
def get_coreset_with_feature(coretab_dt: CoreTabDT, feature_to_add: str):
    nodes_with_feature = search_for_leaves_with_feature(coretab_dt, feature_to_add)
    return get_coreset_with_nodes(coretab_dt, nodes_with_feature)
def add_feature_to_coreset():
    coretab_name = hilt.SelectorComponent(list(CORETAB_DTS.keys()), label="Select the coreset to add a feature to:")
    feature_name = hilt.UserInputComponent(str, label="Enter the name of the feature to add to the coreset:")
    new_coretab_name = hilt.UserInputComponent(str, label="Enter the name of the resulting coreset:")
    if tool.user_input_received():
        if feature_name.value not in CORETAB_DTS[coretab_name.value].columns:
            hilt.results.show_results("Feature not found in the coreset's columns.")
            return
        coretab_dt = get_coreset_with_feature(CORETAB_DTS[coretab_name.value], feature_name.value)
        CORETAB_DTS[new_coretab_name.value] = coretab_dt
        plot_coreset(coretab_dt)
        plt.savefig('coreset_feature_plot.jpg', dpi=300, bbox_inches='tight')
        coreset_content = hilt.UserContent(
            content_name="coreset_feature_plot",
            content_file_path='coreset_feature_plot.jpg',
            content_type=hilt.ContentTypes.JPG
        )
        tool.save_content(coreset_content)
        hilt.results.show_results(coreset_content, "Feature added to coreset and visualized.")
tool.add_stage('add_feature_to_coreset', add_feature_to_coreset)
# adapted from demo.ipynb
def coretab_without_leaves(coretab_dt: CoreTabDT, leaves_to_remove: list):
    coretab_copy = deepcopy(coretab_dt)
    coretab_copy.hom_groups_candidates = [c for c in coretab_copy.hom_groups_candidates if not c.key in leaves_to_remove]
    coretab_copy.hom_groups = dict()
    coretab_copy.choose_groups(tool.state['y_train'])
    return coretab_copy
def coretab_without_feature(coretab_dt: CoreTabDT, feature_to_remove):
    leaves_with_feature = search_for_leaves_with_feature(coretab_dt, feature_to_remove)
    return coretab_without_leaves(coretab_dt, leaves_with_feature)
def remove_feature_from_coreset():
    coretab_name = hilt.SelectorComponent(list(CORETAB_DTS.keys()), label="Select the coreset to remove a feature from:")
    feature_name = hilt.UserInputComponent(str, label="Enter the name of the feature to remove from the coreset:")
    new_coretab_name = hilt.UserInputComponent(str, label="Enter the name of the resulting coreset:")
    if tool.user_input_received():
        if feature_name.value not in CORETAB_DTS[coretab_name.value].columns:
            hilt.results.show_results("Feature not found in the coreset's columns.")
            return
        coretab_dt = coretab_without_feature(CORETAB_DTS[coretab_name.value], feature_name.value)
        CORETAB_DTS[new_coretab_name.value] = coretab_dt
        plot_coreset(coretab_dt)
        plt.savefig('coreset_feature_plot.jpg', dpi=300, bbox_inches='tight')
        coreset_content = hilt.UserContent(
            content_name="coreset_feature_plot",
            content_file_path='coreset_feature_plot.jpg',
            content_type=hilt.ContentTypes.JPG
        )
        tool.save_content(coreset_content)
        hilt.results.show_results(coreset_content, "Feature removed from coreset and visualized.")
tool.add_stage('remove_feature_from_coreset', remove_feature_from_coreset)
if __name__ == "__main__":
    tool.run()