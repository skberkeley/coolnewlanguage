import pymupdf

from coolNewLanguage import src as hilt

DESCRIPTION = "This is a Tool for testing PDF functionality. Users can upload PDF files and view them."


tool = hilt.Tool('PDF_Demo', description=DESCRIPTION)


def file_upload():
    file_path = hilt.FileUploadComponent(
        expected_ext="pdf", label="Upload a PDF file", replace_existing=True)
    name_input = hilt.UserInputComponent(str, "Name your PDF: ")
    if tool.user_input_received():
        content = hilt.UserContent(content_name=name_input.value,
                                   content_file_path=file_path.value, content_type=hilt.ContentTypes.PDF)
        tool.save_content(content)
        hilt.results.show_results((content, "Uploaded PDF:"))


tool.add_stage('File Upload', file_upload)


def see_all_pdfs():
    for content in tool.get_content():
        hilt.PDFViewerComponent(content)


tool.add_stage('See All PDFs', see_all_pdfs)


def search_pdfs():
    search_input = hilt.UserInputComponent(str, "Search for PDFs: ")
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


tool.run()
