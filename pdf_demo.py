import pymupdf
from coolNewLanguage import src as hilt
import pandas as pd
DESCRIPTION = "This is a Tool for uploading PDFs and linking them to individuals of interest."
tool = hilt.Tool('PDF_Demo', description=DESCRIPTION)
if 'Names' not in tool.tables:
    tool.tables['Names'] = pd.DataFrame(columns=['name'])


def upload_and_search_pdf():
    file_path = hilt.FileUploadComponent(
        expected_ext="pdf", label="Upload a PDF file", replace_existing=True)
    name_input = hilt.UserInputComponent(str, "Name your PDF: ")
    if tool.user_input_received():
        content = hilt.UserContent(content_name=name_input.value,
                                   content_file_path=file_path.value, content_type=hilt.ContentTypes.PDF)
        tool.save_content(content)
        hilt.results.show_results(
            (content, "Uploaded PDF:"))


tool.add_stage('File Upload and Search', upload_and_search_pdf)


def see_all_pdfs():
    for content in tool.get_content():
        hilt.PDFViewerComponent(content)


tool.add_stage('See All PDFs', see_all_pdfs)


def search_pdfs():
    search_input = hilt.SelectorComponent(options=tool.tables['Names']['name'].tolist(),
                                          label="Select a name to search for in the PDFs")
    if tool.user_input_received():
        all_content = tool.get_content()
        found = []
        for content in all_content:
            if content.content_type == hilt.ContentTypes.PDF:
                pdf = pymupdf.open(content.content_file_path)
                for page in pdf:
                    text = page.get_text()
                    if search_input.value in text:
                        found.append(content)
        hilt.results.show_results(*[(content, "Found in:")
                                  for content in found])


tool.add_stage('Search PDFs', search_pdfs)


def add_names():
    name_inputs = hilt.UserInputComponent(
        str, "Add a name: ", multiple_values=True)
    if tool.user_input_received():
        names = tool.tables['Names']
        new_names = set(name_inputs.value) - set(names['name'])
        name_rows = pd.DataFrame([{'id': len(names) + 1 + i, 'name': name}
                                  for i, name in enumerate(new_names)])
        tool.tables['Names'] = pd.concat([names, name_rows])
        hilt.results.show_results(*[(name, "Name added:")
                                    for name in new_names])


tool.add_stage('Add Names', add_names)
tool.run()
