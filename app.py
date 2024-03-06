from flask import Flask, render_template, request, redirect, url_for, send_file
from brd_gen import save_section_datain_DB
from use_case_gen import use_cases_gen,flowchart
from test_cases_gen import gen_testcases
from test_scripts_gen import test_scripts_gen
from boiler_template import boilerplate_gen
from section_change import brd_section_change,usecase_section_change,test_case_section_change,section_change_testscrpt
from queue import Queue
from threading import Thread
import zipfile
import sqlite3
import openai

app = Flask(__name__)
task_queue = Queue()


def db_update(project_name):
    # Connect to your SQLite database
    conn = sqlite3.connect('blueprint.db')
    cursor = conn.cursor()

    # Get the project_name from the form input
    # project_name = request.form['projectNameInput']

    # Update the row based on the project_name
    update_query = f'''
    UPDATE options
    SET
        "Brd-generator" = CASE WHEN "Project-name" = ? AND "Brd-generator" = 'In-Progress' THEN 'Done' ELSE "Brd-generator" END,
        "Use-cases" = CASE WHEN "Project-name" = ? AND "Use-cases" = 'In-Progress' THEN 'Done' ELSE "Use-cases" END,
        "test-cases" = CASE WHEN "Project-name" = ? AND "test-cases" = 'In-Progress' THEN 'Done' ELSE "test-cases" END,
        "test-scripts" = CASE WHEN "Project-name" = ? AND "test-scripts" = 'In-Progress' THEN 'Done' ELSE "test-scripts" END,
        "Boiler-templete" = CASE WHEN "Project-name" = ? AND "Boiler-templete" = 'In-Progress' THEN 'Done' ELSE "Boiler-templete" END
    WHERE "Project-name" = ?;
    '''

    # Execute the update query with the project_name
    cursor.execute(update_query, (project_name, project_name, project_name, project_name, project_name, project_name))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    return print("updated-db-successfully")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_type = request.form['userType']

        # Redirect based on the selected user type
        if user_type == 'admin':
            return redirect('/New_Project')
        elif user_type == 'user':
            return redirect('/Modify')

    return render_template('loginpage.html')

@app.route('/New_Project')
def brd_page():
    return render_template('brd.html')

