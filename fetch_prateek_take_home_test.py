# Fetch Take Home Test

import csv
import os.path
from datetime import datetime
import sys


def check_row_length(rowLength):
    """
    This function checks if each row length is equal to a specific length.
    :param rowLength:
    :return: Does not return anything but throws an error if the row length is different from the specified one.
    """

    if rowLength != 3:
        raise Exception('Row length is not right.')


def validate_row(row, payer_index, point_index, timestamp_index, row_number):
    """
    This function validates each row of the CSV. It throws an error if the value in any of the row
    is null or empty or if payer is not a string or point is not a digit or timestamp is not in the right format.
    :param row: Takes the entire row
    :param payer_index: Index of the payer name in each row
    :param point_index: Index of the point in each row
    :param timestamp_index: Index of the timestamp in each row
    :param row_number: current row number that is being checked
    :return: Does not return anything but throws error.
    """

    # Checking if the value of payer is a string or not. Also checking for null values.
    if not type(row[payer_index]) == str or row[payer_index] is None or len(row[payer_index]) == 0:
        raise Exception(f"The row number {row_number} does not have an string value for payer")

    # Striping the sign from the string to check if a value of point is a digit or not. Also checking for null values.
    if not row[point_index].lstrip('+-').isdigit() or row[point_index] is None or len(row[point_index]) == 0:
        raise Exception(f"The row number {row_number} does not have an integer value for point")

    # Checking Null value for Date and time column
    if row[timestamp_index] is None or len(row[timestamp_index]) == 0:
        raise Exception(f"The row number {row_number} does not have an date value for date and time.")

    # Checking if the value in the date and time column is of the right format.
    try:
        datetime.strptime(row[timestamp_index], '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        raise Exception(
            f"The row number {row_number} does not have an Date format of %Y-%m-%dT%H:%M:%S%z for date and time.")


def validate_header(payer_index, point_index, timestamp_index):
    """
    This function validates the header of the CSV. It throws an error if any index is still None after iterating over
    the header.
    :param payer_index: Index of the payer name in each row
    :param point_index: Index of the point in each row
    :param timestamp_index: Index of the timestamp name in each row
    :return: Does not return anything but throws error.
    """

    if payer_index == None:
        raise KeyError('Name "payer" does not exist in header.')

    if point_index == None:
        raise KeyError('Name "points" does not exist in header.')

    if timestamp_index == None:
        raise KeyError('Name "timestamp" does not exist in header.')


def read_and_sort_transactions_by_date(file_name):
    """
    This function returns a list of all entries in the CSV sorted by date and checks if the header and each of
    the rows are in the right format. It also converts the points into integer and date to python datetime.
    :param file_name: it is the path to the CSV that has to be read.
    :return: eg. [['DANNON', 300, datetime.datetime(2020, 10, 31, 10, 0, tzinfo=datetime.timezone.utc)], ['UNILEVER', 200,...
    """

    # Reading the CSV File
    try:
        with open(file_name) as csv_file:

            # Reading CSV using csv package.
            csv_reader = csv.reader(csv_file, delimiter=',')

            # Initializing line number counter
            line_number = 0

            # creating list of CSV content
            transaction_list = []

            # Calculating total points available to spend
            total_points = 0

            # Creating varibles to store the index of payer, point and  timestamp
            payer_index = None
            point_index = None
            timestamp_index = None

            # Iterating over each row in CSV
            for row in csv_reader:

                # Checking if the row length is correct
                # Remove line on 104th and 105th line if the row length could be changed
                row_length = len(row)
                check_row_length(row_length)

                # Checking if the line is 0 to check for header
                if line_number == 0:

                    # Iterating over each value of the header and storing the useful indexes in variables.
                    for title_index in range(len(row)):

                        if row[title_index].lower() == 'payer':
                            payer_index = title_index

                        if row[title_index].lower() == 'points':
                            point_index = title_index

                        if row[title_index].lower() == 'timestamp':
                            timestamp_index = title_index

                    # Calling the header validator to validate the header
                    validate_header(payer_index, point_index, timestamp_index)

                else:

                    # Calling the row validator to validate each row
                    validate_row(row, payer_index, point_index, timestamp_index, line_number)

                    # Converting the string value for timestamp to datetime and point to integer.
                    row[timestamp_index] = datetime.strptime(row[timestamp_index], '%Y-%m-%dT%H:%M:%S%z')
                    row[point_index] = int(row[point_index])

                    # Adding points from each row
                    total_points += row[point_index]

                    # Putting each row into a list
                    transaction_list.append(row)

                line_number += 1

            # Sorting the list in order of the date from oldest to latest using lamdba function
            transaction_list = sorted(transaction_list, key=lambda x: x[timestamp_index])

            return transaction_list, total_points, point_index, payer_index, timestamp_index

    except Exception:
        raise Exception('Error sorting the transaction list')


