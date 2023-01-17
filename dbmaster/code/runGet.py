import dbmaster

with dbmaster.open('databaseTwo') as obj:
    print(obj.get(0,10))