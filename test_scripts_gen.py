import sqlite3
import pandas as pd
import re
import openai
import ipywidgets as widgets
import requests
import os
import pandas as pd
import datetime
from fpdf import FPDF
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from IPython.display import HTML
from docx import Document

openai.api_key = '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'

def db_connect(project_name):
    connection = sqlite3.connect("blueprint.db")
    cursor = connection.cursor()
    section_name = "test_cases"
    projectname = project_name 
    table_name = "test_cases"
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

def test_scripts_gen(project_name, business_idea):
    generated_testcase_responses = db_connect(project_name)
    automation_language = "Java"
    seleniumcode_response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {
             "role": "system",
            #  "content": "Based on the provided Test-Cases and automation_language, You are the QA Automation Engineer Generate the Selenium automation script all the Test-cases."
             "content": "Based on the provided Test-cases and automation_language, Generate the Selenium automation script for each and every Test-case in the given Test-Cases and in the given automation_language"
             },
            {
                "role": "user",
                "content": f"Test-cases: {generated_testcase_responses}’\n\nAutomation_Language: {automation_language}"
            }
        ],
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    selenium_code_response = seleniumcode_response['choices'][0]['message']['content']
    print(selenium_code_response)
    # Determine the file extension based on the selected language
    file_extension = ".java" if automation_language.lower() == "java" else ".py"
    # Save the generated code to a file
    output_code_path = "/home/ldamarala/Desktop/brd_project/selenium"
    file_name = output_code_path + file_extension
    with open(file_name, "w") as file:
        file.write(selenium_code_response)
    print(f"Generated code saved to {file_name}")

    con = sqlite3.connect("blueprint.db")
    cursor = con.cursor()

    sql = "INSERT INTO test_scripts (project_name, user_business_idea, script, test_scripts) VALUES (?, ?, ?, ?)"
    data = (project_name, business_idea, automation_language, selenium_code_response)

    cursor.execute(sql, data)
    con.commit() 

    con.close()
    print("Use-Cases added to DB successfully!")
    return print("test-scripts-generated successfully")