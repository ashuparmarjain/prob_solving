import sys
import json
from datetime import datetime
from functools import reduce


DATE_FORMAT = '%Y-%m-%d'


def get_user_inputs():
    """
        Function to get user inputs
    """
    print('Enter the path to the loan applications file, path to the output file, N (the starting capital), K (the max number of concurrently active loans)')
    print('For example: applications.json approved.txt 50000 1000')
    user_input = raw_input()
    return user_input.split()


def get_applications(_file):
    """
        Function to read json file and load the data
    """
    open_loan_applications_file = open(_file,)
    return json.load(open_loan_applications_file)


def defaulter(arr):
    """
        Function to mark user as defaulters, defaulters are the one who fails to pay the principle amount and the fee
    """
    return list(set(map(lambda application: application['customer_id'], filter(lambda application: application['repaid_amount'] < (application['principal'] + application['fee']), arr))))


def remove_high_risk_application(arr, defaulters_list):
    """
        Function to remove high risk profiles, basically user who have marked as defaulters and who takes more than 90 days to repay the loan amount
    """
    return list(filter(lambda application: application['customer_id'] not in defaulters_list and
                       ((datetime.strptime(application['repayments'][-1]['date'], DATE_FORMAT) - datetime.strptime(application['disbursement_date'], DATE_FORMAT)).days < 91), arr))


def has_active_loan(user_application, approved_loans):
    """
        Function to check if user has any active loan     
    """
    return len(filter(lambda item: item['customer_id'] == user_application['customer_id'] and len(intersected_applications(user_application, approved_loans)), approved_loans))


def slot_avaialble(application, approved_loans, K):
    """
        Function to check if slot is available, basically if there is any room to handle this applications.
    """
    return len(intersected_applications(application, approved_loans)) < K



def intersected_applications(application, applications):
    """
        Function to get all intersected applications
    """
    return filter(lambda item: datetime.strptime(item['disbursement_date'], DATE_FORMAT) <= datetime.strptime(application['repayments'][-1]['date'], DATE_FORMAT) and datetime.strptime(application['disbursement_date'], DATE_FORMAT) <= datetime.strptime(item['repayments'][-1]['date'], DATE_FORMAT), applications)


def approval_loan_algorithm(applications, N, K):
    """
        Function to approve loans and return the list of apllications approved.
    """
    approved_loan = []
    loan_disbursement = []
    loan_repayment = []
    while len(applications):
        print(len(applications), 'left!')
        print('*'*50) 
        application = applications[0]
        intersected = list(intersected_applications(application, applications))
        intersected.sort(key=lambda application: (
            (application['repaid_amount'] - application['principal']) / application['principal']) * 100, reverse=True)
        applications = filter(lambda item: item['application_id'] not in list(
            map(lambda item: item['application_id'], intersected)), applications)
        for i_application in intersected:
            total_disburse = reduce(lambda a, b: (a[1]+b[1], a[1]+b[1]), filter(lambda item: datetime.strptime(
                i_application['repayments'][-1]['date'], DATE_FORMAT) >= datetime.strptime(item[0], DATE_FORMAT), loan_disbursement), (0, 0))
            total_repayments = reduce(lambda a, b: (a[1]+b[1], a[1]+b[1]), filter(lambda item: datetime.strptime(
                i_application['disbursement_date'], DATE_FORMAT) >= datetime.strptime(item[0], DATE_FORMAT), loan_repayment), (0, 0))
            if (N + total_repayments[0] - total_disburse[0]) > i_application['principal'] and not has_active_loan(i_application, approved_loan) and slot_avaialble(i_application, approved_loan, K):
                loan_disbursement.append(
                    (i_application['disbursement_date'], i_application['principal']))
                for repayments in i_application['repayments']:
                    loan_repayment.append(
                        (repayments['date'], repayments['amount']))
                approved_loan.append(i_application)
    return approved_loan


def write_output(arr, filename):
    """
        Function to write list item in the filename.
    """
    print('Started writing the output..')
    f = open(filename, 'w')
    for a in arr:
        f.write(str(a) + '\n')
    f.close()
    print('Done!, Open the file to see the approved loans.')


def main():
    user_input = get_user_inputs()
    loan_applications_file = user_input[0]
    loan_approved_file = user_input[1]
    N = int(user_input[2])
    K = int(user_input[3])
    applications = get_applications(loan_applications_file)
    print('Collecting all applications!')
    print('*'*50)
    defaulter_users = defaulter(applications)
    print('Marking defaulters')
    print('*'*50)
    applications = remove_high_risk_application(applications, defaulter_users)
    print('Removing high risk applications from the approval criteria')
    print('*'*50)
    applications.sort(key=lambda application: datetime.strptime(
        application['disbursement_date'], DATE_FORMAT))
    print('Running algorithm to approve or disapprove the loan')
    print('*'*50)    
    approved_loans = approval_loan_algorithm(applications, N, K)
    approved_loans_list = map(
        lambda item: item['application_id'], approved_loans)
    write_output(approved_loans_list, loan_approved_file)


main()
