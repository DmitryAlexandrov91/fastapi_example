from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.services.constants import REPORT_DATE_FORMAT, SECONDS_IN_HOUR
from app.services.utils import get_days_string


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(REPORT_DATE_FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {'title': f'Отчёт на {now_date_time}',
                       'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': 'Лист1',
                                   'gridProperties': {'rowCount': 100,
                                                      'columnCount': 11}}}]
    }
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheetid = response['spreadsheetId']
    return spreadsheetid


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheetid: str,
        charity_projects: list[dict],
        wrapper_services: Aiogoogle
) -> list[dict]:
    """Обновляет google таблицу.

    Возвращает модифицированный список словарей с новым ключом
    collection_time(время, затраченное на сбор средств).
    """
    now_date_time = datetime.now().strftime(REPORT_DATE_FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        ['Отчёт от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Называние проекта', 'Время сбора', 'Описание']
    ]

    for project in charity_projects:

        delta = project['close_date'] - project['create_date']

        project['collection_time'] = (
            f'{get_days_string(delta.days)}, '
            f'{delta // SECONDS_IN_HOUR}'
        )
        new_row = [
            str(project['name']),
            str(project['collection_time']),
            str(project['description'])
        ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )

    return charity_projects
