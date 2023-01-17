import tkinter as tk
from tkinter import ttk
import dbmaster


root = tk.Tk()

root.title("DBMaster")
root.geometry("1000x700")
#root.iconbitmap("icon")


def newDB(): # Create a new database
    global db

    try: closeDB()
    except: pass

def openDB(fileName): # Open a database
    global db

    try: closeDB()
    except: pass

    db = dbmaster.open(fileName)
    theMenuBar_file.entryconfig("Close", state="normal")
    
    global frame
    frame = tk.Frame(root)
    frame.pack(side=tk.BOTTOM, fill='x')
    tree = ttk.Treeview(frame, columns=['PK'] + db.columns(), show='headings', height=30)
    tree.pack(fill='x')
    tree.heading('PK', text='PK')
    tree.column('PK', anchor=tk.W, width=10)
    for column in db.columns():
        tree.heading(column, text=column)
        tree.column(column, anchor=tk.W, width=10)
    toInsert = db.get(0,30)
    for i in range(len(toInsert[0])):
        tree.insert(parent='', index='end', iid=toInsert[0][i], text='', values=[toInsert[0][i]] + toInsert[1][i])
    
def closeDB(): # Close a database
    global db

    del db
    theMenuBar_file.entryconfig("Close", state="disabled")
    frame.destroy()


# The Menu Bar
theMenuBar = tk.Menu(root)
root.config(menu=theMenuBar)

# File Menu
theMenuBar_file = tk.Menu(theMenuBar,  tearoff=False)
theMenuBar.add_cascade(label="File", menu=theMenuBar_file)
theMenuBar_file.add_command(label="New", command=newDB)
theMenuBar_file_open = tk.Menu(theMenuBar_file, tearoff=False)
theMenuBar_file.add_cascade(label="Open", menu=theMenuBar_file_open)
for i in dbmaster.getDbs():
    theMenuBar_file_open.add_command(label=i, command=lambda:openDB(i))
theMenuBar_file.add_command(label="Close", command=closeDB, state="disabled")
theMenuBar_file.add_separator()
theMenuBar_file.add_command(label="Exit", command=root.quit)


root.mainloop()