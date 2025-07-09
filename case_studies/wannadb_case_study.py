"""
Ran this script with wannadb's requirements installed, and its location added to PYTHONPATH.
"""
import coolNewLanguage.src as hilt

from wannadb.configuration import Pipeline
from wannadb.data.data import DocumentBase
from wannadb.interaction import InteractionCallback, EmptyInteractionCallback
from wannadb.matching.custom_match_extraction import FaissSentenceSimilarityExtractor
from wannadb.matching.distance import SignalsMeanDistance
from wannadb.matching.matching import SingleNuggetMatcher, SingleNuggetUpdater
from wannadb.preprocessing.embedding import RelativePositionEmbedder, SBERTDocumentSentenceEmbedder, SBERTLabelEmbedder, SBERTTextEmbedder
from wannadb.preprocessing.label_paraphrasing import OntoNotesLabelParaphraser, SplitAttributeNameLabelParaphraser
from wannadb.preprocessing.normalization import CopyNormalizer
from wannadb.preprocessing.other_processing import ContextSentenceCacher
from wannadb.resources import ResourceManager
from wannadb.statistics import Statistics
from wannadb.status import EmptyStatusCallback

tool = hilt.Tool('wannadb')

DOCUMENT_BASE = 'document_base'
ALL_NUGGETS = 'all_nuggets'
tool.state[DOCUMENT_BASE] = DocumentBase([], [])
tool.state[ALL_NUGGETS] = {}
ResourceManager()

def corpus_upload():
    """
    Stage to upload a bson file to load in a DocumentBase.
    :return:
    """
    bson_file = hilt.FileUploadComponent('', label="Upload a bson file:")

    if tool.user_input_received():
        with open(bson_file.value, 'rb') as f:
            tool.state[DOCUMENT_BASE] = DocumentBase.from_bson(f.read())
            document_base = tool.state[DOCUMENT_BASE]
            if not document_base.validate_consistency():
                raise ValueError("The uploaded file is not a valid document base.")
            
            hilt.results.show_results((document_base, "Successfully uploaded document base: "))


tool.add_stage('corpus_upload', corpus_upload)


