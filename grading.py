import re
import os
import numpy as np
import pandas as pd
import random
from datetime import date, datetime, timedelta

def importCSV(file=None):
    if file is None:
        file = input('What file would you like to use?')
    else:
        pass

    df = pd.read_csv(file)
    return df

def addFiles(path=None, rename=False):
    if path is None:
        path = input('Where are the extra files located? ')
    else: 
        pass

    fileDict = {}

    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        netID = re.search(r'\w\w\d\d\d\d\d\d', filename).group(0)
        if rename:
            # ext = re.search(r'\..*$', filename).group(0)
            newName = os.path.join(path, netID + "_" + filename)
            # print(newName)
            os.rename(f, newName)
            fileDict[netID] = newName
        else:
            fileDict[netID] = f
    
    return fileDict

def findLate(username, path, dueDate, isResub=False):
    # Default to maximum points if not late/resubmission
    points = 3

    # Search all metadata files for match
    for file in os.listdir(path):
        user = re.search(r'\w\w\d\d\d\d\d\d', file).group(0)

        # When match is found, find submission date and determine points to assign
        if user == username:
            filePath = path + '/' + file
            with open(filePath) as f:
                contents = f.readlines()
            subDate = re.search(r'(Date Submitted: )(.*$)', contents[2]).group(2)
            subDate = datetime.strptime(subDate, '%A, %B %d, %Y %I:%M:%S %p %Z')
            if subDate > dueDate:
                print(f'Assignment is late, Submitted {subDate}, due {dueDate}')
                if isResub:
                    points = input('Points to recieve: ') or 3
                else:
                    points = input('Points to recieve: ')

    return points

def main():
    # Take input about assignment
    assignment = input("Assignment: ")
    dueDate = input('Due Date YYYY-MM-DD: ')
    colName = input('Column Name: ')
    extraCredit = input('Extra Credit [y/N] ') or False

    # Set up paths and variables
    dueDate = datetime.strptime(dueDate + '-23-59', '%Y-%m-%d-%H-%M')
    txtPath = 'gradeFiles/' + assignment + '/file_submissions/txt/'
    file = f'gradeFiles/{assignment}/{assignment}.csv'
    resubDeadline = date.today() + timedelta(days=7)
    
    # Create dataframe and dictionaries
    gradeDF = importCSV(file)
    gradeDict = {}
    feedDict = {}
    formatDict = {}

    # Handle extra credit
    if extraCredit == 'y':
        extraPoints = input('How many points available: [1]') or 1
        extraCredit = True

    for index, row in gradeDF.sort_values(by=['Username']).iterrows():
        print(f"Currently grading {row['First Name']} {row['Last Name']} - {row['Username']}")
        
        # Check if there is actually a submission, skip if not
        if pd.isnull(row[colName]):
            print('No submission')
        elif re.search(r'^Needs Grading', row[colName]):
            # Check if it is a resubmission (whether there is already feedback)
            # Then determine points
            if pd.isnull(row['Feedback to Learner']):
                points = findLate(row['Username'], txtPath, dueDate)
                isResub = False
            else:
                print(row['Feedback to Learner'])
                isResub = True
                points = findLate(row['Username'], txtPath, dueDate, isResub)
            
            # Pass/Fail, if pass give positive feedback otherwise prompt for feedback
            passing = input('Pass? [Y/n] ') or True
            if passing is True:
                if extraCredit:
                    getExtra = input('Extra credit? [Y/n] ') or True
                    if getExtra is True:
                        points = int(points) + extraPoints
                gradeDict[row['Username']] = points
                affirmation = affirmations[random.randint(0, len(affirmations) - 1)]
                feedDict[row['Username']] = f"<p>{affirmation}</p>"
            else:
                gradeDict[row['Username']] = 0
                feedback = input('Feedback: ')
                if isResub:
                    feedDict[row['Username']] = f"""<p>{feedback}</p>"""
                else:
                    feedDict[row['Username']] = f"""<p>{feedback}</p>
<p><br></p> 
<p>If you resubmit by {resubDeadline}, you can still receive {points} points.</p>"""
            
            formatDict[row['Username']] = 'HTML'
        else:
            print('No new submission')
            gradeDict[row['Username']] = row[colName]
            feedDict[row['Username']] = row['Feedback to Learner']
            formatDict[row['Username']] = 'HTML'


    # Add all changes to datagrame, then export to csv
    gradeDF[colName] = gradeDF['Username'].map(gradeDict)
    gradeDF['Feedback to Learner'] = gradeDF['Username'].map(feedDict)
    gradeDF['Notes Format'] = gradeDF['Username'].map(formatDict)
    gradeDF['Feedback Format'] = gradeDF['Username'].map(formatDict)

    fileName = assignment + '.csv'
    pd.DataFrame.to_csv(gradeDF, fileName)

affirmations = [
    'Great Job!',
    'Awesome :)',
    'Perfect!',
    'Amazing!',
    'Keep up the good work!',
    'Well done!'
]

if __name__ == '__main__':
    start = datetime.now()
    main()
    print('Total elapsed time:', datetime.now() - start)