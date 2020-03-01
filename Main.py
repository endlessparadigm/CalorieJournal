# Food Journal
import mysql.connector
from datetime import date

#  Create DB Connection
connection = mysql.connector.connect(
	host="localhost",
	user="root",
	passwd="6y7u8i9o",
	database="journalDB")

# I tried to set up a webhost so this could be run by anyone, but I think road runner (spectrum) was not allowing
# this
#connectionTest = mysql.connector.connect(
#	host="gator4271.hostgator.com",
#	user="mokhu_admin",
#	passwd="adminpass",
#	database="mokhu_foodJournal")


def main():  # Execute app, user login
	cursor = connection.cursor(buffered=True)
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print("############FOOD JOURNAL############")
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	userName = str(input("Please enter username:"))
	nameSQL = "SELECT name FROM user WHERE name = %s"
	try:  # Check user exists
		cursor.execute(nameSQL, (userName, ))
		myName = str(cursor.fetchone()[0])
	except:  # Add user
		choice = input("Name not found. Would you like to create a new account? If so, type New, otherwise, enter any "
					   "key to quit.")
		if choice == "New":
			myName = input("Please enter your name:")
			addEntrySQL = "INSERT INTO user (name) VALUES (%s)"
			cursor.execute(addEntrySQL, (myName, ))
			connection.commit()
		else:
			print("Have a great day!")
	cursor.close()
	mainMenu(myName)


def mainMenu(userName):
	print("Welcome, ", userName, "!")
	choice = input("Please select an option. J to access your journal log or M to check on the nutrition metrics. (Q to Quit.)")
	if choice == "J":  # go to Journal Menu
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		print("############   JOURNAL   ############")
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		journalMenu(userName)
	elif choice == "M":  # Go to Metrics Menu
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		print("############   METRICS   ############")
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		calcMenu(userName)
	elif choice == "Q":
		return
	else:
		print("Please verify the menu entry.")
		calcMenu(userName)


def journalMenu(userName):  # Journal Entry
	cursor = connection.cursor(buffered=True)
	print("To start, please specify meal: Breakfast, Lunch, Dinner.")
	mealType = input()
	# SQL Statements Prep
	foodItemSQL = "SELECT foodName FROM foodList WHERE foodName = %s"
	totalFoodListSQL = "SELECT foodName FROM foodList"
	servingAmtSQL = "SELECT servingType FROM foodList WHERE foodName = %s"
	# Enter item to add
	foodItem = input("Please enter the food item you ate today. If you'd like to see a list of options, type FoodList.")
	# Print list of food items in DB
	if foodItem == "FoodList":
		cursor.execute(totalFoodListSQL)
		allFoods = cursor.fetchall()
		print("Food List: ")
		for row in allFoods:
			print((row[0]), "\t")
	else:  # Add food, determine amounts, print output
		cursor.execute(foodItemSQL, (foodItem, ))
		myFood = str(cursor.fetchone()[0])
		cursor.execute(servingAmtSQL, (foodItem, ))
		servingType = str(cursor.fetchone()[0])
		print("Item: ", myFood, ".", "Please enter amount - serving size is:", "(", servingType, ")", myFood)
		myAmt = input()
		print("You have entered: ", myAmt, servingType, myFood, "- if this is correct, press enter. To restart, type R")
		mySub = input()
		if mySub == "R":
			journalMenu()
		else:
			today = str(date.today())
			addEntrySQL = "INSERT INTO Journal (userName, date, mealType, foodName, quantity) VALUES (%s, " \
						"%s, %s, %s, %s)"
			cursor.execute(addEntrySQL, (userName, today, mealType, foodItem,  myAmt))
			connection.commit()
			print("You have added: ", myAmt, servingType, foodItem)
	# Rerun Item Add
	choice = input("Add to journal - Type Q to Quit or Enter to input additional food to your journal.")
	if choice == "Q":
		print("Thanks for adding a food entry!")
		cursor.close()
		mainMenu(userName)
	else:  # Back to main menu
		cursor.close()
		journalMenu(userName)


