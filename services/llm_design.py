from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from services.templates import * 

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_llm_chain_response(text_file_path:str, user_selection:str, teacher_name:str, education_center:str , template_type:str, template_output:str):

    with open(text_file_path, 'r') as file:
        content = file.read()

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=2000, chunk_overlap=250)
    texts = text_splitter.create_documents([content])

    llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro-latest", google_api_key=GOOGLE_API_KEY, convert_system_message_to_human=True)


    summary_output_options = {
        'one_sentence' : """
        - Only one sentence
        """,
        
        'bullet_points': """
        - Bullet point format
        - Separate each bullet point with a new line
        - Each bullet point should be concise
        """,
        
        'short' : """
        - A few short sentences
        - Do not go longer than 4-5 sentences
        """,
        
        'long' : """
        - A verbose summary
        - You may do a few paragraphs to describe the transcript if needed
        """,

        'list' : """
        - A list of items: ['point1', 'point2', 'point3']
        """,

        'class_plan' : """
        - Make proper class plan
        - day wise plan for the class
        """,

        'class_json' : """
        Output in the following JSON format: 

        {
        "study_plan" : [
            A list of dictionaries like given below:
                {
                    "class_no": "number of the class,
                    "topic": "topic for the class"
                }
            ]
        }


        Be as concise as possible in your output.
        """
    }

    template= template_type

    human_template="{text}"


    system_message_prompt_map = SystemMessagePromptTemplate.from_template(template)
    human_message_prompt_map = HumanMessagePromptTemplate.from_template(human_template)

    template= template_output
    system_message_prompt_combine = SystemMessagePromptTemplate.from_template(template)

    human_template="{text}" # Simply just pass the text as a human message
    human_message_prompt_combine = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt_combine = ChatPromptTemplate.from_messages(messages=[system_message_prompt_combine, human_message_prompt_combine])

    chat_prompt_map = ChatPromptTemplate.from_messages(messages=[system_message_prompt_map, human_message_prompt_map])


    chain = load_summarize_chain(llm,
                                chain_type="map_reduce",
                                map_prompt=chat_prompt_map,
                                combine_prompt=chat_prompt_combine,
                                verbose=True
                                )


    output = chain.run({
                        "input_documents": texts,
                        "teacher_name": teacher_name, \
                        "education_center": education_center ,
                        "output_format" : summary_output_options[user_selection]
                    })

    return output




# final_result = get_llm_chain_response("notebooks_analysis/class_transcript.txt",
#                                        "list", "John Doe", "ABC School",CONCEPTS_TAUGHT_PROMPT , CONCEPTS_TAUGHT_PROMPT_OUTPUT)


# print(final_result)


