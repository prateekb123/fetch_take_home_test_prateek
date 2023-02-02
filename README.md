# Take Home Test for Fetch

This repository includes a Python script for the Fetch Take Home Test. The script requests the user's spent amount and then returns the output in the form of JSON, displaying the remaining points for each payer.

# Getting Started

By following these steps, you can setup a local copy of the project for use in testing and development.

# Prerequisites

To run this script, you must have Python installed on your computer. It is available for download from the official website https://www.python.org/downloads/.

# Installing

1. Clone the repository to your local machine by using the following command:

   Command - 
   git clone https://github.com/prateekb123/fetch_take_home_test_prateek.git
   
2. Navigate to the project directory by using the following command:

   Command - 
   cd fetch_take_home_test_prateek

# Usage

1. Run the script using the following command:

   python3 fetch_prateek_take_home_test.py <input spend amount>
   
   Eg. -> python3 fetch_prateek_take_home_test.py 5000
   
2. Enter the full file path for the CSV when prompted.

   Please provide the file path - <Input Path Here>
   
   Eg. Please provide the file path - /Users/prateekbansal/Downloads/transactions.csv
   
3. Remove the line 104 and 105 if coloums can be more than 3.

   
2. The script will return the output in the form of JSON, showing how many points are left with each payer.

# Output
   
If there are enough points - 
   
   {'DANNON': 1000, 'UNILEVER': 0, 'MILLER COORS': 5300}
      
If there are not enough points - 

   'Insufficient points'

  


