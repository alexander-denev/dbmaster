import io, os, ast, datetime
from datetime import datetime
os.chdir(os.path.dirname(os.path.dirname(__file__))+'\databases') # Optional. Sets directory to be in folder databases

def getDbs() -> list: # Returns a list of all databases in the current directory
    Return = list(value[:value.find(".dbmd" if value.endswith(".dbmd") else ".dbmm" if value.endswith(".dbmm") else ".dbmt")] for value in os.listdir() if value.endswith(".dbmd") or value.endswith(".dbmm") or value.endswith(".dbmt"))
    Return = list(set(value for value in Return if Return.count(value) == 3))
    return Return   

class open(object):
        
    def __init__(self, fileName:str, arrangement:dict={}, spaceFill:chr='~', primKeyLen:int=8): # Initializer function
        str(fileName); dict(arrangement); int(primKeyLen)
        self.fileName = fileName

        if arrangement == {}: # Check if user tries to load or create database and if file with fileName already exists
            
            if os.path.exists(fileName + ".dbmd"): # If data file exists
                if os.path.exists(fileName + ".dbmm"): # If meta file exists 
                    if os.path.exists(fileName + ".dbmt"): # If tracking file exists. Then LOAD
                        self.fileData = io.open(fileName + ".dbmd", "r+", encoding='utf-8') # Open data file
                        self.fileMeta = io.open(fileName + ".dbmm", "r+", encoding='utf-8') # Open meta file
                        self.fileTrack = io.open(fileName + ".dbmt", "r+", encoding='utf-8') # Open tracking file
                        self.spaceFill = self.fileMeta.read(1)
                        read = ""
                        while "{" not in read:
                            read += self.fileMeta.read(1)
                        self.primKeyLen = int(read.strip("{"))
                        self.fileMeta.seek(self.fileMeta.tell() -1)
                        self.arrangement = ast.literal_eval(self.fileMeta.read(os.stat(fileName + ".dbmm").st_size-1)) # Parses it to dictionary
                    
                    else: raise Exception("Dbmaster: Tracking file with such name doesn't exit.")
                else: raise Exception("Dbmaster: Meta file with such name doesn't exit.")
            else: raise Exception("Dbmaster: Data file with such name doesn't exit.")
        else:
            if os.path.exists(fileName + ".dbmd") or os.path.exists(fileName + ".dbmm"):
                raise Exception('Dbmaster: Giving formatting arguments wilst a file/s with this name already exists')

            else: # New database
                if fileName == '': raise Exception("Dbmaster: Name can't be empty")
                try:
                    self.arrangement = dict(arrangement)
                    for key in self.arrangement:
                        if self.arrangement[key][0] == "date": self.arrangement[key] += [10]
                        elif self.arrangement[key][0] == "time": self.arrangement[key] += [8]
                        elif self.arrangement[key][0] != "date" and self.arrangement[key][0] != "time": self.arrangement[key][1]
                        if key == "__primaryKey__": raise Exception("Dbmaster: <__primaryKey__> is a \"system\" column - you can't use it, my friend")
                except: raise Exception("Dbmaster: Invalid create arguments")
                if len(spaceFill) != 1: raise Exception("Dbmaster: Invalid filler byte")
                self.spaceFill = spaceFill
                self.primKeyLen = primKeyLen
                self.fileData = io.open(fileName + ".dbmd", "w+", encoding='utf-8') # Create data file
                self.fileMeta = io.open(fileName + ".dbmm", "w+", encoding='utf-8') # Create meta file
                self.fileTrack = io.open(fileName + ".dbmt", "w+", encoding='utf-8') # Create tracking file
                self.fileMeta.write(self.spaceFill + str(self.primKeyLen) + str(self.arrangement)) # Write database formatting to meta file
                self.fileTrack.write('0')
        
        self.entryLength = sum(i[1] for i in self.arrangement.values()) + self.primKeyLen + 1 # Get length of one entry. Plus 1 for the <active> column
        read = self.fileTrack.read(int(os.stat(fileName + ".dbmt").st_size))
        if read == '': read = 1
        self.PKReached = int(read) # Get the reacher primar key
        self.numOfEntries = os.stat(fileName + ".dbmd").st_size / self.entryLength # Get number of entries in the file
        if float(self.numOfEntries).is_integer(): self.numOfEntries = int(self.numOfEntries)
        else: raise Exception('Dbmaster: Data is corrupt', self.numOfEntries) # Check if database is corrupt by deviding all of the entries's length by the length of a non-corrupt entry
        if len(self.spaceFill) != 1: raise Exception("Dbmaster: spaceFill must be 1 character long")
        if len(str(self.primKeyLen)) < 1: raise Exception("Dbmaster: Primary key length must be at least 1 characters long")

    def insert(self, toInsert:dict): # Insert to database
        dict(toInsert)
        if len(str(self.PKReached)) == self.primKeyLen +1: raise Exception("Dbmaster: End of database reached. Can't insert ;(")

        for key in toInsert: # Arguments checks
            if key not in self.arrangement: raise Exception("Dbmaster: Column <" + key + "> is not a valid column in this database")
            if len(str(toInsert[key])) > self.arrangement[key][1]: raise Exception("Dbmaster: Column <" + key + "> is bigger than the allocated space")
        write = ''
        for key in self.arrangement: # Converts insert dictionary argument into insertable string and inserts into database
            if key not in toInsert: toInsert[key] = ""

            try: # Column type check
                if len(str(toInsert[key])) == 0: pass
                elif self.arrangement[key][0] == "date": _ = datetime.strptime(str(toInsert[key]), "%Y-%m-%d")
                elif self.arrangement[key][0] == "time": _ = datetime.strptime(str(toInsert[key]), "%H:%M:%S")
                elif self.arrangement[key][0] == "int": int(str(toInsert[key]))
                elif self.arrangement[key][0] == "float": float(str(toInsert[key]))
                elif self.arrangement[key][0] == "str": str(str(toInsert[key]))
            except: raise Exception("Dbmaster: <" + key + "> is not a <" + self.arrangement[key][0] + ">")

            write += str(toInsert[key]) + ("".join(self.spaceFill for _ in range(self.arrangement[key][1]-len(str(toInsert[key])))))

        self.fileData.seek(0,2)
        self.fileData.write("1" + str(self.PKReached) + ("".join(self.spaceFill for _ in range(self.primKeyLen-len(str(self.PKReached))))) + write)
        self.PKReached += 1
        self.fileTrack.seek(0)
        self.fileTrack.write(str(self.PKReached))

    def search(self, toSearch:dict, length:int=100) -> list: # Search in database
        dict(toSearch)
        for key in toSearch: # Check if search argument/s are valid
            if key not in self.arrangement and key != "__primaryKey__":
                raise Exception('Dbmaster: <' + key + '> is not a valid column in the database')

        found = []
        for entry in range(self.numOfEntries): # Searches entries for passed filter and gives matching entries
            
            self.fileData.seek(self.entryLength * entry) # \
            if self.fileData.read(1) == "0": continue    #  Check if entry is deleted. If so, skip it.

            try:
                for key in toSearch:
                    if key == "__primaryKey__":
                        self.fileData.seek(self.entryLength * entry + 1) # The 1 is for the <active> column
                        if int(self.fileData.read(self.primKeyLen).strip(self.spaceFill)) != int(toSearch[key]):
                            raise Exception('genius way of breaking multiple loops')
                    else: # Calculate where in each entry it needs to start reading
                        columnOffset = 0
                        for i in self.arrangement:
                            if i == key:
                                break
                            columnOffset += self.arrangement[i][1]
                        self.fileData.seek(self.entryLength * entry + 1 + self.primKeyLen + columnOffset) # The 1 is for the <active> column
                        if not self.fileData.read(self.arrangement[key][1]).count(toSearch[key]):
                            raise Exception('genius way of breaking multiple loops')
            except:
                continue
            found.append(entry)
            if len(found) >= length:break
        
        result = []
        for i in found:
            self.fileData.seek(self.entryLength * i + 1 + self.primKeyLen) # The 1 is for the <active> column
            self.fileData.seek(self.entryLength * i + 1)
            result += [[int(self.fileData.read(self.primKeyLen).strip(self.spaceFill))]]
            for key in self.arrangement:
                result[found.index(i)] += [self.fileData.read(self.arrangement[key][1]).strip(self.spaceFill)]

        return result

    def get(self, pk:int, diap:int = 1, backwards:bool = False) -> list: # Get specified entries startng at <start> and ending at <start + end>
        int(pk); int(diap)
        if pk >= self.PKReached or pk < 0: raise Exception('Dbmaster: Primary key is out of bounds')
        if diap < 0: raise Exception('Dbmaster: Length can\'t be 0')

        data = self.search({'__primaryKey__':pk})

        if not backwards:
            while len(data) != diap:
                pk += 1
                if pk >= self.PKReached: break
                search = self.search({'__primaryKey__':pk})
                if not search: continue
                data += search
        else:
            while len(data) != diap:
                pk -= 1
                if pk < 0: break
                search = self.search({'__primaryKey__':pk})
                if not search: continue
                data += search
            data.reverse()

        return data

    def columns(self) -> list: # Returns a list of the columns names
        return list(self.arrangement.keys())

    def delete(self, pk:int): # Delete an entry
        int(pk)
        if pk < 0 or pk >= self.PKReached: raise Exception("Dbmaster: Primary key out of bounds")
        
        for entry in range(self.numOfEntries):
            self.fileData.seek(self.entryLength * entry + 1) # The 1 is for the <active> column
            if int(self.fileData.read(self.primKeyLen).strip(self.spaceFill)) == pk: 
                self.fileData.seek(self.entryLength * entry)
                if self.fileData.read(1) == "0": raise Exception("Dbmaster: Specified entry is already deleted")
                self.fileData.seek(self.entryLength * entry)
                self.fileData.write("0")
                return
        raise Exception("Dbmaster: Entry not found")

    def phoenix(self, pk:int): # Bring back an entry
        int(pk)
        if pk < 0 or pk >= self.PKReached: raise Exception("Dbmaster: Primary key out of bounds")
        
        for entry in range(self.numOfEntries):
            self.fileData.seek(self.entryLength * entry + 1) # The 1 is for the <active> column
            if int(self.fileData.read(self.primKeyLen).strip(self.spaceFill)) == pk: 
                self.fileData.seek(self.entryLength * entry)
                if self.fileData.read(1) == "1": raise Exception("Dbmaster: Specified entry is not deleted")
                self.fileData.seek(self.entryLength * entry)
                self.fileData.write("1")
                return
        raise Exception("Dbmaster: Entry not found")
 
    def update(self, pk:int, params:dict): # Update an entry

        for key in params: # Arguments checks
            if key not in self.arrangement.keys(): raise Exception("Dbmaster: Column <" + key + "> is not a valid column in this database")
            if len(params[key]) > self.arrangement[key][1]: raise Exception('Dbmaster: Length of <' + key + '> is larger than the allowed size of <' + str(self.arrangement[key][1]) + '>')
        if pk < 0 or pk >= self.PKReached: raise Exception("Dbmaster: Primary key out of bounds")

        for entry in range(self.numOfEntries):
            self.fileData.seek(self.entryLength * entry + 1) # The 1 is for the <active> column
            if int(self.fileData.read(self.primKeyLen).strip(self.spaceFill)) == pk:
                self.fileData.seek(self.entryLength * entry)
                read = self.fileData.read(self.entryLength)
                if read[0] == "0": raise Exception("Dbmaster: Cannot update deleted entry")

                for key in params:

                    try: # Column type check
                        if len(params[key]) == 0: pass
                        elif self.arrangement[key][0] == "date": _ = datetime.strptime(params[key], "%Y-%m-%d")
                        elif self.arrangement[key][0] == "time": _ = datetime.strptime(params[key], "%H:%M:%S")
                        elif self.arrangement[key][0] == "int": int(params[key])
                        elif self.arrangement[key][0] == "float": float(params[key])
                        elif self.arrangement[key][0] == "str": str(params[key])
                        else: raise Exception("Dbmaster: <" + key + "> is not a <" + self.arrangement[key][0] + ">")
                    except: raise Exception("Dbmaster: <" + key + "> is not a <" + self.arrangement[key][0] + ">")
                    
                    columnOffset = 1 + self.primKeyLen # Calculate where in each entry it needs to start reading
                    for i in self.arrangement:
                        if i == key:
                            break
                        columnOffset += self.arrangement[i][1]
                    read = read[:columnOffset] + params[key] + ("".join(self.spaceFill for _ in range(self.arrangement[key][1]-len(params[key])))) + read[columnOffset + self.arrangement[key][1]:]

                self.fileData.seek(self.entryLength * entry)
                self.fileData.write(read)
                return
        raise Exception("Dbmaster: Entry not found")

        self.fileData.seek(self.entryLength * pk)
        if self.fileData.read(1) == "0": raise Exception("Dbmaster: Cannot update deleted entry")
        for key in params:
            columnOffset = 1 # Calculate where in each entry it needs to start reading
            for i in self.arrangement:
                if i == key:
                    break
                columnOffset += self.arrangement[i][1]
            self.fileData.seek(self.entryLength * pk + columnOffset) # Seek to the correct position.
            self.fileData.write(params[key] + ("".join(self.spaceFill for _ in range(self.arrangement[key][1]-len(params[key])))))

    def close(self): # Should close everything needed to be closed
        self.fileData.close()
        self.fileMeta.close()
        del self

    def __enter__(self): # Support for "with" expression
        return self

    def __exit__(self, type, value, traceback): # Support for "with" expression
        self.close()

    def shrink(self):
        if os.path.exists("tempFileForDBMaster"): raise Exception("DBMaster: Delete file named <temfileForDBMaster> as DBMaster cannot shrink otherwise")
        fileNew = io.open("tempFileForDBMaster", "w", encoding='utf-8')
        for i in range(self.numOfEntries):
            self.fileData.seek(self.entryLength * i)
            if self.fileData.read(1) == "1":
                self.fileData.seek(self.entryLength * i)
                fileNew.write(self.fileData.read(self.entryLength))
        self.fileData.close()
        fileNew.close()
        os.remove(self.fileName + ".dbmd")
        os.rename("tempFileForDBMaster", self.fileName + ".dbmd")
        io.open(self.fileName + ".dbmd", "r+", encoding='utf-8')