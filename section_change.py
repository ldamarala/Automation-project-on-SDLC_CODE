import openai
import sqlite3
import re
import os
import pandas as pd
from brd_gen import brd_create
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

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

def brd_section_change(section_name,project_name,additional_data):
    table_name = "brd_responses"

    connection = sqlite3.connect("blueprint.db")
    cursor = connection.cursor()
    query = f"SELECT {section_name} FROM {table_name} WHERE project_name = ?;"

    # Execute the query
    cursor.execute(query, (project_name,))

    # Fetch the result (assuming one row is returned)
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    section_response = openai.ChatCompletion.create(
    model="gpt-4-1106-preview",
    messages=[
          {
              "role": "system",
              "content": "For the given specific Section in BRD and its content along with additional data for that specific section.You are a Business Analyst improve the existing section in the BRD providing the additional data regarding to that section"
          },
          {
              "role": "user",
              "content": f"Section_name: {section_name}’\n\nSection_content: {result}\n\nAdditional_data: {additional_data}"
          }
      ],
      temperature=0.0,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=0.0
    )
    brdsection_responses = section_response['choices'][0]['message']['content']

    # Define a regular expression to match the content after "Section Content:"
    pattern = re.compile(r'Section_content:(.*)', re.DOTALL)

    # Use the regular expression to find the match in the string
    match = pattern.search(brdsection_responses)

    # Extract the content if there is a match
    if match:
        section_content = match.group(1).strip()
        print(section_content)
    else:
        print("Section Content not found.")

    connection = sqlite3.connect("blueprint.db")
    cursor = connection.cursor()

    section_content
    # new_value = 'new_value'  # Replace with the actual new value

    # Define the SQL query to update the column value for the selected id
    query = f"UPDATE {table_name} SET {section_name} = ? WHERE project_name = ?;"

    # Execute the query with the new value and id value as parameters
    cursor.execute(query, (section_content, project_name))

    # Commit the changes
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    print(f"Value for id={project_name} in {section_name} updated to {section_content}.")
    brd_create(project_name)
    return print("updated_the_BRD_section_file_created")

    

def usecase_section_change(section_name,project_name,additional_data):

    sample_usecase = "Login with username and password.If credentails are valid allow login.Otherwise throw message saying 'invalid login'.If Login is successful then verify default screen is dashboard.Otherwise display message 'did not meet expected result'.If dashboard is visible, Move to Folder Access screen and If Folder Access screen is visible Click on create folder.Otherwise say'Folder Access Sreen is not visible'.If the create folder pop-up is visible then enter folder name.Otherwise display message 'test case is failed as pop-up is not displayed'.Click on Enter and validate Folder is created successfully or not.If folder is created successfully then create a excel file in it.Otherwise display message 'folder is not created'.If the excel file is created then open the file through online editor.Otherwise display message 'file is not created'."

    connection = sqlite3.connect("blueprint.db")
    cursor = connection.cursor()
    table_name = "use_cases"

    query = f"SELECT {section_name} FROM {table_name} WHERE project_name = ?;"

    # Execute the query
    cursor.execute(query, (project_name,))

    # Fetch the result (assuming one row is returned)
    use_cases = cursor.fetchone()

    cursor.close()
    connection.close()

    edit_usecase_response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "For the given Use_Cases, additional_data and sample_usecase. You are a Business Analyst correct the Generated use_cases and make use of additional_data."
            },
            {
                "role": "user",
                "content": f"Use_Cases: {use_cases}’\n\nadditional_data: {additional_data}\n\nsample usecase: {sample_usecase}"
            }
        ],
        temperature=0.0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    generated_edited_usecase_responses = edit_usecase_response['choices'][0]['message']['content']
    # print(generated_edited_usecase_responses)
    # business_idea = db_connect(project_name)
    filename = f"Gen_UseCases.txt"
    path = "/home/ldamarala/Desktop/brd_project/"
    file_path = os.path.join(path, filename)

    # Open the file in write mode and write the string data to the file
    with open(file_path, "w") as file:
        file.write(generated_edited_usecase_responses)

    # Connect to your SQLite database
    conn = sqlite3.connect('blueprint.db')
    cursor = conn.cursor()

    # Update the row based on the project_name
    update_query = '''
    UPDATE use_cases
    SET use_cases = ?
    WHERE project_name = ?;
    '''

    # Execute the update query with the provided values
    cursor.execute(update_query, (generated_edited_usecase_responses, project_name))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Use-Cases added to DB successfully!")

    
    return print("updated_the_usecase_section_file_created")

