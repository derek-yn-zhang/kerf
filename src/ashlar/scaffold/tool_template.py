"""Ashlar tool: TOOL_NAME"""


def tool_name(input_data, params):
    # Process input_data using params, return the result.
    # This function receives the output of the previous tool in the chain.
    return input_data


def register(manager):
    manager.register_tool("TOOL_NAME", tool_name)
