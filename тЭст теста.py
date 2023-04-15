import gspread

# Указываем путь к JSON
lenn = 0
gc = gspread.service_account(filename='base-383807-0e733b3a2dc5.json')
# Открываем тестовую таблицу
sh = gc.open("bd_magic")
worksheet = sh.sheet1

list_of_dicts = worksheet.get_all_records()
print(list_of_dicts)