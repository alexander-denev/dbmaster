import PySimpleGUI_forDBMaster as sg
import dbmaster
from datetime import datetime

pageSize = 30
global close
close = False

def emptyWindow(Size = (300, 200)):
    global window
    window = sg.Window('DBMaster', size=Size, layout=[
        [sg.Menu([['File', ['New::-new-', 'Open', list(i+'::-open-' for i in dbmaster.getDbs()), '!Close::-close-', '---', 'Exit::-exit-']], ['!Edit', ['Insert::-insert-']]])]
    ])

def contentWindow(fileName):
    global window, table, menuButtons
    menuButtons = False
    db = dbmaster.open(fileName)
    try: Values = db.get(0,pageSize)
    except: Values = [list(['null'] for _ in range(len(db.columns())+1))]
    table = sg.Table(headings=['PK'] + db.columns(), values=Values, auto_size_columns=False, col_widths=[len(str(Values[len(Values)-1][0]))+1]+list(max(db.arrangement[i][1]+1, len(i)) for i in db.arrangement), num_rows=30, hide_vertical_scroll=True, font=('Arial', 14), justification='center', enable_events=True, key='-table-')
    window = sg.Window('DBMaster: '+db.fileName, use_default_focus = False, layout=[
        [sg.Menu([['File', ['New::-new-', 'Open', list(i+'::-open-' for i in dbmaster.getDbs()), 'Close::-close-', '---', 'Exit::-exit-']], ['Edit', ['Insert::-insert-', 'Update::-upt-', 'Delete::-del-', '---', 'Shrink::-shrink-']]], key='-themenu-')],
        [sg.Text('Search', font=('Arial', 15)), sg.Input(key='-search-', font=('Arial', 15), enable_events=True)],
        [table],
        [sg.Push(),sg.Button(button_text='<', key='-ppage-', font=('Arial', 20)), sg.Button(button_text='>', key='-npage-', font=('Arial', 20)), sg.Push()]
    ])

def newWindow():
    global windowNew, columns, fileName
    windowNew = sg.Window('DBMaster New Database', layout=[
        [sg.Text('Database name', font=('Arial', 15)), sg.Input(key='-dbname-', font=('Arial', 15), size=31, enable_events=True)],
        [sg.Text('Define column names (Separate with ;)', font=('Arial', 15))],
        [sg.Input(key='-columns-', font=('Arial', 15), enable_events=True),],
        [sg.Text('Additional options. Don\'t use if you don\'t know what you\'re doing:', font='Arial', text_color='dark gray')],
        [sg.Text('spacefill', font='Arial', text_color='dark gray'), sg.Input(key='-spacefill-', font='Arial', default_text='~', enable_events=True, size=1), sg.Text('pkLen', font='Arial', text_color='dark gray'), sg.Input(key='-pklen-', font='Arial', default_text='8', enable_events=True, size=4)],
        [sg.Submit(key='-submit_columns-', disabled=True), sg.Cancel(key='-cancel-')]
    ])
    while True:
        event, values = windowNew.read()
        if event in ('-columns-', '-dbname-', '-spacefill-', '-pklen-'):
            if all(value!='' for value in values.values()):
                windowNew.Element('-submit_columns-').Update(disabled=False)
            else:
                windowNew.Element('-submit_columns-').Update(disabled=True)
            if event == '-spacefill-' and len(values[event]) > 1:
                windowNew.Element(event).Update(values[event][:-1])
            if event == '-pklen-':
                try: int(values[event])
                except: windowNew.Element(event).Update(values[event][:-1])
        elif '-submit_columns-' == event:
            windowNew.close()
            spacefill = values['-spacefill-']
            name = values['-dbname-']
            pklen = int(values['-pklen-'])
            columns = values['-columns-'].split(';')
            windowNew = sg.Window('DBMaster New Database', layout=[
                [sg.Push(), sg.Text('Column', text_color='black', font=('Arial', 15), pad=(30,0)), sg.Text('Type', text_color='black', font=('Arial', 15), pad=(30,0)), sg.Text('Length', text_color='black', font=('Arial', 15), pad=(30,0))],
                ([sg.Push(), sg.Text(text=i, font=('Arial', 15)), sg.Input(key='-'+i+'_type-', font=('Arial', 15), enable_events=True, size=10), sg.Input(key='-'+i+'_len-', font=('Arial', 15), enable_events=True, disabled_readonly_background_color = 'dark gray', size=10)] for i in columns),
                [sg.Submit(key='-submit_new-', disabled=True), sg.Cancel(key='-cancel-')]
            ])
        elif '-cancel-' == event or sg.WIN_CLOSED == event:
            break
        elif '_type-' in event:
            if values[event] in ('date', 'time'):
                windowNew.Element(event[:event.find('_type-')]+'_len-').Update((10 if values[event] == 'date' else 8), disabled=True)
                values[event[:event.find('_type-')]+'_len-'] = (10 if values[event] == 'date' else 8)
            else:
                windowNew.Element(event[:event.find('_type-')]+'_len-').Update('', disabled=False)
                values[event[:event.find('_type-')]+'_len-'] = ''
        elif '_len-' in event:
            try: int(values[event])
            except: windowNew.Element(event).Update(values[event][:-1])
        elif '-submit_new-' == event:
            windowNew.close()
            window.close()
            params = {}
            filename = name
            fileName = name
            for i in list(i for i in values if '_type-' in i):
                params[i[1:i.find('_type-')]] = [values[i], int(values[i[:i.find('_type-')]+'_len-'])]  if values[i] not in ('date', 'time') else  [values[i]]
            try: dbmaster.open(filename, params, spacefill, pklen)
            except:
                try:
                    while True:
                        w = sg.Window('FIle Name Taken', layout=[[sg.Text('File name is taken, enter a different name:')], [sg.Input(key='-dbname-', enable_events=True)], [sg.Submit(key='-submit-'), sg.Cancel(key='-cancel-')]])
                        while True:
                            event, values = w.read()
                            if event in (sg.WIN_CLOSED, '-cancel-'): windowNew.close(); w.close(); raise Exception
                            elif event == '-dbname-': 
                                if values[event] != '': w.Element('-submit-').Update(disabled=False)
                                else: w.Element('-submit-').Update(disabled=False)
                            elif event == '-submit-':
                                filename = values['-dbname-']
                                break
                        w.close()
                        try: dbmaster.open(filename, params, spacefill, pklen)
                        except: continue
                except: pass
            contentWindow(filename)
        if '_len-' in event or '_type-' in event:
            if all(value!='' for value in values.values()) and all(value in ('int', 'str', 'float', 'date', 'time') for value in list(values[i] for i in values if '_type-' in i)):
                windowNew.Element('-submit_new-').Update(disabled=False)
            else:
                windowNew.Element('-submit_new-').Update(disabled=True)
    windowNew.close()

