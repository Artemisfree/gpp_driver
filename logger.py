import json


def log_telemetry(filename, telemetry_data):
    """
    Записывает телеметрические данные в файл.
    :param str filename: Имя файла, в который нужно записать данные.
    :param dict telemetry_data: Словарь с телеметрическими данными для записи.
    """
    with open(filename, 'a') as log_file:
        log_file.write(json.dumps(telemetry_data) + '\n')
