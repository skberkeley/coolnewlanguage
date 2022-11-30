from coolNewLanguage.src import util
from coolNewLanguage.src.stage.stage import Stage


def show_results(result, label: str = ''):
    """
    Render the passed result as a rendered Jinja template, and set it on Stage
    This function is called from the programmer defined stage functions, so
    returning wouldn't pass the state where we want it
    If we're not handling a post request, doesn't do anything
    :param result: The result to render in template
    :param label: An optional label for the results
    """
    # we're not handling a post request, so we don't have any results to show
    if not Stage.handling_post:
        return

    form_action = '/'
    form_method = "get"

    template_list = [
        '<html>',
        '<head>',
        '<title>',
        "Results",
        '</title>',
        '</head>',
        '<body>',
    ]

    if label:
        template_list += [
            '<div>',
            '<p>',
            label,
            '</p>',
            '</div>'
        ]

    template_list += [
        '<div>',
        str(result),
        '</div>',
        f'<form action="{form_action}" method="{form_method}">',
        '<input type="submit" value="Back to landing page">',
        '</form>',
        '</body>',
        '</html>'
    ]

    raw_template = ''.join(template_list)
    jinja_template = util.JINJA_ENV.from_string(raw_template)
    Stage.results_template = jinja_template.render()
