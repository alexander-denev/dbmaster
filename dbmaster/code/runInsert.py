import dbmaster

params = {
    'name': 'Giorge',
    'family': 'Peshov',
    'number': '20107',
    'town': 'Sofia',
    'gender': 'C',
    'room': '408',
    'birthDate': '2006-08-22',
    'score': '6.00',
    'timeToSchool': '23:59:59'
}

obj = dbmaster.open('databaseTwo')
obj.insert(params)