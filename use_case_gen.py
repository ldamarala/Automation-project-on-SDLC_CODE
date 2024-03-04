import openai
import sqlite3
import os
import datetime
import pandas as pd
import re
import ipywidgets as widgets
import requests
from fpdf import FPDF
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from IPython.display import HTML
from docx import Document

# from dotenv import load_dotenv

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = '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'

def db_connect(project_name):
    connection = sqlite3.connect("blueprint.db")
    cursor = connection.cursor()
    section_name = "user_business_idea"
    projectname = project_name 
    table_name = "brd_responses"
    query = f"SELECT {section_name} FROM {table_name} WHERE project_name = ?;"

    # Execute the query
    cursor.execute(query, (projectname,))

    # Fetch the result (assuming one row is returned)
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Print the result
    return result

def use_cases_gen(project_name,business_idea):
    sample_usecase = """
    Login with username and password.If credentails are valid allow login.Otherwise throw message saying 'invalid login'.If Login is successful then verify default screen is dashboard.Otherwise display message 'did not meet expected result'.If dashboard is visible, Move to Folder Access screen and If Folder Access screen is visible Click on create folder.Otherwise say'Folder Access Sreen is not visible'.If the create folder pop-up is visible then enter folder name.Otherwise display message 'test case is failed as pop-up is not displayed'.Click on Enter and validate Folder is created successfully or not.If folder is created successfully then create a excel file in it.Otherwise display message 'folder is not created'.If the excel file is created then open the file through online editor.Otherwise display message 'file is not created'.
    """
    # Business_idea = db_connect(project_name)

    usecase_response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                # "content": "For the given Business_idea and sample_usecase, Generate the different user-stories for the Given Business_Idea. Generated Use-Stories should cover all the possibilities and follow the sample_usecase structure."
                # "content": "For the given Product_Deliverable form the BRD and sample_usecase, Generate the different usecases for the Given Product_Deliverable. Generated Use_Cases should cover all the possibilities and follow the sample_usecase structure."
                "content": "For the given Business_idea and sample_usecase, Generate the different usecases for the Given Business_Idea. Generated Use_Cases should cover all the possibilities and follow the sample_usecase structure."
                #"content": "Based on the provided Module1 and sample Usecase, generate the otherwise usecases for the Given Module1. output of generated usecases format should be same as sample usecase."
            },
            {
                "role": "user",
                "content": f"Business_Idea: {business_idea}’\n\nsample usecase: {sample_usecase}"
            }
        ],
        temperature=0.0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    generated_usecase_responses = usecase_response['choices'][0]['message']['content']
    print(generated_usecase_responses)

    # timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).strftime("%Y%m%d%I%M%p")
    filename = f"gen_usecase.txt"
    path = "/home/ldamarala/Desktop/brd_project/"
    file_path = os.path.join(path, filename)

    # Open the file in write mode and write the string data to the file
    with open(file_path, "w") as file:
        file.write(generated_usecase_responses)

    con = sqlite3.connect("blueprint.db")
    cursor = con.cursor()

    sql = "INSERT INTO use_cases (project_name, user_business_idea, use_cases) VALUES (?, ?, ?)"
    data = (project_name, business_idea, generated_usecase_responses)

    cursor.execute(sql, data)
    con.commit() 

    con.close()
    print("Use-Cases added to DB successfully!")

    
    return print(f"String data has been saved to {file_path}")

def flowchart(project_name):
    connection = sqlite3.connect("blueprint.db")
    cursor = connection.cursor()
    section_name = "use_cases"
    projectname = project_name 
    table_name = "use_cases"
    query = f"SELECT {section_name} FROM {table_name} WHERE project_name = ?;"

    # Execute the query
    cursor.execute(query, (projectname,))

    # Fetch the result (assuming one row is returned)
    use_cases = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    flowchart_response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "Generate a 'top to bottom' Mermaidjs code for all the given use case one by one and place it in a basic html code so that if i render the file flowcharts should be displayed:"},
            {"role": "user", "content": f"usecase: {use_cases}"}
        ],
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    generated_flowchart_responses = flowchart_response['choices'][0]['message']['content']
    print(generated_flowchart_responses)

    output_path = "/home/ldamarala/Desktop/brd_project"
    output_mermaidjs_path = output_path.rstrip('/') + '/olobby_flowchart_diagram.html'

    with open(output_mermaidjs_path, "w") as file:
        file.write(generated_flowchart_responses)

    print(f"HTML content has been successfully written to {output_mermaidjs_path}")

    return print('flowchart_generated_successfully')

