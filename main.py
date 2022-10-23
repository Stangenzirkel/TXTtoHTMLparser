from flask import Flask, render_template, request
import os
app = Flask(__name__)


def get_color_dict(file):
    with open(file, "r") as file:
        lines = file.read().split("\n")

    cd = dict()
    for line in lines:
        key, values = tuple(line.split(": "))
        cd[key] = values

    return cd


def parse_text_to_html(text, data):
    if not isinstance(text, str):
        return "<table id=\"table\">""</table>"

    try:
        cd = get_color_dict("colors.txt")
        text = text.replace("\r", "")
        text = text.split("\n")
        cur_text_line_num = text.index("Товар\tМодель\tКол-во\tЦена за ед.\tВсего") + 1
        table = []
        cur_row = -1
        while True:
            cur_text_line = text[cur_text_line_num]
            if "Предварительная стоимость" in cur_text_line:
                break

            if cur_text_line[:4] != "  - ":
                cur_row += 1
                table.append(["", "", "", ""])
                if cur_text_line.count("\t") == 4:
                    cur_text_line = cur_text_line.split("\t")
                    table[cur_row][1] = cur_text_line[1]
                    table[cur_row][3] = cur_text_line[2]
                    cur_text_line = cur_text_line[0]

            if cur_text_line[:4] != "  - ":
                table[cur_row][0] = cur_text_line
            elif cur_text_line[:10] == "  - ЦВЕТ: ":
                    color = cur_text_line.replace("  - ЦВЕТ: ", "")
                    if color in cd:
                        color = cd[color]
                    table[cur_row][2] = color
            else:
                table[cur_row][0] = table[cur_row][0] + " " + cur_text_line.replace("  - ", "")
            cur_text_line_num += 1

        html_table = "<table id=\"table\">"
        for i, line in enumerate(table):
            html_table += "<tr>"
            if i == 0:
                html_table += f"<td rowspan={cur_text_line_num}>{data['num'] if 'num' in data else ''}</td>"
                html_table += f"<td rowspan={cur_text_line_num}>{data['date'] if 'date' in data else ''}</td>"
                html_table += f"<td rowspan={cur_text_line_num}>{data['sth'] if 'sth' in data else ''}</td>"
            html_table += f"<td>{line[0]}</td>"
            html_table += f"<td>{line[1]}</td>"
            html_table += f"<td>{line[2]}</td>"
            html_table += f"<td>{line[3]}</td>"
            html_table += "</tr>"
        html_table += "</table>"

        return html_table

    except Exception as e:
        return "<table id=\"table\"><tr><td>" + "Ошибка\n" + str(e) + "</tr></td></table>"


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        my_data = parse_text_to_html(request.args.get('description'), {'num': request.args.get('num')})

    else:
        my_data = parse_text_to_html(request.form['description'], {'num': request.form['num']})

    return render_template("index.html", data=my_data)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
