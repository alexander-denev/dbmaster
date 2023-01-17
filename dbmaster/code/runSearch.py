import dbmaster

params = {
    '__primaryKey__':'6'
}

obj = dbmaster.open('databaseTwo')
print(obj.search(params))