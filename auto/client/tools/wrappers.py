from fc.invoke import call_fc_function

def make_tool_func(tool_name):
    def tool_func(**kwargs):
        # kwargs 已经是 {"team": "Liverpool"} 或 {"league": "...", "team": "..."}
        return call_fc_function(tool_name, kwargs)
    return tool_func