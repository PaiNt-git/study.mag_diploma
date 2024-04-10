import json


def q_k_result_format_override(row):
    if hasattr(row, 'category'):
        row.category = row.category or ''
    if hasattr(row, 'name'):
        row.name = row.name or ''
    if hasattr(row, 'questions'):
        row.questions = '; '.join(row.questions) if row.questions and len(row.questions) else ''
    if hasattr(row, 'keywords'):
        row.keywords = ', '.join(row.keywords) if row.keywords and len(row.keywords) else ''
    if hasattr(row, 'result'):
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