def remove_negative_points_from_list(sorted_by_date_transaction_list, payer_index, point_index):
    """
    This functions takes the list which is sorted by date and finds if the list has any value with
    negative points and remove those points from the same payer according to the oldest date rule.
    :param sorted_by_date_transaction_list: List of rows sorted by Date
    :param payer_index: Index of the payer name in each row
    :param point_index: Index of the point in each row
    :return: Returns a hashMap with removed negative points or throw an error if the payer who is taking
    out points does not have enough points to take out.
    Eg - {'DANNON': [['DANNON', 100, datetime.datetime(2020, 10, 31, 10, 0, tzinfo=datetime.timezone.utc)],
                    ['DANNON', 1000, datetime.datetime(2020, 11, 2, 14, 0, tzinfo=datetime.timezone.utc)]],
        'UNILEVER': [['UNILEVER', 200, datetime.datetime(2020, 10, 31, 11, 0, tzinfo=datetime.timezone.utc)]],
        'MILLER COORS': [['MILLER COORS', 10000, datetime.datetime(2020, 11, 1, 14, 0, tzinfo=datetime.timezone.utc)]]}
    """

    # Creating a Map to maintain name and corresponding rows
    namePointMap = dict()
    currPointMap = dict()
    transaction_with_no_points = []

    # Iterating over the list of rows that is sorted by date
    for row in sorted_by_date_transaction_list:

        if row[point_index] < 0 and currPointMap[row[payer_index]] < abs(row[point_index]):
            raise ValueError(f'Not Enough Points with user {row[payer_index]} to take points out.')

        # If the payer does not exist in the hashMap we check if the point value is negative if yes
        # we cannot remove the points from the payer as they don't have points yet to take out,
        # else to put the row into the hashMap mapping it to the payer.
        if row[payer_index] not in namePointMap:
            if row[point_index] < 0:
                raise ValueError(f'Not Enough Points with user {row[payer_index]} to take points out.')

            namePointMap[row[payer_index]] = [row]
            currPointMap[row[payer_index]] = row[point_index]

        else:

            # If the payer exist in the hashmap and the value of the points is negative we remove
            # the points from the payer according to the oldest date.
            if row[point_index] < 0:
                index = 0
                payerList = namePointMap[row[payer_index]]
                while index < len(payerList):
                # for row_in_list in namePointMap[row[payer_index]]:
                    if abs(row[point_index]) > payerList[index][point_index]:
                        row[point_index] += payerList[index][point_index]
                        payerList[index][point_index] = 0
                        transaction_with_no_points.append(payerList.pop(index))

                    elif abs(row[point_index]) < payerList[index][point_index]:
                        payerList[index][point_index] += row[point_index]
                        row[point_index] = 0
                        transaction_with_no_points.append(row)
                        index += 1
                        break

                    else:
                        row[point_index] = 0
                        payerList[index][point_index] = 0
                        transaction_with_no_points.append(row)
                        transaction_with_no_points.append(payerList.pop(index))
                        break




                # Raising an error if the points to be removed does not come to 0 after taking them out
                # from the payers account.
                # if row[point_index] != 0:
                #     raise ValueError(f'Not Enough Points with user {row[payer_index]} to take points out.')
            else:
                namePointMap[row[payer_index]].append(row)
                currPointMap[row[payer_index]] += row[point_index]

    return namePointMap, transaction_with_no_points


