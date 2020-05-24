import pyodbc

conn = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_zhemingx;pwd=RyyN7aEh46PyMLF3')
#  ^^^ 2 values must be change for your own program.

#  Since the CSIL SQL Server has configured a default database for each user, there is no need to specify it (<username>354)

cur = conn.cursor()

# to validate the connection, there is no need to change the following line
cur.execute('SELECT username from dbo.helpdesk')
row = cur.fetchone()
while row:
    print ('SQL Server standard login name = ' + row[0])
    row = cur.fetchone()

conn.close()

#  This program will output your CSIL SQL Server standard login,
#  If you see the output as s_<yourusername>, it means the connection is a success.
#  
#  You can now start working on your assignment.
# 

#judge if s string is a date-time for sql server
def is_validtime(time_str):
    if len(time_str) == 8: #20160111
        if time_str.isdigit():
            return 1
        else:
            return 0
    elif len(time_str) == 10: #2016-01-11
        if time_str[0:4].isdigit() and time_str[5:7].isdigit() and time_str[8:].isdigit():
            return 1
        else:
            return 0
#set the format time 20160111 (for compared)
def format_time(time_str):
    if len(time_str) == 8:
        return time_str
    if len(time_str) == 10:
        form_t = time_str[0:4]+time_str[5:7]+time_str[8:]
        return form_t
#compare format time time1>time2 return 1
def compare_time(time1, time2):
    time1 = format_time(time1)
    time2 = format_time(time2)

    if int(time1) > int(time2):
        return 1
    else:
        return 0
#judge if a string is a float_type
def is_float(s):
    if s.isdigit():
        return True

    return sum([n.isdigit() for n in s.strip().split('.')]) == 2

#Search Listing
#1. This function allows the user to search for a suitable listing the satisfies certain criteria. 
#2. A user should be able to set the following filters as their search criteria: minimum and 
#maximum price, number of bedrooms, and start and end date. 
#3. After the search is complete, a list of search results must be shown to the user. The list 
#must include the following information for each listing: id, name, first 25 characters of 
#description, number of bedrooms, price. The results can be shown on the terminal or in a 
#GUI.
#4. If the search result is empty, an appropriate message should be shown to the user.
#after search listing, prechoice will record listing_id alternatives 
prechoice = []
#record start_date and end_date and number_of_beds of user criteria
date_beds = []

def search_listings():
    connection = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_zhemingx;pwd=RyyN7aEh46PyMLF3')
    #create cursor
    cursor = connection.cursor()
    #user set the search criteria
    print('Here are five criteria you need to set: ')
    min_price = input('minimum price:')
    max_price = input('maximum price:')
    number_of_bedrooms = input('number of bedrooms:')
    start_date = input('start date:')
    end_date = input('end date:')
    print()

    #invalid input
    if not (is_float(min_price) and is_float(max_price) and number_of_bedrooms.isdigit() and  is_validtime(start_date)
            and is_validtime(end_date)):
        print('Invaild input for wrong type!')
        return 0

    if (float(min_price) > float(max_price) or compare_time(start_date,end_date) or int(number_of_bedrooms) <= 0 ):
        print('Invaild input for logic!')
        return 0
    
    parameters = [number_of_bedrooms, start_date, end_date, min_price, max_price, start_date, end_date]
    #sql query
    SQLCommand  = ('''select L.id, L.name, L.description, L.number_of_bedrooms, temp.total_price 
                      from Listings L,(select L.id, SUM(C.price) as total_price
				                       from Listings L, Calendar C
				                       where L.id = C.listing_id and L.number_of_bedrooms = ? and C.available = 1 
                                       and C.date >= ? and c.date <= ? and C.price >= ? and C.price <= ?
				                       group by L.id
				                       having COUNT(*) = DATEDIFF(dd,?,?) + 1) temp
                      where L.id = temp.id''')
    #processing query
    cursor.execute(SQLCommand,parameters)
    
    result = cursor.fetchone()

    if result:
        date_beds.append(start_date)
        date_beds.append(end_date)
        date_beds.append(number_of_bedrooms)
        print('According to your criteria, a list of search is shown here:')
        print()
        i = 1
        while result:
            prechoice.append(result[0])
            print(str(i)+'.')
            print('listing id: '+ str(result[0]))
            print('name: '+ str(result[1]))
            print('description: '+ str(result[2][0:25]))
            print('number of bedrooms: '+ str(result[3]))
            print('total price: '+ str(result[4]))
            print()
            i = i + 1
            result = cursor.fetchone()
    else:
        #result is empty
        print('No result according to your criteria')
        return 0
    #commiting any pending transaction to the database.
    connection.commit()
    #closing connection
    connection.close()

    return 1

