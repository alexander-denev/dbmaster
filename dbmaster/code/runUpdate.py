import dbmaster

params = {
    'room':'417',
    'name':'Bob',
    'timeToSchool': '07:57:32'
}

obj = dbmaster.open('databaseTwo')
obj.update(6, params)