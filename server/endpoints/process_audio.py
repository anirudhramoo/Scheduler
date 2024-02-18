
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv, find_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain.prompts import (
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
import ast
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime



load_dotenv(find_dotenv())

API_URL = os.environ["API_URL"]
HF_API_TOKEN = os.environ["HF_API_TOKEN"]

prompt = hub.pull("hwchase17/openai-functions-agent")
llm = ChatOpenAI(model="gpt-4", temperature=0)

# text_to_tuple_agent = create_openai_functions_agent(llm, None, prompt)
# text_to_tuple_agent_executor = AgentExecutor(agent=text_to_tuple_agent, tools=None, verbose=True)

# reaction_agent = create_openai_functions_agent(llm, None, prompt)
# reaction_agent_executor = AgentExecutor(agent=reaction_agent, tools=None, verbose=True)


def get_current_date():
    # Get the current date
    current_date = datetime.now().date()
    return current_date

def add_tuple_conversion_user(user_input):
    prompt = f'''ONLY do the following if the user specifies an input to schedule something. If for example the user doesn't mention this, respond as a normal assistant.
    If for example user input specifies different events they want to do in the week please convert the user input for each and every single event into a list of 
    tuples where each tuple represents one of these events. If for example they specify they want to do an event multiple times, please create multiple events. PLEASE only return only the tuple. Do NOT return anything else besides the tuple or else the user will be upset if they specify events. 
    The format of the event's tuple is of (duration, release, deadline, days, information) where 
    "duration" is the time to complete the event in the format of (String hours::minutes in 24 hour format), 
    "release" is the earliest the event can be done in the format of (String hours::minutes in 24 hour format), 
    "deadline" is the latest the event can be done in the format of (String hours::minutes in 24 hour format), 
    "days" is the possible days this event can be added. This is in the format of (String '01234567' where each number represents the days from now and you can have multiple options up to 7 days in advance),    
    "information" is the name of the event (String).
    Please return this to the user as a list of tuples with each element being one event in the format of: [(duration, release, deadline, days, information), (duration, release, deadline, days, information), ...] 
    PLEASE only return only the tuple. Do NOT return anything else besides the tuple or else the user will be upset.
    ONLY do the following if the user specifies an input to schedule something. 
    If for example the user doesn't mention this, respond as a normal assistant and ignore returning tuples.
    Here is the prompt to convert: "{user_input}". 
    Make sure to only respond with the list of tuple if an event is specified. Please use the current date "{get_current_date()}" in your calculations. 
    ONLY do the tuple information if the user specifies an input to schedule something. 
    If for example the user doesn't mention this, respond as a normal assistant and ignore returning tuples.
    As you convert the events into these tuples, use the information and make your own decisions. For example, if release and deadlines aren't specified, 
    generate your own at reasonable hours for the task specified. Make the user happy. PLEASE only return only the tuple. Do NOT return anything else besides the tuple or else the user will be upset if they mention events.
    Again, only do the event tuples if the user wants to schedule something, if they do not, respond as a normal assistant and ignore returning tuples.'''


    return prompt

# Define headers using the environment variables
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {HF_API_TOKEN}",  # Use the loaded API token
    "Content-Type": "audio/flac"  # Ensure this matches the content type of the audio you're sending
}


# def react():

#     event_tuples_string=text_to_tuple_agent_executor.invoke({"input": add_tuple_conversion_user(data["text"]), "chat_history": prior_context})
    



def handle_audio():
    audio_data = request.data  # Directly use the binary data from the request
    if not audio_data:
        return jsonify({'error': 'No audio data received'}), 400

    # Forward the audio data to the Hugging Face API
    response = requests.post(API_URL, headers=headers, data=audio_data)
    
    if response.status_code == 200:
        return response.json()  # Return the Hugging Face API response
    else:
        return jsonify({'error': 'Failed to process audio'}), response.status_code
    


# converts frontetn messages to langchain format
def frontend_to_backend_message_helper(messages):
    python_messages=[HumanMessage(content=message["text"]) if message["user"]=="human" else AIMessage(content=message["text"]) for message in messages]
    return python_messages

def backend_to_frontend_message_helper(python_messages):
    messages = []
    for message in python_messages:
        if isinstance(message, HumanMessage):
            user_type = "human"
        elif isinstance(message, AIMessage):
            user_type = "ai"
        else:
            continue  # Skip unknown message types
        messages.append({"user": user_type, "text": message.content})
    return messages




prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant named Heather. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
chat = ChatOpenAI(model="gpt-4")

chain = prompt | chat
def handle_execute():
    # Check if there is file data
    # if 'audio' not in request.fo:
    #     return jsonify({'error': 'No audio file part'}), 400
    
    audio_file = request.data
    audio_file=request.files['audio']

    prior_messages = json.loads(request.form.get('prior_messages'))
    print(prior_messages)
    prior_messages=frontend_to_backend_message_helper(prior_messages)
    
    profile= json.loads(request.form.get('profile', '{}'))
    response = requests.post(API_URL, headers=headers, data=audio_file)
    
    data = response.json()
    prior_messages.append(
        HumanMessage(content=add_tuple_conversion_user(data["text"]))
    )
    res=chain.invoke(
        {
            "messages":prior_messages
        }
    )

    prior_messages.append(res)
    prior_messages=backend_to_frontend_message_helper(prior_messages)

    #### calendar call (hopefully async w/ promise but unsure if python supports)
    
    # event_tuples_string=text_to_tuple_agent_executor.invoke({"input": add_tuple_conversion_user(data["text"]), "chat_history": prior_context})
    #    # append ai message to the end of this



    
    if response.status_code == 200:
        success = True
        final_response = {"text": res.content , "prior_messages" : prior_messages, "success" : success }
        return final_response,200  # Return the Hugging Face API response
    else:
        return jsonify({'error': 'Failed to process audio'}), response.status_code




