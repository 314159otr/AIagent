import os

from google.genai import types
def get_files_info(working_directory, directory="."):
    abs_working_dir = os.path.abspath(working_directory)
    abs_target_dir = os.path.abspath(os.path.join(working_directory, directory))
    if not abs_target_dir.startswith(abs_working_dir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(abs_target_dir):
        return f'Error: "{directory}" is not a directory'
    try:
        files_info = []
        for filename in os.listdir(abs_target_dir):
            path =  os.path.join(abs_target_dir, str(filename))
            size = os.path.getsize(path)
            is_dir = os.path.isdir(path)
            files_info.append(
                f"- {filename}: file_size={size}bytes, is_dir={is_dir}"
            )
        return "\n".join(files_info)
    except Exception as e:
        return f'Error: {e}'

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
        required=["directory"],
    ),
)