@app.route('/generate_files', methods=['POST'])
def generate_files():
    project_name = request.form['projectNameInput']
    business_idea = request.form['textInput']
    uploaded_file = request.files['file']
    selected_option = request.form['selectedOption']
    # selected_options = request.form.getlist('selectedOptions')

    # # Connect to the SQLite database
    # conn = sqlite3.connect('blueprint.db')
    # cursor = conn.cursor()

    # # Define the table name
    # table_name = "options"

    # # Define the columns and their values
    # columns = ["Project-name", "Brd-generator", "Use-Cases", "test-cases", "test-scripts", "Boiler-templete"]
    # values = {"Project-name": project_name}

    # # Create the SQL query for insertion
    # column_str = ', '.join('"{}"'.format(col) for col in columns)
    # value_str = ', '.join(
    #     "'{}'".format("In-Progress" if col == selected_option else "Not_Yet") if col != "Project-name" else "'{}'".format(project_name)
    #     for col in columns
    # )
    # sql_query = "INSERT INTO {} ({}) VALUES ({})".format(table_name, column_str, value_str)

    # # Execute the SQL query
    # cursor.execute(sql_query)

    # # Commit the changes and close the connection
    # conn.commit()
    # conn.close()

    # Connect to the SQLite database
    conn = sqlite3.connect('blueprint.db')
    cursor = conn.cursor()

    # Define the table name
    table_name = "options"

    # Define the columns and their values
    columns = ["Project-name", "Brd-generator", "Use-Cases", "test-cases", "test-scripts", "Boiler-templete"]
    values = {"Project-name": project_name}

    # Create the SQL query for insertion
    column_str = ', '.join('"{}"'.format(col) for col in columns)

    # Determine the number of columns to set as "In-Progress" based on selected_option
    num_columns = columns.index(selected_option) + 1
    value_str = ', '.join(
        "'{}'".format("In-Progress" if i < num_columns else "Not_Yet") if col != "Project-name" else "'{}'".format(project_name)
        for i, col in enumerate(columns)
    )

    sql_query = "INSERT INTO {} ({}) VALUES ({})".format(table_name, column_str, value_str)

    # Execute the SQL query
    cursor.execute(sql_query)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # for option in selected_option:
    if selected_option == 'Brd-generator':
        task_queue.put(lambda: save_section_datain_DB(project_name, business_idea))
        # save_section_datain_DB(project_name,business_idea)
        task_queue.put(lambda: db_update(project_name))
    elif selected_option == 'Use-cases':
        task_queue.put(lambda: save_section_datain_DB(project_name, business_idea))
        task_queue.put(lambda: use_cases_gen(project_name, business_idea))
        task_queue.put(lambda: flowchart(project_name))
        task_queue.put(lambda: db_update(project_name))
        # use_cases_gen(project_name, business_idea)
        # flowchart(project_name)
    elif selected_option == 'test-cases':
        task_queue.put(lambda: save_section_datain_DB(project_name, business_idea))
        task_queue.put(lambda: use_cases_gen(project_name, business_idea))
        task_queue.put(lambda: flowchart(project_name))
        task_queue.put(lambda: gen_testcases(project_name, business_idea))
        task_queue.put(lambda: db_update(project_name))
        # gen_testcases(project_name,business_idea)
    elif selected_option == 'test-scripts':
        task_queue.put(lambda: save_section_datain_DB(project_name, business_idea))
        task_queue.put(lambda: use_cases_gen(project_name, business_idea))
        task_queue.put(lambda: flowchart(project_name))
        task_queue.put(lambda: gen_testcases(project_name, business_idea))
        task_queue.put(lambda: test_scripts_gen(project_name, business_idea))
        task_queue.put(lambda: db_update(project_name))
        # test_scripts_gen(project_name,business_idea)
    elif selected_option == 'Boiler-templete':
        task_queue.put(lambda: save_section_datain_DB(project_name, business_idea))
        task_queue.put(lambda: use_cases_gen(project_name, business_idea))
        task_queue.put(lambda: flowchart(project_name))
        task_queue.put(lambda: gen_testcases(project_name, business_idea))
        task_queue.put(lambda: test_scripts_gen(project_name, business_idea))
        # boilerplate_gen(business_idea,project_name)
        task_queue.put(lambda: boilerplate_gen(business_idea, project_name))
        task_queue.put(lambda: db_update(project_name))
    
    return render_template('confirmation_page.html', option = selected_option, projectname=project_name)
    # return redirect(url_for('projects'))

@app.route('/projects')
def projects():

    conn = sqlite3.connect("blueprint.db")
    cursor = conn.cursor()

    sql = "SELECT * FROM options"
    data = cursor.execute(sql).fetchall()

    conn.close()

    return render_template('Table.html', options=data)

@app.route('/project_details/<int:project_id>')
def project_details(project_id):

    conn = sqlite3.connect('blueprint.db')
    cursor = conn.cursor()

    # Fetch details for the project with the given project_id from the database
    sql = "SELECT * FROM options WHERE id = ?"
    cursor.execute(sql, (project_id,))
    project_details = cursor.fetchone()

    # Close the database connection
    conn.close()

    # For now, let's pass a placeholder
    # project_details = {'project_name': f'Project {project_id}', 'details': 'Some details...'}

    return render_template('EnteringProjectName.html', project_details=project_details)

def worker():
    while True:
        task = task_queue.get()
        try:
            task()
        except Exception as e:
            print(f"Error executing task: {e}")
        task_queue.task_done()

# Start the worker thread
worker_thread = Thread(target=worker, daemon=True)
worker_thread.start()