def insertWindow():
    global inswindow, window
    db = dbmaster.open(fileName)
    inswindow = sg.Window('Insert', layout=[
        [sg.Text('Column', text_color='black', font=('Arial', 15)), sg.Text('Type', text_color='dark gray', font=('Arial', 15)), sg.Push(), sg.Text('Value', text_color='black', font=('Arial', 15))],
        ([sg.Text(text=col, font=('Arial', 15)), sg.Text(db.arrangement[col][0], text_color='dark gray', font=('Arial', 15)), sg.Push(), sg.Input(key='-'+col+'_inscol-', font=('Arial', 15), enable_events=True, size=db.arrangement[col][1]+1)] for col in db.columns()),
        [sg.Submit(key='-submit_insert-', disabled=True), sg.Cancel(key='-cancel-')]
    ])
    while True:
        event, values = inswindow.read()
        if event in (sg.WIN_CLOSED, '-cancel-'):
            break
        elif '_inscol-' in event:
            type = db.arrangement[event[1:event.find('_inscol-')]][0]
            try:
                if type == 'int': int(values[event])
                elif type == 'float': float(values[event])
                elif type == 'str': str(values[event])
                elif type == "date" and len(values[event]) == 10: _ = datetime.strptime(values[event], "%Y-%m-%d")
                elif type == "time" and len(values[event]) == 8: _ = datetime.strptime(values[event], "%H:%M:%S")
                if len(values[event]) > db.arrangement[event[1:event.find('_inscol-')]][1]: raise Exception
            except: inswindow.Element(event).Update(values[event][:-1])
            if type == "date" and len(values[event]) == 11: values[event] = values[event][:-1]
            elif type == "time" and len(values[event]) == 9: values[event] = values[event][:-1]
            if all(list(len(values[value])==10 for value in values if (db.arrangement[value[1:value.find('_inscol-')]][0] == 'date') and len(values[value])!=0)) and all(list(len(values[value])==8 for value in values if (db.arrangement[value[1:value.find('_inscol-')]][0] == 'time') and len(values[value])!=0)):
                inswindow.Element('-submit_insert-').Update(disabled=False)
                inswindow.refresh()
            else:
                inswindow.Element('-submit_insert-').Update(disabled=True)
                inswindow.refresh()
        elif '-submit_insert-' == event:
            toInsert = {}
            for value in values:
                toInsert[value[1:value.find('_inscol-')]] = values[value]
            inswindow.close()
            return(toInsert, True)
    inswindow.close()
    return (None, False)

