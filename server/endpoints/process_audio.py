
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
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
import ast
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime
import datetime as dt
import re




from utils.sched_iter import scheduler

load_dotenv(find_dotenv())

API_URL = os.environ["API_URL"]
HF_API_TOKEN = os.environ["HF_API_TOKEN"]

prompt = hub.pull("hwchase17/openai-functions-agent")
llm = ChatOpenAI(model="gpt-4", temperature=0)

# text_to_tuple_agent = create_openai_functions_agent(llm, None, prompt)
# text_to_tuple_agent_executor = AgentExecutor(agent=text_to_tuple_agent, tools=None, verbose=True)

# reaction_agent = create_openai_functions_agent(llm, None, prompt)
# reaction_agent_executor = AgentExecutor(agent=reaction_agent, tools=None, verbose=True)


def get_current_date(): ### double check correct
    # Get the current date
    current_date = datetime.utcnow()
    return current_date

def tuple_to_response_correct(user_input):
    prompt = f'''
        Convert the specified tuple into a normal response saying that the event with the 
        information of the tuple was scheduled successfully and added to the calendar.
        The format of the tuple is (date, duration, release, deadline, information) where
        "date" is the date that the event has been scheduled,
        "duration" is the time to complete the event in the format of (String hours::minutes in 24 hour with a UTC format. Reference the current timezone for conversion), 
        "release" is the earliest the event can be done in the format of (String hours::minutes in 24 hour format with a UTC format. Reference the current timezone for conversion), 
        "deadline" is the latest the event can be done in the format of (String hours::minutes in 24 hour format with a UTC format. Reference the current timezone for conversion), 
        "days" is the possible days this event can be added. This is in the format of (String '01234567' where each number represents the days from now and you can have multiple options up to 7 days in advance),    
        "information" is the name of the event (String).
        here is the tupple to convert: "{user_input}". 
        Please use the current date "{get_current_date()}" for reference.
    '''
    return prompt

def tuple_to_response_incorrect(user_input, event, future_events):
    prompt = f'''
        Convert the specified tuple into a normal response saying that the event with the 
        information of the tuple was scheduled unsuccessfully and added to the calendar. In addition list conflicts and also the events that still need to be scheduled. 
        Essentially it should say that the event converted event_tuple was not scheduled successfuly. Then it should list the conflicts specified in the user_input.

        The format of the conflcit tuples is (date, duration, release, deadline, information) where
        "date" is the date that the event has been scheduled,
        "duration" is the time to complete the event in the format of (String hours::minutes in 24 hour with a UTC format. Reference the current timezone for conversion), 
        "release" is the earliest the event can be done in the format of (String hours::minutes in 24 hour format with a UTC format. Reference the current timezone for conversion), 
        "deadline" is the latest the event can be done in the format of (String hours::minutes in 24 hour format with a UTC format. Reference the current timezone for conversion),    
        "information" is the name of the event (String).
        
        The format of the event_tuple is of (duration, release, deadline, days, information) where 
        "duration" is the time to complete the event in the format of (String hours::minutes in 24 hour with a UTC format. Reference the current timezone for conversion), 
        "release" is the earliest the event can be done in the format of (String hours::minutes in 24 hour format with a UTC format. Reference the current timezone for conversion), 
        "deadline" is the latest the event can be done in the format of (String hours::minutes in 24 hour format with a UTC format. Reference the current timezone for conversion), 
        "days" is the possible days this event can be added. This is in the format of (String '01234567' where each number represents the days from now and you can have multiple options up to 7 days in advance),    
        "information" is the name of the event (String).

        We also have a list of future_events which are all also event_tuples. Convert these to the event and say that we still need to schedule these events, 
        here is the list of conflict tuples to convert: "{user_input}".
        here is the event_tuple to convert: "{event}"
        here is the future_events to convert into future events that need to be scheduled: "{future_events}"
        Please use the current date "{get_current_date()}" for reference.
    '''
    return prompt



# Define headers using the environment variables
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {HF_API_TOKEN}",  # Use the loaded API token
    "Content-Type": "audio/flac"  # Ensure this matches the content type of the audio you're sending
}

    
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


