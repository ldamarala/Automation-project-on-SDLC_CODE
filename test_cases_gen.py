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
    section_name = "use_cases"
    projectname = project_name 
    table_name = "use_cases"
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

def gen_testcases(project_name,business_idea):

    print("function_called")
    use_cases = db_connect(project_name)
    Structureof_Use_Cases = """
        Test Case ID:
        Test Case Description:
        Pre-Conditions:
        Test Steps:
        1.
        2.
        3.
        Expected Result:
        Failure Cases:
    """
    testcase_response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                # "content": "You are a helpful assistant that write test cases for the requriment include with Failure Cases and also Follow the format 'Test Case ID,Test Case Description,Pre-Conditions,Test Steps,Expected Result'"
                "content": "For the given Use_Cases and Structureof_Use_Cases. you are the QA Engineer generate the Test-Cases for all the given Use_Cases and also Follow the format 'Test Case ID,Test Case Description,Pre-Conditions,Test Steps,Expected Result,Failure Cases'"
            },
            {
                "role": "user",
                "content": f"Use_Cases: {use_cases}\n\nStructureof_Use_Cases: {Structureof_Use_Cases}"
            }
        ],
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    generated_testcase_responses = testcase_response['choices'][0]['message']['content']
    print(generated_testcase_responses)

    # Split the data into individual test cases
    test_cases = generated_testcase_responses.strip().split('\n\n')

    # Create a list to store the dictionaries for each test case
    test_case_data_list = []

    # Iterate through test cases and extract information
    for test_case in test_cases:
        lines = test_case.split('\n')
        test_case_data = {
            'Test Case ID': '',
            'Test Case Description': '',
            'Pre-Conditions': '',
            'Test Steps': '',
            'Expected Result': '',
            'Failure Cases': ''
        }

        current_key = None

        for line in lines:
            if line.startswith("Test Case ID:"):
                current_key = 'Test Case ID'
                test_case_data[current_key] = line.split(":")[1].strip()
            elif line.startswith("Test Case Description:"):
                current_key = 'Test Case Description'
                test_case_data[current_key] = line.split(":")[1].strip()
            elif line.startswith("Pre-Conditions:"):
                current_key = 'Pre-Conditions'
                test_case_data[current_key] = line.split(":")[1].strip()
            elif line.startswith("Test Steps:"):
                current_key = 'Test Steps'
            elif line.startswith("Expected Result:"):
                current_key = 'Expected Result'
                test_case_data[current_key] = line.split(":")[1].strip()
            elif line.startswith("Failure Cases:"):
                current_key = 'Failure Cases'
                test_case_data[current_key] = line.split(":")[1].strip()
            elif current_key:
                test_case_data[current_key] += ' ' + line.strip()

        test_case_data_list.append(test_case_data)

    # Create a DataFrame
    df = pd.DataFrame(test_case_data_list)

    # Display the DataFrame
    print(df)

    # Specify the Excel file path
    # excel_file_path = 'test_cases.xlsx'

    # filename = f"Gen_TestCases_for_{project_name}.xlsx"
    filename = f"Test_Cases.xlsx"
    path = "/home/ldamarala/Desktop/brd_project/"
    output_testcases_path = os.path.join(path, filename)

    # Save the DataFrame to Excel
    df.to_excel(output_testcases_path, index=False)

    print(f"DataFrame saved to {output_testcases_path}")

    # print(type(generated_testcase_responses))
    con = sqlite3.connect("blueprint.db")
    cursor = con.cursor()

    sql = "INSERT INTO test_cases (project_name, user_business_idea, test_cases) VALUES (?, ?, ?)"
    data = (project_name, business_idea, generated_testcase_responses)

    cursor.execute(sql, data)
    con.commit() 

    con.close()
    print("Use-Cases added to DB successfully!")

    return print("Excel file created successfully")
