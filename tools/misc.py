def get_html_table(input_list):
    html_table_buffer = '<table border=1 cellspacing=0 cellpadding=0>'
    for inner_list in input_list:
        html_table_buffer += '<tr>'
        for item in inner_list:
            if item is None:
                item = ''
            print(item, type(item))
            if isinstance(item, tuple):
                if isinstance(item[1], str):
                    html_table_buffer += '<td style=\'%s\'>%s</td>' % (item[0], item[1])
                elif isinstance(item[1], int):
                    html_table_buffer += '<td style=\'%s\'>%i</td>' % (item[0], item[1])
                else:
                    html_table_buffer += '<td style=\'%s\'>%.2f</td>' % (item[0], item[1])
            elif isinstance(item, str):
                html_table_buffer += '<td>%s</td>' % item
            elif isinstance(item, int):
                html_table_buffer += '<td>%i</td>' % item
            else:
                html_table_buffer += '<td>%.2f</td>' % item
        html_table_buffer += "</tr>"
    html_table_buffer += '</table>'
    return html_table_buffer
