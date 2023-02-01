class Employee:
    def __init__(self, name, start_time, end_time):
        # Instantiate the Employee
        self.name = name
        self.start_time = start_time
        self.end_time = end_time

        # Set the hours worked
        self.hours_worked = self.end_time - self.start_time

        # If the employee works past midnight their hours worked will be negative, 
        # which can be added to 24 to get their actual hours worked.
        if (self.hours_worked < 0):
            self.hours_worked = 24 + self.hours_worked

        # Set break length to 0, if the employee works 4.5 or 6 hours assign them the relevant break.
        self.break_length = 0
        if (self.hours_worked >= 4.5):
            self.break_length = .25
        if (self.hours_worked >= 6):
            self.break_length = .5

# Example Roster
e0001 = Employee("1", 9, 17)
e0002 = Employee("2", 9, 15)
e0003 = Employee("3", 9, 17)
e0004 = Employee("4", 9, 17)
e0005 = Employee("5", 9, 17)
e0006 = Employee("6", 9, 17)
e0007 = Employee("7", 9, 17)
e0008 = Employee("8", 9, 18)
e0009 = Employee("9", 9, 17)

roster = [e0001, e0002, e0003, e0004, e0005, e0006, e0007, e0008, e0009]
roster.sort(key=lambda x: x.start_time) # Sort the Employees based on who started first
available_breaks = [10.00, 11.00, 12.00, 13.00, 14.00, 15.00, 16.00, 20.00, 21.00]
def calculateEmployeeBreaks(roster):
    breakList = []
    i = 0
    for employee in roster:
        if (employee.break_length > 0): # If the employee has a break
            if i >= len(available_breaks):
                i = 0 # Go back to the start of the list if it goes over the size
            if (available_breaks[i] < (employee.end_time - employee.break_length) and 
                (available_breaks[i] > employee.start_time)): # If the break will be during the employees shift
                breakList.append({'name' : employee.name, 'time' : str(available_breaks[i])}) # Add the Employees break to the Break List
            i += 1

    print(breakList)

calculateEmployeeBreaks(roster)