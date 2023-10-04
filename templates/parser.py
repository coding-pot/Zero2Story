import jinja2

def gen_from_file(filename, kwargs):
    # for basic template there are two keys that should be provided
    # characters (list) 
    # - each item has 'img' and 'name' keys
    #
    # items (stories)
    # - each item has 'video', 'img', 'audio', and 'story'
    html_template = open(filename, "r")

    environment = jinja2.Environment()
    template = environment.from_string(html_template)

    return template.render(**kwargs)