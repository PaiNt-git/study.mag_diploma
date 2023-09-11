import json


def q_k_result_format_override(row):
    row.category = row.category or ''
    row.name = row.name or ''
    row.questions = '; '.join(row.questions) if row.questions and len(row.questions) else ''
    row.keywords = ', '.join(row.keywords) if row.keywords and len(row.keywords) else ''
    row.result = json.dumps(row.result, ensure_ascii=False) if row.result and len(row.result) else ''
    return row


def cell_editable(queryset_row, qt_item):
    # return False

    column_inx = qt_item.column()
    if column_inx > 0:
        return True
    table_widget = qt_item.tableWidget()
    vert = table_widget.horizontalHeaderItem(column_inx)
    column_name = vert.text()
    if column_name == 'id':
        return False
    return True
