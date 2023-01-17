import dbmaster

params = {
    'name': ['str', 15] ,
    'family': ['str', 20] ,
    'number': ['int', 5] ,
    'town': ['str', 20] ,
    'gender': ['str', 1] ,
    'room': ['int', 3] ,
    'birthDate': ['date'] , 
    'score': ['float', 4] ,
    'timeToSchool': ['time']
}

params2 = {
    'n': ['str', 5], 
    'd': ['date']
}

obj = dbmaster.open('db2', {'n': ['str', 5], 'd': ['date']}, '~', 8)