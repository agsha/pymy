import inspect
import json
import logging
import os
import sys
import subprocess
import urllib2
import socket
from multiprocessing import Process, Queue

# import requests
# setup logging to console with line number
import math
import locale

import time

locale.setlocale(locale.LC_MONETARY, 'hi_IN.ISCII-DEV')
console = logging.StreamHandler(sys.stdout)
console.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger('').addHandler(console)
logging.getLogger('').setLevel(logging.DEBUG)
log = logging.getLogger(__name__)

this_host = socket.gethostname()
try:
    this_ip = socket.gethostbyname(this_host)
except:
    pass
this_file = os.path.abspath(__file__)
this_file_name = os.path.basename(__file__)
this_dir = os.path.dirname(os.path.abspath(__file__))

__author__ = 'sharath.g'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    PRETTY = '\033[1;36m'
    FAIL = '\033[91m'
    TAME = '\033[0;36m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def l(*args):
    log.debug(*args)


def sf(string, *args, **kwargs):
    return string.format(*args, **kwargs)

def fc(n):
    return locale.currency(n, grouping=True)

def prettify(cmd, line=-1, plain_text=False):
    if not plain_text:
        return "{tame_color}[{host} {cwd}:{line}]$ {bold_color}{cmd}{end_color}".format(tame_color=bcolors.TAME,
                                                                                        bold_color=bcolors.PRETTY,
                                                                                        host=socket.gethostname(),
                                                                                        cwd=os.getcwd(),
                                                                                        line=line,
                                                                                        cmd=cmd, end_color=bcolors.ENDC)
    return "[{host} {cwd}:{line}]$ {cmd}".format(
        host=socket.gethostname(),
        cwd=os.getcwd(),
        line=line,
        cmd=cmd)


def lineno1():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def lineno2():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_back.f_lineno


def lineno3():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_back.f_back.f_lineno


this_os = 'Darwin'
try:
    if 'Linux' in co("uname"):
        this_os = 'Linux'
except:
    pass


def split(s, delim="\n"):
    return filter(None, [x.strip() for x in s.strip().split(delim)])

################ ALL THE GOOD CODE FROM HERE ######################


emi_period = 10*12
emi_amount = 3000000.0
emi_rate = 8.7 / 1200

house_period = 30*12
rent = 30000.0
rent_rate = 4.0 / 1200

house_rate = 14.5 / 1200

sip_interest = 10.0 / 1200

upfront = 5000000.0
registration = 800000.0

def house():

    # case 1 house is bought:

    # equivalent to emi per month times months
    emi_per_month = calc_emi(emi_amount, emi_rate, emi_period)
    initial = -emi_per_month * emi_period
    # less registration also
    initial -= registration
    # less upfront
    initial -= upfront

    #I've sold the house, add that value emi_amount+upfront is the amount on which appreciation has occured
    initial += compound(emi_amount+upfront, house_rate*12, house_period/12)


    # I've taken the rent each month and invested it in sip.
    # the calculation is complicated.
    cur_rent = rent
    for month in range(house_period):
        initial += compound(cur_rent, sip_interest * 12, (house_period - month) / 12)
        if month % 12 == 0:
            cur_rent *= (1 + rent_rate * 12)
    x = initial

    # tax is calculated yearly: 30% of min (2L, interest paid)
    interest_this_year = 0
    current_principal = emi_amount
    for month in range(emi_period):
        interest_this_month = current_principal*emi_rate
        current_principal -= (emi_per_month - interest_this_month)
        interest_this_year += interest_this_month
        if month % 12 == 0:
            assert interest_this_year > 0
            tax_savings = min(200000.0, interest_this_year)*0.33
            # invested in sip
            initial += compound(tax_savings, sip_interest*12, (house_period - month) / 12)
            interest_this_year = 0

    # this is the amount i will have after house_period months
    return initial


def invest():
    # case 2: I have invested in sip
    initial = compound(upfront + registration, sip_interest * 12, house_period / 12)
    emi_per_month = calc_emi(emi_amount, emi_rate, emi_period)

    # the emi i have invested in sip
    for month in range(emi_period):
        initial += compound(emi_per_month, sip_interest * 12, (house_period - month) / 12)

    return initial

