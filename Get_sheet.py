import gspread

"""
Интеграция гугл таблиц с апи для алисы:)
тут происходит просто подключение и обработка всего
содержимого 
"""

gc = gspread.service_account(filename='base-383807-0e733b3a2dc5.json')
sh = gc.open("bd_magic")
worksheet = sh.sheet1

list_of_dicts = worksheet.get_all_records()