# @app.route('/download/<module_type>/<project_name>')
# def download_file(module_type, project_name):
#     # Replace these paths with the actual paths for each module
#     module_paths = {
#         'brd': url_for('static', filename='brd_project/brd_response.docx'),
#         'use_case': url_for('static', filename=f'brd_project/Gen_UseCase_for_{project_name}.docx'),
#         'test_script': url_for('static', filename=f'brd_project/Gen_TestScript_for_{project_name}.java'),
#         'test_case': url_for('static', filename=f'brd_project/Gen_TestCases_for_{project_name}.xlsx')
#     }


#     # Check if the module type is valid
#     if module_type in module_paths:
#         module_path = module_paths[module_type]
#     else:
#         return "Invalid module type"

#     # Generate the dynamic file name based on the project name
#     file_name = f"{module_type}_response_for_{project_name}.docx"

#     # Create a zip file containing the specified module
#     zip_filename = f"/home/ldamarala/Desktop/brd_project/{file_name}_files.zip"
#     with zipfile.ZipFile(zip_filename, 'w') as zipf:
#         zipf.write(module_path, file_name)

#     # Serve the file for download
#     return send_file(
#         zip_filename,
#         as_attachment=True
#     )

@app.route('/download')
def download_file():
    brd_path = "/home/ldamarala/Desktop/brd_project/Gen_BRD_Responses.docx"

    zip_filename = "/home/ldamarala/Desktop/brd_project/generated_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(brd_path, 'Gen_BRD_Responses.docx')

    # Serve the file for download
    return send_file(
        zip_filename,
        as_attachment=True
    )

@app.route('/download1')
def download_file1():
    brd_path = "/home/ldamarala/Desktop/brd_project/Gen_BRD_Responses.docx"
    use_case_path = "/home/ldamarala/Desktop/brd_project/Gen_UseCases.txt"
    flowchart_path = "/home/ldamarala/Desktop/brd_project/Gen_FlowChart.html"

    zip_filename = "/home/ldamarala/Desktop/brd_project/generated_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(brd_path, 'Gen_BRD_Responses.docx')
        zipf.write(use_case_path, 'Gen_UseCases.txt')
        zipf.write(flowchart_path, 'Gen_FlowChart.html')

    # Serve the file for download
    return send_file(
        zip_filename,
        as_attachment=True
    )

@app.route('/download2')
def download_file2():
    brd_path = "/home/ldamarala/Desktop/brd_project/Gen_BRD_Responses.docx"
    use_case_path = "/home/ldamarala/Desktop/brd_project/Gen_UseCases.txt"
    flowchart_path = "/home/ldamarala/Desktop/brd_project/Gen_FlowChart.html"
    test_case_path = "/home/ldamarala/Desktop/brd_project/Test_Cases.xlsx"

    zip_filename = "/home/ldamarala/Desktop/brd_project/generated_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(brd_path, 'Gen_BRD_Responses.docx')
        zipf.write(use_case_path, 'Gen_UseCases.txt')
        zipf.write(flowchart_path, 'Gen_FlowChart.html')
        zipf.write(test_case_path, 'Test_Cases.xlsx')

    # Serve the file for download
    return send_file(
        zip_filename,
        as_attachment=True
    )

@app.route('/download3')
def download_file3():
    brd_path = "/home/ldamarala/Desktop/brd_project/Gen_BRD_Responses.docx"
    use_case_path = "/home/ldamarala/Desktop/brd_project/Gen_UseCases.txt"
    flowchart_path = "/home/ldamarala/Desktop/brd_project/Gen_FlowChart.html"
    test_case_path = "/home/ldamarala/Desktop/brd_project/Test_Cases.xlsx"
    test_script_path = "/home/ldamarala/Desktop/brd_project/Selenium.java"

    zip_filename = "/home/ldamarala/Desktop/brd_project/generated_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(brd_path, 'Gen_BRD_Responses.docx')
        zipf.write(use_case_path, 'Gen_UseCases.txt')
        zipf.write(flowchart_path, 'Gen_FlowChart.html')
        zipf.write(test_case_path, 'Test_Cases.xlsx')
        zipf.write(test_script_path, 'Selenium.java')

    # Serve the file for download
    return send_file(
        zip_filename,
        as_attachment=True
    )

