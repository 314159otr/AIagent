from google.genai import types
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info 
from functions.write_file import write_file
from functions.run_python_file import run_python_file
from config import WORKING_DIR

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = function_call_part.args

    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f"- Calling function: {function_name}")

    functions_dict = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "write_file": write_file,
        "run_python_file": run_python_file,
    }

    try:
        function = functions_dict[function_name]
    except KeyError :
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    args = {"working_directory": WORKING_DIR} | function_args
    function_result = function(**args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )
