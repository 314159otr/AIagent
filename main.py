import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import MAX_ITERATIONS
from functions.call_function import call_function
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file

def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv 
    args = []
    for arg in sys.argv[1:]: #The first argv is always the filename
        if not arg.startswith("--"):
            args.append(arg)
    if not args:
        print('Usage: python main.py "your prompt here" [--verbose]')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)
    if verbose:
        print(f"User prompt: {user_prompt}")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_write_file,
            schema_run_python_file,
        ]
    )

    for _ in range(MAX_ITERATIONS):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt
                ),
            )
            if verbose:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

            if response.candidates is not None:
                for candidate in response.candidates:
                    if candidate.content is not None:
                        messages.append(candidate.content)
            function_responses = []

            if response.function_calls:
                for function_call_part in response.function_calls:
                    function_call_result = call_function(function_call_part, verbose)
                    if (
                        not function_call_result.parts
                        or not function_call_result.parts[0].function_response
                    ):
                        raise Exception("empty function call result")
                    if verbose:
                        print(f"-> {function_call_result.parts[0].function_response.response}")
                    function_responses.append(function_call_result.parts[0])

                if not function_responses:
                    raise Exception("no function responses generated, exiting.")

                messages.append(types.Content(role="tool", parts=function_responses))
            else:
                print(response.text)
                break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