#Book Listing   
#1. A user must be able to select a listing from the results of the function Search Listings and 
#book it. This can be done by entering the listing’s id in a terminal or by clicking at a listing
#in a GUI.
#2. All the booking information should be recorded in the Booking table. 
#3. When a listing is booked, the Calendar table needs to be updated as well. This should 
#happen by the first trigger you wrote for assignment 4.
def book_listing():
    connection = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_zhemingx;pwd=RyyN7aEh46PyMLF3')
    #create cursor
    cursor = connection.cursor()
    print()
    print('----------------------------------------------------------------------')
    print('Here you need to book a listing in terms of the search result: ')
    listingid = input('Enter the listing id you want to order: ')
    #ensure whether the input listing id is valid
    if not listingid.isdigit():
        print('Input invalid!')
        return 0
    flag = 0
    for prec in prechoice:
        if int(listingid) == prec:
            flag = 1
            break
    if not flag:
        print('Input invalid!')
        return 0
    else:
        #get the last booking id
        SQLCommand1 = ('select MAX(id) from Bookings')
        cursor.execute(SQLCommand1)
        last_id = cursor.fetchone()
        #commiting any pending transaction to the database.
        connection.commit()
        #new produced booking id
        if not last_id[0]:
            new_id = 1
        else:
            new_id = int(last_id[0]) + 1
        #input guest name, stay_from, stay_to, number_of_guests
        print()
        print('Give us some necessary additional information: ')
        guest_name = input('guest name: ')
        stay_from = date_beds[0]
        stay_to = date_beds[1]
        number_of_guests = input('number of guests: ')

        if not (number_of_guests.isdigit()):
            printf('Input invalid for number of guests type!')
            return 0
        if int(number_of_guests) <= 0 or int(number_of_guests) > int(date_beds[2]):
            print('Input invalid for number of guests logically!')
            return 0
        
        values = [new_id,listingid,guest_name,stay_from,stay_to,number_of_guests]

        #insert into bookings
        SQLCommand2 = ("INSERT INTO Bookings(id,listing_id,guest_name,stay_from,stay_to,number_of_guests)VALUES(?,?,?,?,?,?)")
        #processing query
        row_effect = cursor.execute(SQLCommand2,values).rowcount
        #commiting any pending transaction to the database.
        connection.commit()
        #closing connection
        connection.close()
        if row_effect == 0:
            print('Booking fail!')
            return 0
        else:
            print('Booking success!')
            return 1