def test_case_section_change(section_name, project_name, additional_data):

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
    connection = sqlite3.connect("blueprint.db")
    cursor = connection.cursor()
    table_name = "test_cases"

    query = f"SELECT {section_name} FROM {table_name} WHERE project_name = ?;"

    # Execute the query
    cursor.execute(query, (project_name,))

    # Fetch the result (assuming one row is returned)
    test_cases = cursor.fetchone()

    cursor.close()
    connection.close()

    edit_testcase_response = openai.ChatCompletion.create(
    model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "For the given Test_Cases, additional_data and Structureof_Use_Cases. You are the QA Engineer correct the Generated Test-cases and make use of additional_data.Provide overall the test-cases after adding/editing."
            },
            {
                "role": "user",
                "content": f"Test_Cases: {test_cases}’\n\nadditional_data: {additional_data}\n\nStructureof_Use_Cases: {Structureof_Use_Cases}"
            }
        ],
        temperature=0.0,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    generated_edited_testcase_responses = edit_testcase_response['choices'][0]['message']['content']
    test_cases = generated_edited_testcase_responses.strip().split('\n\n')

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

    filename = f"Test_Cases.xlsx"
    path = "/home/ldamarala/Desktop/brd_project/"
    output_testcases_path = os.path.join(path, filename)

    # Save the DataFrame to Excel
    df.to_excel(output_testcases_path, index=False)

    print(f"DataFrame saved to {output_testcases_path}")

    # business_idea = db_connect(project_name)

    con = sqlite3.connect("blueprint.db")
    cursor = con.cursor()

    # Update the row based on the project_name
    update_query = '''
    UPDATE test_cases
    SET test_cases = ?
    WHERE project_name = ?;
    '''

    # Execute the update query with the provided values
    cursor.execute(update_query, (generated_edited_testcase_responses, project_name))

    # Commit the changes and close the connection
    con.commit()
    con.close()

    print("Test-Cases added to DB successfully!")

    return print("Section_change_for_testcases_successfully")
    
def section_change_testscrpt(section_name, project_name, additional_data):
    automation_language = "Java"
    connection = sqlite3.connect("blueprint.db")
    cursor = connection.cursor()
    table_name = "test_scripts"

    query = f"SELECT {section_name} FROM {table_name} WHERE project_name = ?;"

    # Execute the query
    cursor.execute(query, (project_name,))

    # Fetch the result (assuming one row is returned)
    test_scripts = cursor.fetchone()

    cursor.close()
    connection.close()

    edited_seleniumcode_response = openai.ChatCompletion.create(
    model="gpt-4-1106-preview",
        messages=[
            {
             "role": "system",
            #  "content": "Based on the provided Test-Cases and automation_language, You are the QA Automation Engineer Generate the Selenium automation script all the Test-cases."
             "content": "Based on the provided Test-scripts, additional_data and automation_language, You are the QA Automation Engineer Correct the Generated Selenium automation script and make use of additional_data.Provide overall the Selenium automation script after adding/editing." 
             },
            {
                "role": "user",
                "content": f"Test-scripts: {test_scripts}’\n\nAutomation_Language: {automation_language}\n\nAdditional_data: {additional_data}"
            }
        ],
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    selenium_code_response = edited_seleniumcode_response['choices'][0]['message']['content']

    output_code_path = f"/home/ldamarala/Desktop/brd_project/Selenium"
    file_extension = ".java" if automation_language.lower() == "java" else ".py"
    file_name = output_code_path + file_extension
    with open(file_name, "w") as file:
        file.write(selenium_code_response)
    print(f"Generated code saved to {file_name}")

    con = sqlite3.connect("blueprint.db")
    cursor = con.cursor()

    update_query = '''
    UPDATE test_scripts
    SET test_scripts = ?
    WHERE project_name = ?;
    '''

    # Execute the update query with the provided values
    cursor.execute(update_query, (selenium_code_response, project_name))
    print("Test-Scripts added to DB successfully!")

    return print("section_change_test-scripts-generated successfully")