def attribute_feedback_step():
    """
    Stage to provide feedback on a nugget
    :return:
    """
    matching_phase = Pipeline(
        [
            SplitAttributeNameLabelParaphraser(do_lowercase=True, splitters=[" ", "_"]),
            ContextSentenceCacher(),
            SBERTLabelEmbedder("SBERTBertLargeNliMeanTokensResource"),
            SBERTDocumentSentenceEmbedder("SBERTBertLargeNliMeanTokensResource"),
            SingleNuggetMatcher(
                distance=SignalsMeanDistance(
                    signal_identifiers=[
                        "LabelEmbeddingSignal",
                        "TextEmbeddingSignal",
                        "ContextSentenceEmbeddingSignal",
                        "RelativePositionSignal"
                    ]
                ),
                max_num_feedback=100,
                len_ranked_list=10,
                max_distance=0.2,
                num_random_docs=1,
                sampling_mode="AT_MAX_DISTANCE_THRESHOLD",
                adjust_threshold=True,
                nugget_pipeline=Pipeline(
                    [
                        ContextSentenceCacher(),
                        CopyNormalizer(),
                        OntoNotesLabelParaphraser(),
                        SplitAttributeNameLabelParaphraser(do_lowercase=True, splitters=[" ", "_"]),
                        SBERTLabelEmbedder("SBERTBertLargeNliMeanTokensResource"),
                        SBERTTextEmbedder("SBERTBertLargeNliMeanTokensResource"),
                        # BERTContextSentenceEmbedder("BertLargeCasedResource"),
                        RelativePositionEmbedder()
                    ]
                ),
                find_additional_nuggets=FaissSentenceSimilarityExtractor(num_similar_sentences=20, num_phrases_per_sentence=3),
                store_best_guesses=True,
            )
        ]
    )

    # value_present, nugget_selector, nugget
    feedback_components = []
    def show_components_interaction_callback(identifier, feedback_request):
        print("Interaction callback called")
        if 'nugget' not in feedback_request:
            hilt.TextComponent("No further feedback needed.")
            return
        nugget = feedback_request['nugget']
        attribute = feedback_request['attribute']
        tool.state[ALL_NUGGETS][attribute.name] = feedback_request['all_nuggets']

        hilt.TextComponent(f"Attribute: {attribute}")
        hilt.TextComponent(f"Current nugget: {nugget}")
        hilt.TextComponent(nugget.document.text)
        value_present = hilt.SelectorComponent(
            ["Present", "Not Present"],
            "Select whether a correct value is present in the document: "
        )
        nugget_selector = hilt.SelectorComponent([n.text for n in nugget.document.nuggets], "Select an updated value: ")

        feedback_components.append(value_present)
        feedback_components.append(nugget_selector)
        feedback_components.append(nugget)

    interaction_callback = InteractionCallback(show_components_interaction_callback)
    matching_phase(tool.state[DOCUMENT_BASE], interaction_callback, EmptyStatusCallback(), Statistics(False))

    if tool.user_input_received():
        if feedback_components[0].value != "Present":
            message = "no-match-in-document"
        else:
            message = "is-match"

        for n in feedback_components[2].document.nuggets:
            if n.text == feedback_components[1].value:
                nugget = n
                break

        updater = SingleNuggetUpdater(
            distance=SignalsMeanDistance(
                signal_identifiers=[
                    "LabelEmbeddingSignal",
                    "TextEmbeddingSignal",
                    "ContextSentenceEmbeddingSignal",
                    "RelativePositionSignal"
                ]
            ),
            max_num_feedback=100,
            len_ranked_list=10,
            max_distance=0.2,
            num_random_docs=1,
            sampling_mode="AT_MAX_DISTANCE_THRESHOLD",
            adjust_threshold=True,
            nugget_pipeline=Pipeline(
                [
                    ContextSentenceCacher(),
                    CopyNormalizer(),
                    OntoNotesLabelParaphraser(),
                    SplitAttributeNameLabelParaphraser(do_lowercase=True, splitters=[" ", "_"]),
                    SBERTLabelEmbedder("SBERTBertLargeNliMeanTokensResource"),
                    SBERTTextEmbedder("SBERTBertLargeNliMeanTokensResource"),
                    # BERTContextSentenceEmbedder("BertLargeCasedResource"),
                    RelativePositionEmbedder()
                ]
            ),
            find_additional_nuggets=FaissSentenceSimilarityExtractor(num_similar_sentences=20,
                                                                     num_phrases_per_sentence=3),
            feedback_result={
                "message": message,
                "nugget": nugget,
                "not-a-match": None
            },
            store_best_guesses=True,
        )
        updater(tool.state[DOCUMENT_BASE], EmptyInteractionCallback(), EmptyStatusCallback(), Statistics(False))


tool.add_stage('attribute_feedback_step', attribute_feedback_step)


def see_attribute_values():
    """
    Stage to see the attribute values of the document base.
    :return:
    """
    attr = hilt.SelectorComponent(
        [attr.name for attr in tool.state[DOCUMENT_BASE].attributes],
        "Select an attribute to see its values: "
    )

    if tool.user_input_received():
        d_to_n = {n.document.name : n for n in tool.state[ALL_NUGGETS][attr.value]}

        results = []
        for d in tool.state[DOCUMENT_BASE].documents:
            if attr.value in d.attribute_mappings.keys() and len(d.attribute_mappings[attr.value]) > 0:
                results.append((d.name, d.attribute_mappings[attr.value][0].text))
            else:
                results.append((d.name, d_to_n[d.name].text if d.name in d_to_n else "No value found"))
        hilt.results.show_results(*results)


tool.add_stage('see_attribute_values', see_attribute_values)


tool.run()