def calculate_spend_points(sorted_by_date_transaction_list, spent_amount, point_index):
    """
    Now,this function finally starts subtracting the amount each payer can contribute to the points user
    is trying to take out and finally give a list with the updated points of the payers.
    :param sorted_by_date_transaction_list: List of rows sorted by Date
    :param spent_amount: The amount user is trying to take out
    :param point_index: Index of the point in each row
    :return: A list after removing points from the oldest date to contribute to the points user is trying to take out.
    Eg. - [['DANNON', 0, datetime.datetime(2020, 10, 31, 10, 0, tzinfo=datetime.timezone.utc)],
           ['UNILEVER', 0, datetime.datetime(2020, 10, 31, 11, 0, tzinfo=datetime.timezone.utc)], .....]
    """

    curr_spend = spent_amount

    # Iterating over the list for each row
    for row in sorted_by_date_transaction_list:

        # If current spent comes to 0 return the list
        if curr_spend == 0:
            return sorted_by_date_transaction_list

        else:

            # if current points is more than the row points remove the points in the row until they are zero.
            amount = row[point_index]
            if amount <= curr_spend:
                curr_spend -= row[point_index]
                row[point_index] = 0

            else:
                row[point_index] -= curr_spend
                curr_spend = 0

    return sorted_by_date_transaction_list


def create_response(final_transaction_list, payer_index, point_index):
    """
    This function takes in the list which contains rows and then create a hashmap according to each payer.
    :param final_transaction_list: The list which contains each row.
    :param payer_index: Index of the payer name in each row
    :param point_index: Index of the point name in each row
    :return: Returns a Json response as output. Eg. - {'DANNON': 1000, 'UNILEVER': 0, 'MILLER COORS': 5300}
    """

    # Initializing the hashMap
    payerPointMap = dict()

    # Iterating over the list which contains each row
    for row in final_transaction_list:

        # If a payer does not exist in the map we create a new value for them in the hashmap
        # else we add the points they added on a later date.

        if row[payer_index] not in payerPointMap:
            payerPointMap[row[payer_index]] = row[point_index]
        else:
            payerPointMap[row[payer_index]] += row[point_index]

    return payerPointMap


def create_list_from_map(content_Map, timestamp_index, transaction_with_no_points):
    """
    This fucntion converts the hashmap we got after removing the negative points from the list
    and convert it again into a list.
    :param content_Map: Hashmap with removed negative points and updated points.
    :param timestamp_index: Index of the timestamp in each row
    :return: List of rows without negative point row.
    Eg. - [['DANNON', 100, datetime.datetime(2020, 10, 31, 10, 0, tzinfo=datetime.timezone.utc)],
    ['UNILEVER', 200, datetime.datetime(2020, 10, 31, 11, 0, tzinfo=datetime.timezone.utc)],......]
    """
    row_list = transaction_with_no_points

    # Iterating over the hashmap and putting the rows back in a list.
    for payer in content_Map:
        for row in content_Map[payer]:
            row_list.append(row)

    # Sorting the list according to date
    row_list = sorted(row_list, key=lambda x: x[timestamp_index])
    return row_list


def main(spent_amount):
    # Input file path
    file_name = input('Please provide the file path (Eg. /Users/prateekbansal/Downloads/transactions.csv)- ')
    if not os.path.exists(file_name):
        print('Enter a valid file path.')
        main(spent_amount)
        return

    sorted_by_date_transaction_list, total_points, point_index, payer_index, timestamp_index = read_and_sort_transactions_by_date(
        file_name)

    # Checking if there are enough points to spend or not.
    if total_points >= spent_amount:

        # Function to create a hashmap with adjusted negative points in the CSV.
        content_Map, transaction_with_no_points = remove_negative_points_from_list(sorted_by_date_transaction_list, payer_index, point_index)

        # This function call creates a list from the hashmap
        updated_transaction_list = create_list_from_map(content_Map, timestamp_index, transaction_with_no_points)

        # Function to remove the points spent by user.
        final_transaction_list = calculate_spend_points(updated_transaction_list, spent_amount, point_index)

        # Printing the final Json output
        print(create_response(final_transaction_list, payer_index, point_index))

    else:
        # Printing 'Insufficient points' if points are not enough.
        print('Insufficient points')


if __name__ == '__main__':
    # takes amount that has to be spent from the user
    # spent_amount = int(sys.argv[1])
    spent_amount = 5000

    main(spent_amount)
