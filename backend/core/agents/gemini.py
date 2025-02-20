import functools
from google import genai
from core.output_structures.error_correction import CorrectionResponse
from core.output_structures.general_query import GeneralQueryResponse
from dotenv import load_dotenv
import os

load_dotenv()
GENAI_API = os.getenv("GENAI_API")

class Gemini:
    def __init__(self, api_key:str, model:str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    @staticmethod
    def complete(func):
        @functools.wraps(func)
        def wrapper(self,*args, **kwargs):
            context, prompt, response = func(self,*args, **kwargs)
            response = self.client.models.generate_content(
                model=self.model,
                contents = [f"{prompt} \ncontext:{context}"],
                    config={
                    'response_mime_type': 'application/json',
                    'response_schema': response,
                }
            )
            return response
        return wrapper
    
    @complete
    def error_correction(self, prompt, context):
        prompt = f"Correct the error in this command {prompt}, If the correction is very obvious just return the correct command else return the top 3 plausible commands. No explanation needed."
        context = context if context else "No previous commands."
        response = CorrectionResponse
        return context, prompt, response
    
    @complete
    def general_query(self, prompt, context):
        response = GeneralQueryResponse
        return context, prompt, response
    

if __name__ == "__main__":
    base = Gemini(GENAI_API, "gemini-2.0-flash")
    text = """
    ╰❯ dir -a
    Get-ChildItem : Parameter cannot be processed because the parameter name 'a' is ambiguous. Possible matches include:
    -Attributes -Directory -File -Hidden -ReadOnly -System.
    At line:1 char:5
    + dir -a
    +     ~~
        + CategoryInfo          : InvalidArgument: (:) [Get-ChildItem], ParameterBindingException
        + FullyQualifiedErrorId : AmbiguousParameter,Microsoft.PowerShell.Commands.GetChildItemCommand
    """

    response = base.error_correction(prompt=text, context="")
    print(response.parsed.corrections)
    response = base.general_query(prompt="How to install a package in linux", context="")
    print(response.parsed.response)