@app.route('/download4')
def download_file4():
    brd_path = "/home/ldamarala/Desktop/brd_project/Gen_BRD_Responses.docx"
    use_case_path = "/home/ldamarala/Desktop/brd_project/Gen_UseCases.txt"
    flowchart_path = "/home/ldamarala/Desktop/brd_project/Gen_FlowChart.html"
    test_case_path = "/home/ldamarala/Desktop/brd_project/Test_Cases.xlsx"
    test_script_path = "/home/ldamarala/Desktop/brd_project/Selenium.java"
    test_script_path = "/home/ldamarala/Desktop/brd_project/Boiler_Code_Template.docx"

    zip_filename = "/home/ldamarala/Desktop/brd_project/generated_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(brd_path, 'Gen_BRD_Responses.docx')
        zipf.write(use_case_path, 'Gen_UseCases.txt')
        zipf.write(flowchart_path, 'Gen_FlowChart.html')
        zipf.write(test_case_path, 'Test_Cases.xlsx')
        zipf.write(test_script_path, 'Selenium.java')
        zipf.write(test_script_path, 'Boiler_Code_Template.docx')

    # Serve the file for download
    return send_file(
        zip_filename,
        as_attachment=True
    )

@app.route('/editfile1')
def edit_file1():
    return render_template('Modifying.html')

@app.route('/editfile2')
def edit_file2():
    return render_template('Modifying1.html')

@app.route('/editfile3')
def edit_file3():
    return render_template('Modifying2.html')

@app.route('/editfile4')
def edit_file4():
    return render_template('Modifying3.html')

@app.route('/editfile5')
def edit_file5():
    return render_template('Modifying4.html')

@app.route('/editfiles', methods=['POST'])
def editfiles():
    selected_option = "Business Requirements Document"
    project_name = request.form['projectNameInput']
    section_name = request.form['sectionNameInput']
    additional_data = request.form['textInput']
    uploaded_file = request.files['file']
    task_queue.put(lambda: brd_section_change(section_name,project_name,additional_data))
    # brd_section_change(section_name,project_name,additional_data)
    return render_template('confirmation_page1.html', option = selected_option, projectname=project_name)

@app.route('/editfiles1', methods=['POST'])
def editfiles1():
    selected_option = "Use Cases"
    project_name = request.form['projectNameInput']
    section_name = request.form['sectionNameInput']
    additional_data = request.form['textInput']
    uploaded_file = request.files['file']
    task_queue.put(lambda: usecase_section_change(section_name, project_name, additional_data))
    task_queue.put(lambda: flowchart(project_name))
    # usecase_section_change(section_name,project_name,additional_data)
    return render_template('confirmation_page1.html', option = selected_option, projectname=project_name)

@app.route('/editfiles2', methods=['POST'])
def editfiles2():
    selected_option = "Test Cases"
    project_name = request.form['projectNameInput']
    section_name = request.form['sectionNameInput']
    additional_data = request.form['textInput']
    uploaded_file = request.files['file']
    task_queue.put(lambda: test_case_section_change(section_name, project_name, additional_data))
    # test_case_section_change(section_name,project_name,additional_data)
    return render_template('confirmation_page1.html', option = selected_option, projectname=project_name)

@app.route('/editfiles3', methods=['POST'])
def editfiles3():
    selected_option = "Test Scripts"
    project_name = request.form['projectNameInput']
    section_name = request.form['sectionNameInput']
    additional_data = request.form['textInput']
    uploaded_file = request.files['file']
    task_queue.put(lambda: section_change_testscrpt(section_name, project_name, additional_data))
    # section_change_testscrpt(section_name, project_name, additional_data)
    return render_template('confirmation_page1.html', option = selected_option, projectname=project_name)

@app.route('/modify')
def modify_page():
    return render_template('Modifying.html')

if __name__ == '__main__':
    app.run(debug=True)