def calcMenu(userName):
	cursor = connection.cursor(buffered=True)
	print("What would you like to do? Type Options for list of available options.")
	choice = input()
	if choice == "Options":
		print("Update Metric Information - type MI")
		print("Calorie Summary - type CS")
		print("Calculate BMR - type BMR")
		choice = calcMenu(userName)
	elif choice == "MI":
		# Print user stats
		nameSQL = "SELECT * FROM user WHERE name = %s AND kg > 0 ORDER BY dateEntered DESC LIMIT 1"
		rowCount = cursor.execute(nameSQL, (userName,))
		if cursor.rowcount == 0:
			input("No metric information found. Have you added your metric information? Press any key to enter metric information.")
			cursor.close()
			metricUpdate(userName)
		cursor.execute(nameSQL, (userName,))
		colNames = [i[0] for i in cursor.description]
		userInfo = cursor.fetchall()
		print("Here are your stats: ")
		print('{:^10}'.format(colNames[1]), "\t", '{:^10}'.format(colNames[2]), "\t",
			  '{:^10}'.format(colNames[3]), "\t", '{:^10}'.format(colNames[4]), "\t",
			  '{:^10}'.format(colNames[5]), "\t")
		for row in userInfo:
			print('{:^10}'.format(row[1]), "\t", '{:^10}'.format(row[2]), "\t", '{:^10}'.format(row[3]), "\t",
				  '{:^10}'.format(row[4]), "\t", '{:^10}'.format(row[5]), "\t")
		userChoice = input("Would you like to add or update your metrics? Type any key to continue or Q to quit.")
		if userChoice == 'Q':
			cursor.close()
			mainMenu(userName)
		else:  # Update or add metrics
			cursor.close()
			metricUpdate(userName)
	elif choice == "CS":
		cursor.close()
		calorieSummary(userName)
		calcMenu(userName)
	elif choice == "BMR":
		cursor = connection.cursor(buffered=True)
		metricInfo = "SELECT * FROM user WHERE name = %s AND kg > 0 ORDER BY dateEntered DESC LIMIT 1"
		cursor.execute(metricInfo, (userName,))
		row = cursor.fetchall()
		if cursor.rowcount == 0:  # Check metrics available
			choice = input("No metric information found. Have you added your metric information? Enter any key to enter metric information, or Q for main menu.")
			cursor.close()
			if choice == "Q":
				mainMenu(userName)
			else:
				metricUpdate(userName)
		else:  # Get stats
			kg = int(row[0][2])
			height = int(row[0][3])
			gender = str(row[0][4])
			age = int(row[0][5])
			# Get total calories
			caloriesConsumed = calorieCalc(userName)
			# Calculate BMR
			bmr = float((66 + (13.7 * kg) + (5 * 180) - (6.8 * age)) * 1.3)
			# Exercise level
			print("Your age:", age)
			print("Your height:", height, "centimeters")
			print("Your weight:", kg, "kilograms.")
			print("Total calories consumed today:", round(caloriesConsumed, 2))
			print("The estimated amount of calories you expend in a day given the above stats is ", round(bmr,2))
			if caloriesConsumed < bmr:
				pounds = round((abs(int(bmr) - int(caloriesConsumed))) * 30 / 3500, 2)
				diffWeight = "lose"
			else:
				pounds = round((abs(int(caloriesConsumed) - int(bmr))) * 30 / 3500, 2)
				diffWeight = "gain"
			print("If you maintain a similar calorie intake as today, you will ", diffWeight, pounds, "pounds in a month.")
			mainMenu(userName)
	else:
		calcMenu(userName)


def metricUpdate(userName):
	cursor = connection.cursor(buffered=True)
	kg = input("Please enter your weight in kg: (Ex: 85) ")
	height = input("Please enter your height in centimeters: (Ex: 180) ")
	gender = input("Please enter your gender - (Ex: Female): ")
	age = input("Please enter your age in years: (Ex: 30) ")
	addEntrySQL = "INSERT INTO User (name, kg, height, gender, age, dateEntered) VALUES (%s, " \
				  "%s, %s, %s, %s, %s)"
	today = str(date.today())
	cursor.execute(addEntrySQL, (userName, kg, height, gender, age, today))
	connection.commit()
	print("Thanks for updating your stats!")
	cursor.close()
	mainMenu(userName)

def calorieSummary(userName):
	cursor = connection.cursor(buffered=True)
	# Get Journal for today
	# SQL UNION JOIN *****************************
	caloriesListSQL = "SELECT a.foodName, a.quantity, b.calories, b.protein, b.carb, b.fat, b.fiber FROM " \
					  "journaldb.journal a LEFT JOIN journaldb.foodList b ON a.foodName = b.foodName WHERE a.userName " \
					  "= %s AND DATE %s "
	today = str(date.today())
	cursor.execute(caloriesListSQL, (userName, today))
	foodList = cursor.fetchall()
	totalCal = 0
	for row in foodList:
		calSum = round(float(row[1]) * float(row[2]), 2)
		pTotal = round(float(row[1]) * float(row[3]), 2)
		cTotal = round(float(row[1]) * float(row[4]), 2)
		fTotal = round(float(row[1]) * float(row[5]), 2)
		fiberTotal = round(float(row[1]) * float(row[6]), 2)
		totalCal += calSum
		print(row[1], row[0], "amounts to", calSum, "Calories |", pTotal, "(g) Protein |", cTotal,
		  "(g) Carbohydrates |", fTotal, "(g) Fat |",
		  fiberTotal, "(g) Fiber total.", )
	print(round(totalCal, 2), "total calories consumed")
	cursor.close()
	return totalCal


def calorieCalc(userName):
	cursor = connection.cursor(buffered=True)
	# Get Journal for today
	# SQL UNION JOIN *****************************
	caloriesListSQL = "SELECT a.foodName, a.quantity, b.calories, b.protein, b.carb, b.fat, b.fiber FROM " \
					  "journaldb.journal a LEFT JOIN journaldb.foodList b ON a.foodName = b.foodName WHERE a.userName " \
					  "= %s AND DATE %s "
	today = str(date.today())
	cursor.execute(caloriesListSQL, (userName, today))
	foodList = cursor.fetchall()
	totalCal = 0
	for row in foodList:
		calSum = round(float(row[1]) * float(row[2]), 2)
		pTotal = round(float(row[1]) * float(row[3]), 2)
		cTotal = round(float(row[1]) * float(row[4]), 2)
		fTotal = round(float(row[1]) * float(row[5]), 2)
		fiberTotal = round(float(row[1]) * float(row[6]), 2)
		totalCal += calSum
	cursor.close()
	return totalCal


main()
