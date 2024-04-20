import json

from sqlalchemy.inspection import inspect

from info_service.db_base import Session


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
    table_widget = qt_item.tableWidget()
    main_window = table_widget.window()
    table_widget_name = table_widget.objectName()

    column_inx = qt_item.column()
    if column_inx > 0:
        return True

    vert = table_widget.horizontalHeaderItem(column_inx)
    column_name = vert.text()
    if column_name == 'id':
        return False
    return True


def get_cell_edit_callback(main_window, table_widget_name, queryset, row_map_callback,
                           instance_edit_callback=(lambda table_widget, session, instance, row_map_callback, rowNum, colNum: False),
                           pk_col=0):
    """
    Конструктор калбеков для ечеек

    :param main_window:
    :param table_widget_name:
    :param queryset:
    :param row_map_callback:
    :param instance_edit_callback:
    :param pk_col:
    """
    entity = None
    try:
        if isinstance(queryset, list) and len(queryset):
            entity = inspect(queryset[0]).mapper
        else:
            entity = [item['entity'] for item in queryset.column_descriptions][0]
    except:
        pass

    row_map_callback = row_map_callback
    main_window = main_window

    def tablecell_edit_callback(self, row, column):
        nonlocal entity, row_map_callback, main_window
        if main_window.MAINWINDOW_LOCAL_STORAGE[f'_{table_widget_name}_paginate']: return None
        if not entity: return None
        if pk_col == column: return None
        session = Session()
        table_widget = getattr(main_window, f'{table_widget_name}')
        if pk_col is not None:
            pk_cell_val = int(table_widget.item(row, pk_col).text())
            instance = session.query(entity).get(pk_cell_val)
        else:
            instance = entity()
        instance_edit_callback(table_widget, session, instance, row_map_callback, row, column)

    return tablecell_edit_callback


def update_entity(table_widget, session, instance, row_map_callback, rowNum, colNum):
    main_window = table_widget.window()
    table_widget_name = table_widget.objectName()

    row = row_map_callback(instance)
    cell_val = table_widget.item(rowNum, colNum).text()
    entity = inspect(instance).mapper
    attr_name = list(row.keys())[colNum]
    instarrpr = getattr(entity.attrs, attr_name)
    typesql = str(instarrpr.columns[0].type)
    print(typesql)
    if typesql in ('VARCHAR', 'TEXT'):
        cell_val = cell_val
    elif typesql == 'VARCHAR[]':
        cell_val = [x.strip() for x in cell_val.split(';')]
    setattr(instance, attr_name, cell_val)
    session.add(instance)
    session.flush()
    session.commit()