#Write Review
#1. A user should be able to write a review of a listing after his stay in that listing.
#2. To write a review, a user must enter their name and the program should show all the 
#bookings of that user. Then the user can select one of their bookings and write a review of 
#that listing.
#3. The following information should be asked from the user who wants to write a review: 
#user’s name, current date, review text.
#4. The program should allow a review only if the given date is after the stay_to attribute of 
#the related booking record. You need to make sure that the triggers you implemented in 
#assignment 4 are working properly with your application program. If any error happened 
#in a trigger, your program should print the trigger’s error message and let the user know 
#that the review was not stored. 
def write_review():
    connection = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_zhemingx;pwd=RyyN7aEh46PyMLF3')
    #create cursor
    cursor = connection.cursor()
    print('---------------------------------------------------------------')
    #get user name
    user_name = input('Before review, please enter your name: ')
    print()
    #SQL query
    SQLCommand3 = ("select * from Bookings where guest_name = ?")
    cursor.execute(SQLCommand3,user_name)
    outputlist = cursor.fetchone()
    if not outputlist:
        #no matching listing order for this guest name
        print('No such guest!')
        return 0
    #set prechoice_id to record all booking id and listing_id alternatives of this guest
    prechoice_id = []
    prechoice_listing_id = []
    prechoice_stay_to = []
    i = 1
    while outputlist:
        prechoice_id.append(outputlist[0])
        prechoice_listing_id.append(outputlist[1])
        prechoice_stay_to.append(outputlist[4])
        print(str(i)+'.')
        print('id: '+str(outputlist[0]))
        print('listing_id: '+str(outputlist[1]))
        print('guest_name: '+str(outputlist[2]))
        print('stay from: '+str(outputlist[3]))
        print('stay to: '+str(outputlist[4]))
        print('number of guests: '+str(outputlist[5]))
        i = i + 1
        outputlist = cursor.fetchone()
    print()
    #commiting any pending transaction to the database.
    connection.commit()

    user_cid = input('Your review choice id: ')

    #verify if this choice id is valid

    flag = 0
    
    
    for cid in prechoice_id:
        if int(user_cid) == cid:
            flag = 1
            index = prechoice_id.index(cid)
            new_listing_id = prechoice_listing_id[index]
            turple_stay_to = prechoice_stay_to[index]
            break
    
    if not flag:
        print('not found your choice id!')
        return 0
    else:
        print()
        current_date = input('current date: ')

        if not is_validtime(current_date):
            return 0

        current_date = format_time(current_date)
        turple_stay_to = format_time(turple_stay_to)
    
        review_text = input('review text: ')
        print()

        #check if the current date meets the requirement
        if not compare_time(current_date,turple_stay_to):
            print('Your review should after your end date of booking!')
            return 0

        #set the new id for the inserted review
        SQLCommand4 = ("select MAX(id) from Reviews")
        cursor.execute(SQLCommand4)
        last_id = cursor.fetchone()
        #commiting any pending transaction to the database.
        connection.commit()

        new_id = last_id[0] + 1
        #SQL insert
        values = [new_listing_id,new_id,review_text,user_name]
        SQLCommand5 = ("INSERT INTO Reviews(listing_id,id,comments,guest_name)VALUES(?,?,?,?)") 
        row_effect = cursor.execute(SQLCommand5,values).rowcount
        #commiting any pending transaction to the database.
        connection.commit()
        #closing connection
        connection.close()

        if row_effect == 0:
            print('Review failed for trigger fault!')
            return 0
        else:
            print('Review success!')
            return 1

#deal with error step --continue or quit
def error_process():
    print(' _______________________________________________________________')
    print('|You want to continue or quit? enter 1 to continue, else quit   |')
    print('|_______________________________________________________________|')
    ans = input('Enter your choice: ')
    return ans

#here is the main function
while 1:
    print('           !         !                        O                   ')
    print('       -------------------  /                /  \                 ')
    print('       |                 | /                /    \                ')
    print('      /| AIRBNB   SYSTEM |/                /   _  \               ')
    print('     / |    ?        ?   |                /   |_|  \              ')
    print('    /  -------------------               /__________\             ')
    print('            |        |                    |        |              ')
    print('            |        |                    |  ____  |              ')
    print('            |        |                    |__|  |__|              ')
    print()
    print('------------------------------------------------------')
    print()
    print('Dear ladies or gentlemen,')
    print('     What can I do for you?')
    print('     Here are three options:')
    print()
    print('     1.Book Listings    2.Write Reviews   3.quit')
    print()
    ops = input('Please enter your choice: ')
    
    if ops == '3':
        break
    elif ops == '1':
        prechoice = []
        two_date = []
        output1 = search_listings()
        quit1 = 0
        while output1 == 0 and quit1 == 0:
            ans = error_process()
            if ans == '1':
                output1 = search_listings()
            else:
                quit1 = 1
        if quit1 == 1:
            break

        output2 = book_listing()
        quit2 = 0
        while output2 == 0 and quit2 == 0:
            ans = error_process()
            if ans == '1':
                output2 = book_listing()
            else:
                quit2 = 1
        if quit2 == 1:
            break
        print()
        print('Enjoy your time here!')
        print()
    elif ops == '2':
        output3 = write_review()
        quit3 = 0
        while output3 == 0 and quit3 == 0:
            ans = error_process()
            if ans == '1':
                output3 = write_review()
            else:
                quit3 = 1
        if quit3 == 1:
            break
        print()
        print('Thanks for your review!')
        print()
    else:
        print()
        print('Please enter valid choice!')
        print()
