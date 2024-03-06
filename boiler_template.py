import openai
from docx import Document

def save_text_to_docx(text, file_path):
    doc = Document()
    doc.add_paragraph(text)

    # Save the document to the specified path
    doc.save(file_path)

def boilerplate_gen(business_idea,project_name):
    boilercode_response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "Based on the provided Business_idea of an application. Please generate Boilerplate code or folder structure at Engineer level:"
            },
            {
                "role": "user",
                "content": f"Business_idea: {business_idea}"
            }
        ],
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    boildercode_response = boilercode_response['choices'][0]['message']['content']
    print(boildercode_response)

    save_text_to_docx(boildercode_response, f'/home/ldamarala/Desktop/brd_project/Boiler_Code_Template.docx')

    return print("boiler_template_created_successfully")