def compound(p, r, t):
    return p * ((1 + r) ** t)


def calc_emi(p, r, t):
    x = (1.0 + r) ** t
    return p * r * x / (x - 1)

def calc_R(p1, p2, t):
    lo = 0.0
    hi = 20.0
    while hi - lo > 0.01:
        mid = (lo+hi)/2
        try:
            pex = compound(p1, mid, t)
            if pex > p2:
                hi = mid
            else:
                lo = mid
        except:
            hi = mid
    return lo


def calc():
    R = [9.0]
    # one to 12 years
    T = [12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228, 240, 252, 264, 276, 288,
         300, 312, 324, 336, 348, 360]
    print "rate,time,emi"
    for r in R:
        rr = r / 1200
        for t in T:
            x = (1.0 + rr) ** t
            e = rr * x / (x - 1)
            print sf("{}   , {}   ,   {}", r, t, str(round(e * 5000000, 10)))



def sumanth():
    lakh = 100*1000
    loan = 25*lakh
    sip_rate = 9.0 / 12 /100
    wealth = 0
    tax_exempt = 0

    principal_per_year = 0

    for month in range(1, 5*12+1):
        new_loan = int(compound(loan, 8.95/12/100, 1))
        loan_interest = new_loan - loan
        loan = new_loan
        towards_loan = min(loan, 50000)
        loan -= towards_loan
        towards_sip = 90000 - towards_loan
        wealth += compound(towards_sip, sip_rate, 60-month)
        principal_per_year += max(0, towards_loan - loan_interest)
        if month % 12 == 0:
            tax_exempt += min(principal_per_year, 150000)*0.3
            principal_per_year = 0
        print sf("month:{} loan:{} wealth:{} principal:{} towards_sip:{} tax_exempt:{} loan_interest:{}", month, loan, int(wealth), 50000 - loan_interest, towards_sip, tax_exempt, loan_interest)


def sumanth_2():
    lakh = 100*1000
    loan = 25*lakh
    sip_rate = 3.0 / 12 /100
    wealth = 0
    tax_exempt = 0

    principal_per_year = 0

    for month in range(1, 5*12+1):
        new_loan = int(compound(loan, 8.95/12/100, 1))
        loan_interest = new_loan - loan
        loan = new_loan
        towards_loan = min(loan, 90000)
        loan -= towards_loan
        towards_sip = 90000 - towards_loan
        wealth += compound(towards_sip, sip_rate, 60-month)
        principal_per_year += max(0, towards_loan - loan_interest)
        if month % 12 == 0:
            tax_exempt += min(principal_per_year, 150000)*0.3
            principal_per_year = 0
        print sf("month:{} loan:{} wealth:{} principal:{} towards_sip:{} tax_exempt:{} loan_interest:{}", month, loan, int(wealth), 50000 - loan_interest, towards_sip, tax_exempt, loan_interest)





def test():
    print compound(2500000, 8.95/100/12, 1)


def docompare():
    global house_period
    for house_period in range(1, 30):
        house_period *= 12
        print sf("years:{}, house_rate:{}, house_investment:{}, invest:{}", house_period/12, fc(compound(emi_amount+upfront, house_rate*12, house_period/12)), fc(house()), fc(invest()))

def perf():
    count = 0
    start = time.time()
    for i in range(100000000):
        count += i
        count %= 100
    print time.time() - start
    print count


def main(params):
    # print calc_R(1, 2, 5) * 100
    #docompare()
    # sumanth_2()
    # test()
    # print house()
    # calc()
    # print [12* i for i in range(30)]
    # raise Exception("Unimplemented!")
    perf()


if __name__ == '__main__':
    method = 'main'
    num_args = len(sys.argv)
    if num_args == 1 or sys.argv[1] not in globals():
        main(sys.argv[1:])
    elif num_args == 2:
        globals()[sys.argv[1]]()
    else:
        globals()[sys.argv[1]](sys.argv[2:])
