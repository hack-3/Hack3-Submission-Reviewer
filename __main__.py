from flask import Flask, request, render_template, redirect, url_for
from core import core_functions

app = Flask(__name__)


@app.route("/")
def index():
    return "This is default page"


@app.route("/check", methods=["GET", "POST"])
def check():
    query = request.args.to_dict()

    if request.method == "GET":
        if "devpost" not in query:
            return render_template("check.html")
        else:
            t1 = f"<h2>Project Url</h2>"
            q = f'<a href="{query["devpost"]}" target="_blank" rel="noreferrer noopener">Inputted Project</a>'
            t2 = """
            <tr>
                <th><h2>Similar Projects</h2></th>
            </tr>
            """
            t3 = """
            <tr>
                <th colspan="3"><h2>Similar Files</h2></th>
            </tr>
            """

            table = "<table>{2}{0}{1}</table"
            project_head = """
                <tr>
                    <th>Devpost Link</ht>
                </tr>
            """
            file_head = """
                <tr>
                    <th>File Name</ht>
                    <th>Github Link</ht>
                    <th>Devpost Link</ht>
                </tr>
            """

            project_template = """
                <tr>
                    <td><a href="{0}" target="_blank" rel="noreferrer noopener">{0}</a></td>
                </tr>
            """
            file_template = """
                <tr>
                    <td>{2}</td>
                    <td><a href="{1}" target="_blank" rel="noreferrer noopener">{1}</a></td>
                    <td><a href="{0}" target="_blank" rel="noreferrer noopener">{0}</a></td>
                </tr>
            """

            style = """
            <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            th, td {
                padding: 5px;
            }
            th {
                  text-align: left;
            }
            </style>"""

            # project_template = '<p><b>Devpost Link</b>: <a href="{0}" target="_blank" rel="noreferrer noopener">{0}</a></p>'
            # file_template = '<p><b>File Name</b>: {2}     <b>Devpost Link</b>: <a href="{1}" target="_blank" rel="noreferrer noopener">{1}</a>     <b>Github Link</b>: <a href="{0}" target="_blank" rel="noreferrer noopener">{0}</a></p>'

            data = core_functions.check_file(query['devpost'])

            p = data[0]
            d = data[1]

            projects = [project_template.format(i) for i in p]
            files = [file_template.format(*i) for i in d]

            doc = f"<html>{style}<body>{t1}{q}<br>{table.format(project_head, ''.join(projects), t2)}<br>{table.format(file_head, ''.join(files), t3)}</body>"

            # return "<html>" + style + "<body>" + t1 + q + t2 + table.format(project_head, ''.join(projects)) + t3 + table.format(file_head,''.join(files)) + "</body>" "</html>"
            return doc

    elif request.method == "POST":
        return redirect(f"/check?devpost={request.form.get('textbox')}")


app.run()
