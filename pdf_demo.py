from coolNewLanguage import src as hilt

DESCRIPTION = "This is a Tool for testing PDF functionality. Users can upload PDF files and view them."


tool = hilt.Tool('PDF_Demo', description=DESCRIPTION)


def file_upload():
    file_path = hilt.FileUploadComponent(
        expected_ext="pdf", label="Upload a PDF file", replace_existing=True)
    name_input = hilt.UserInputComponent(str, "Name your PDF: ")
    if tool.user_input_received():
        content = hilt.UserContent(content_name=name_input.value,
                                   content_file_name=file_path.value, content_type=hilt.ContentTypes.PDF)
        tool.save_content(content)
        hilt.results.show_results((content, "Uploaded PDF:"))


tool.add_stage('File Upload', file_upload)

tool.run()