tuple_to_event_prompt_correct = ChatPromptTemplate.from_messages(
    [
        (
        "system",
        f'''Convert the specified tuple into a normal response saying that the event with the 
        information of the tuple was scheduled successfully and added to the calendar.
        The format of the tuple is (date, duration, release, deadline, information) where
        "date" is the date that the event has been scheduled,
        "duration" is the time to complete the event in the format of (String hours::minutes in 24 hour with a UTC format. Reference the current timezone for conversion), 
        "release" is the earliest the event can be done in the format of (String hours::minutes in 24 hour format with a UTC format. Reference the current timezone for conversion), 
        "deadline" is the latest the event can be done in the format of (String hours::minutes in 24 hour format with a UTC format. Reference the current timezone for conversion), 
        "days" is the possible days this event can be added. This is in the format of (String '01234567' where each number represents the days from now and you can have multiple options up to 7 days in advance),    
        "information" is the name of the event (String).
        Please use the current date "{get_current_date()}" for reference.''',
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)



tuple_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f'''I want you check if the any user input specifies events they want to do in the week. 
            It is crucial to transform this input into a highly specific and structured format. 
            Each event (if it exists) must be represented as a tuple, adhering strictly to the following structure: 
            (duration, release, deadline, days, information).
            Here, "duration" refers to the event's length in a 24-hour format (hours::minutes), taking into account the current timezone for 
            accurate conversion. "Release" specifies the earliest time the event can commence, while "deadline" indicates the latest completion time, 
            both also in a 24-hour format aligned with the current timezone. "Days" denotes the possible days for scheduling the event, formatted 
            as '1234567', where each numeral represents Monday through Sunday, respectively. Finally, "information" provides the event's name. 
            The output must exclusively be a list of such tuples, each encapsulating a single event in the format: \[(duration, release, deadline, days, information), ...\]. 
            This format must be adhered to with precision, ensuring the response contains only a list of tuples and no other text. Moreover, ensure that the duration element only has 
            the hours and minutes given and nothing else. An empty list and nothing else should be returned if no events are provided. 
            It is imperative to use the information provided, along with sensible 
            assumptions for any unspecified details like release times and deadlines, to create a feasible and practical schedule. However, should any event prove impossible to schedule—such as an 
            event exceeding the available time frame—an empty tuple should be returned. It is also important to note that different multiple tuples 
            must be added to the array for a single event if the frequncy of that event is more than 1 (ie, I want to run 4 times a week),
            specified for the
            The significance of delivering the response solely as a list of tuples cannot be overstated.  Please use the current date {get_current_date()} for reference.''',
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


multi_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f'''I want you check if the any user input specifies events they want to do in the week. 
            It is crucial to transform this input into a highly specific and structured format. 
            Each event (if it exists) must be represented as a tuple, adhering strictly to the following structure: 
            (duration, release, deadline, days, information).
            Here, "duration" refers to the event's length in a 24-hour format (hours::minutes), taking into account the current timezone for 
            accurate conversion. "Release" specifies the earliest time the event can commence, while "deadline" indicates the latest completion time, 
            both also in a 24-hour format aligned with the current timezone. "Days" denotes the possible days for scheduling the event, formatted 
            as '1234567', where each numeral represents Monday through Sunday, respectively. Finally, "information" provides the event's name. 
            The output must exclusively be a list of such tuples, each encapsulating a single event in the format: \[(duration, release, deadline, days, information), ...\]. 
            This format must be adhered to with precision, ensuring the response contains only a list of tuples and no other text.
            An empty list and nothing else should be returned if no events are provided. It is imperative to use the information provided, along with sensible 
            assumptions for any unspecified details like release times and deadlines, to create a feasible and practical schedule. However, should any event prove impossible to schedule—such as an 
            event exceeding the available time frame—an empty tuple should be returned. It is also important to note that different multiple tuples 
            must be added to the array for a single event if the frequncy of that event is more than 1 (ie, I want to run 4 times a week),
            specified for the
            The significance of delivering the response solely as a list of tuples cannot be overstated.  Please use the current date {get_current_date()} for reference.''',
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

conversation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f'''You are a helpful assistant who responds to Heather whose purpose is to help the user.''',
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


deletion_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f'''I want you check if the any user input specifies an event they want to cancel (all the events on their calender will also be specified).
            If the input specifies an event they want to cancel, go through the list of all current events (this will be in the format [name_of_event,id]). Find
            the event with the name most similar to the event to be cancelled, and return a tuple in the form of (name_of_event, associated_id). Either only return a 
            single tuple (if there is an event to be cancelled), or just the tuple, (-1,-1) if and only if there is nothing to be deleted. It is of the utmost importance
            that only a single tuple is returned and nothing else. Only either the tuple corresponding to the event to be removed, or the tuple (-1,-1) should be returned. ''',
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chat = ChatOpenAI(model="gpt-4")
tuple_chain = tuple_prompt | chat
convo_chain= conversation_prompt | chat
delete_chain= deletion_prompt | chat


output_correct_chain= tuple_to_event_prompt_correct | chat
output_incorrect_chain = conversation_prompt | chat

def handle_execute():
    
    audio_file = request.data
    audio_file=request.files['audio']

    prior_messages = json.loads(request.form.get('prior_messages'))
    prior_messages=frontend_to_backend_message_helper(prior_messages)
    
    profile= json.loads(request.form.get('profile', '{}'))
    response = requests.post(API_URL, headers=headers, data=audio_file)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to process audio'}), response.status_code
    
    data = response.json()
    prior_messages.append(
        HumanMessage(content=data["text"])
    )
    #### this will need to be modified 


    ### call calendar
    rtok = profile["refresh_token"]
    schedule = scheduler([], rtok)
    
    print("SCHEDULER INITIALIZED \n\n\n\n\n ")

    res=tuple_chain.invoke(
        {
            "messages": prior_messages,
            
        }
    )


    delete_res=delete_chain.invoke(
        {
            "messages": prior_messages+ [SystemMessage(content = "list of events (name of event, id of corresponding event)"+ str(schedule.giveallevents()))],
            
        }
    )
    print("\n\n\nn\n\n")
    print("\n\n\nn\n\n")



    x = str(delete_res.content
    )
    
    if ',' in x and x[0] == '(' and x[-1] == ')' and x[1:3]!="-1":
        nam, ids = x[1:-1].split(',')
        ids = int(ids)

        if schedule.ids.get(ids):
            print(schedule.checkev(ids))
            schedule.remevent(ids)
            prior_messages.append(
                SystemMessage(content="The prior event was cancelled. Relay this information to the user")
            )
            res.content=""


    

    try:
        event_tuples = ast.literal_eval(res.content)
        if not isinstance(event_tuples, list) or not all(isinstance(item, tuple) for item in event_tuples):
            raise ValueError("The string does not represent a list of tuples")
        elif len(event_tuples) == 0:
            raise ValueError("The string does not represent a list of tuples")
        print(event_tuples)
        

    except (ValueError, SyntaxError) as e: #### if this is a normal response, return.
        success = True
        # human chain
        res=convo_chain.invoke(
            {
                "messages": prior_messages
            }
        )

        prior_messages=backend_to_frontend_message_helper(prior_messages)
        final_response = {"text": res.content , "prior_messages" : prior_messages, "success" : success }
        print("executed a none event")
        return final_response,200  # Return the Hugging Face API response
    
    scheduled_events = []
    latest_day = 0
    for count, event in enumerate(event_tuples):

        # (duration, release, deadline, days, information)
        # "0123456"
        
        if count != 0:
            new_event = (event[0], event[1], event[2], "".join([i for i in event[3] if int(i) > latest_day]), event[4])
        else:
            new_event=event


        
        
        event_status = schedule.addevent(new_event)
        # event_status = test_tuple_pass

        if event_status[0]: # passes
            justbooked = event_status[1][0]
            print("WE JUST BOOKED AN EVENT WITH:", justbooked[-1])
            print(justbooked)
            scheduled_events.append(justbooked)
            bookday = datetime.fromisoformat(justbooked[0])
            noww = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0,microsecond=0)
            diff = (bookday - noww).days
            latest_day = max(diff, latest_day)
        else: # fails
            prior_messages.append(
                HumanMessage(content=tuple_to_response_incorrect(event_status[1], new_event, event_tuples[count:]))
            ) 
            res=output_incorrect_chain.invoke(
                {
                    "messages": prior_messages
                }
            )
            # failed
            print("we have a conflict")
            prior_messages=backend_to_frontend_message_helper(prior_messages)
            final_response = {"text": res.content , "prior_messages" : prior_messages, "success" : False }
            return final_response, 200 

    
    prior_messages.append(
                HumanMessage(content=tuple_to_response_correct(scheduled_events))
            ) 
    res=output_correct_chain.invoke(
        {
            "messages": prior_messages
        }
    )
    if response.status_code == 200:
        success = True
        prior_messages=backend_to_frontend_message_helper(prior_messages)
        final_response = {"text": res.content , "prior_messages" : prior_messages, "success" : success }
        return final_response,200  # Return the Hugging Face API response
    else:
        return jsonify({'error': 'Failed to process audio'}), response.status_code