def updateWindow(entry):
    params = {}

    global uptwindow, window, close
    db = dbmaster.open(fileName)
    uptwindow = sg.Window('Update', layout=[
        [sg.Text('Column', text_color='black', font=('Arial', 15)), sg.Text('Type', text_color='dark gray', font=('Arial', 15)), sg.Push(), sg.Text('Value', text_color='black', font=('Arial', 15))],
        ([sg.Text(text=col, font=('Arial', 15)), sg.Text(db.arrangement[col][0], text_color='dark gray', font=('Arial', 15)), sg.Push(), sg.Push(), sg.Input(key='-'+col+'_uptcol-', font=('Arial', 15), enable_events=True, size=db.arrangement[col][1]+1, default_text=entry[list(db.arrangement).index(col)+1])] for col in db.columns()),
        [sg.Submit(key='-submit_update-', disabled=True), sg.Cancel(key='-cancel-')]
    ])
    while True:
        event, values = uptwindow.read()
        if event in (sg.WIN_CLOSED, '-cancel-'):
            break
        elif '_uptcol-' in event:
            type = db.arrangement[event[1:event.find('_uptcol-')]][0]
            try:
                if type == 'int': int(values[event])
                elif type == 'float': float(values[event])
                elif type == 'str': str(values[event])
                elif type == "date" and len(values[event]) == 10: _ = datetime.strptime(values[event], "%Y-%m-%d")
                elif type == "time" and len(values[event]) == 8: _ = datetime.strptime(values[event], "%H:%M:%S")
                if len(values[event]) > db.arrangement[event[1:event.find('_uptcol-')]][1]: raise Exception
            except: uptwindow.Element(event).Update(values[event][:-1])
            if type == "date" and len(values[event]) == 11: values[event] = values[event][:-1]
            elif type == "time" and len(values[event]) == 9: values[event] = values[event][:-1]
            if all(list(len(values[value])==10 for value in values if (db.arrangement[value[1:value.find('_uptcol-')]][0] == 'date') and len(values[value])!=0)) and all(list(len(values[value])==8 for value in values if (db.arrangement[value[1:value.find('_uptcol-')]][0] == 'time') and len(values[value])!=0)):
                uptwindow.Element('-submit_update-').Update(disabled=False)
                uptwindow.refresh()
            else:
                uptwindow.Element('-submit_update-').Update(disabled=True)
                uptwindow.refresh()
        elif '-submit_update-' == event:
            params = {}
            for value in values:
                params[value[1:value.find('_uptcol-')]] = values[value]
            uptwindow.close()
            close=True
            return(params)
    uptwindow.close()

def shrink():
    w = sg.Window('Shrink', use_default_focus=False, layout=[
            [sg.Text('Are you sure you want to SHRINK?', font=('Arial', 15))],
            [sg.Text('Doing this will irreversibly delete clean the inactive entries', font=('Arial',12))],
            [sg.Button('YES', font=('Arial', 12)), sg.Button('NO', font=('Arial', 12))]
            ])
    ev, vals = w.read()
    w.close()
    return ev

emptyWindow()

#mainloop()
entry = None
while True:
    event, values = window.read()

    # Exit
    if event in (sg.WIN_CLOSED, 'Exit::-exit-'): break

    # New
    elif '::-new-' in event:
        newWindow()

    # Open
    elif '::-open-' in event:
        fileName = event[:event.find('::-open-')]
        window.close()
        contentWindow(fileName)

    # Close
    elif '::-close-' in event:
        Size = window.Size
        window.close()
        emptyWindow(Size)

    # Next Page
    elif '-npage-' == event:
        try:
            table.update(dbmaster.open(fileName).get(table.Values[len(table.Values)-1][0]+1, pageSize))
        except: pass

    # Previous Page
    elif '-ppage-' == event:
        try:
            table.update(dbmaster.open(fileName).get(table.Values[0][0]-1, pageSize, backwards=True))
        except: pass

    # Insert
    elif '::-insert-' in event:
        v = insertWindow()
        if v[1] == True:
            dbmaster.open(fileName).insert(v[0])
            window.close()
            contentWindow(fileName)
    
    # Update
    elif '::-upt-' in event:
        if entry != None:
            pk = entry[0]
            params = updateWindow(entry)
            if close:
                close = False
                dbmaster.open(fileName).update(pk, params)
                window.close()
                contentWindow(fileName)
    
    # Selecting entry in table
    elif '-table-' == event:
        entry = table.Values[values['-table-'][0]]

    # Delete
    elif '::-del-' in event:
        if entry != None:
            pk = entry[0]
            dbmaster.open(fileName).delete(pk)
            window.close()
            contentWindow(fileName)

    # Shrink
    elif '::-shrink-' in event: 
        if shrink() == 'YES':
            dbmaster.open(fileName).shrink()

    # Search
    elif '-search-' == event:
        if len(values['-search-']) == 0:
            table.update(dbmaster.open(fileName).get(0,pageSize))
        else:
            try:table.update(dbmaster.open(fileName).search({values[event][:values[event].find(':')]:values[event][values[event].find(':')+1:]}, pageSize))
            except: pass
window.close()