This MP is designed as a simple application program for the Airbnb database on terminal.
(You may need to enter cmd to input 'pip install pyodbc' in case you haven't install this module)
--------------------------------------------------------------------------------------------------
First you will see three options: 1. Booking Listings 2.Write Reviews 3.quit
and you need to enter your choice.

If you enter 1, 
	you are booking listings now. You need to set 5 criteria: minimum price, 
	maximum price, number of bedrooms, start date and end date. 

	*Here you need to pay attention that two prices here are float type,number of bedrooms is 
	integer type and two dates here can accept these styles: 
	'yyyymmdd','yyyy%mm%dd'(% could be '.','/','-'and so on). Any other date style cannot be 
	accepted. (like 2019.1.1 or 2019-1-1 is not accepted.)

	*If you input wrong style or wrong logic such as number_of_bedrooms <= 0 (also in the 
	following steps that require you to input information), you will get an error information 
	and the program will ask you if you want to quit or continue.

	Then a list of search will be shown and you need to input a listing id in the list as your
	choice. And input guest name and number of guests. Finally you will receive 'Booking success'
	if you book successfully.

If you enter 2, 
	you are writing reviews now. You need to input your name first. Then a list of bookings 
	will be shown. You need to choose one booking id. And then input the current date and your
	review text. If your current date is not later than your stay_to in that booking, you cannot
	submit your review successfully. If  your current date is later than your stay_to in that 
	booking but the insertion is still not successful, then you will recieve a trigger failure
	message. Or you will receive 'Review success'.

If you enter 3,
	you will quit this operation and exit the program.
If you enter any other choice,
	you will be acquired to enter choice again.
	
	




