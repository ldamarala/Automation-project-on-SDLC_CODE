from flask import Flask, render_template, request, redirect, url_for, send_file
from brd_gen import save_section_datain_DB
from use_case_gen import use_cases_gen,flowchart
from test_cases_gen import gen_testcases
from test_scripts_gen import test_scripts_gen
from boiler_template import boilerplate_gen
import zipfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_type = request.form['userType']

        # Redirect based on the selected user type
        if user_type == 'admin':
            return redirect('/brd')
        elif user_type == 'user':
            return redirect('/modify')

    return render_template('loginpage.html')

@app.route('/brd')
def brd_page():
    return render_template('brd.html')

@app.route('/generate_files', methods=['POST'])
def generate_files():
    project_name = request.form['projectNameInput']
    business_idea = request.form['textInput']
    uploaded_file = request.files['file']
    # selected_option = request.form['selectedOption']
    selected_options = request.form.getlist('selectedOptions')

    for option in selected_options:
        if option == 'Brd_Generator':
            save_section_datain_DB(project_name,business_idea)
        elif option == 'Use-cases':
            use_cases_gen(project_name, business_idea)
            flowchart(project_name)
        elif option == 'test-cases':
            gen_testcases(project_name,business_idea)
        elif option == 'test-scripts':
            test_scripts_gen(project_name,business_idea)
        elif option == 'Boiler_templete':
            boilerplate_gen(business_idea)


    # save_section_datain_DB(project_name,business_idea)
    # print('fuctionended')
    # use_cases_gen(project_name,business_idea)

    return render_template('brd.html')

@app.route('/download')
def download_file():
    brd_path = "/home/ldamarala/Desktop/brd_project/newOlobbybrd_response_record_olobby.docx"
    use_case_path = "/home/ldamarala/Desktop/brd_project/gen_usecase.txt"
    flowchart_path = "/home/ldamarala/Desktop/brd_project/olobby_flowchart_diagram.html"
    test_case_path = "/home/ldamarala/Desktop/brd_project/test_cases.xlsx"
    test_script_path = "/home/ldamarala/Desktop/brd_project/selenium.java"

    zip_filename = "/home/ldamarala/Desktop/brd_project/generated_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        zipf.write(brd_path, 'newOlobbybrd_response_record_swiftselect.docx')
        zipf.write(use_case_path, 'gen_usecase.txt')
        zipf.write(flowchart_path, 'olobby_flowchart_diagram.html')
        zipf.write(test_case_path, 'test_cases.xlsx')
        zipf.write(test_script_path, 'selenium.java')


    # Serve the file for download
    return send_file(
        zip_filename,
        as_attachment=True
    )

@app.route('/modify')
def modify_page():
    return render_template('Modifying.html')

if __name__ == '__main__':
    app.run(debug=True)
