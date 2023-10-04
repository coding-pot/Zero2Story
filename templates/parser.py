import jinja2

def gen_from_file(filename, kwargs):
    html_template = open(filename, "r")

    environment = jinja2.Environment()
    template = environment.from_string(html_template)

    return template.render(**kwargs)