#!/usr/bin/env python2

"""
JustDespair
 Get historical order information about orders on JustEat. And
regret. There is no API limit for your own sense of regret.

"""

__author__ = "nosmo@nosmo.me"

import argparse
import json
import collections
import datetime
from operator import itemgetter

import BeautifulSoup
import requests

LOGIN_URL = "https://www.just-eat.%s/member/login"
PREVORDERS_URL = "https://www.just-eat.%s/member/prevorders"


class LoginException(Exception):
    pass


class JustEat(object):

    @staticmethod
    def generateYearPlaceholder(year):
        # Generate a placeholder that JustEat expects for the orders page:
        # 2008 is when the placeholder grouping starts so it is place 00.
        # for example 2010 will be 04
        placeholder_t = "ctl00$ContentPlaceHolder1$ctl00$ctl{0:02d}"
        yearfactor = year - 2008
        return placeholder_t.format(yearfactor * 2)

    def __init__(self, username, password, region="ie"):
        self.__username = username
        self.__password = password
        self._session = requests.Session()
        self.region = region
        self.login()

    def login(self):
        # Get our session cookies
        login_attempt = self._session.post(LOGIN_URL % self.region,
                                           data={"EmailAddress": self.__username,
                                                 "Password": self.__password,
                                                 "ReturnUrl": "%2F",
                                                 "PersistentLoginEnabled": "True",
                                                 "RememberMe": "false"})
        if not login_attempt.ok:
            raise LoginException
        return True

    def parseOrderPage(self, page_content):
        # Do some heinous shit with the terrible HTML JustEat return
        # to get what we need.

        content_reader = BeautifulSoup.BeautifulSoup(page_content)
        purchases = []

        # this is some vile html: no ids, very little class except for
        # incorrect ones
        purchase_data = content_reader.findAll("table", {"class": "signUp"})
        if len(purchase_data) > 1:
            raise Exception(("JustEat's HTML looks worse than usual - "
                             "something is broken :("))
        purchase_data = purchase_data[0]

        # TODO use per-order checks with this URL - will be able to get
        # more interesting details like average time of day (almost
        # certianly time of morning) of orders
        # https://www.just-eat.ie/pages/ViewOrder.aspx?ordertable=order&userid=UID&orderid=ORDERID&ratingcode=somestuffidunno
        for purchase in purchase_data.findAll("tr"):
            left_td_find = purchase.findAll("td", {"align": "left"})
            if not left_td_find or len(left_td_find) != 2:
                # This line isn't a purchase, skip it
                continue

            # TODO make a datetime
            purchase_date, purchase_location = [ i.string for i in left_td_find ]
            purchase_amount = purchase.findAll("div", {"style": "float: right;"})
            if purchase_amount:
                purchase_amount = float(purchase_amount[0].string)
            purchase_id = purchase.findAll("a", {"style": "cursor:pointer;"})
            if purchase_id:
                purchase_id = purchase_id[0].string
            purchase_dict = {
                "date": purchase_date,
                "location": purchase_location,
                "amount": purchase_amount,
                "id": purchase_id
            }
            purchases.append(purchase_dict)

        return purchases

    def getOrderData(self, startyear=2008, endyear=datetime.datetime.now().year):
        # Request the order history from startyear until endyear and
        # create a per-year dict.
        order_dict = collections.defaultdict(dict)
        for year in range(2008, endyear+1):
            page_content = self.getOrderPage(year)
            order_dict[year]["orders"] = self.parseOrderPage(page_content)
            order_dict[year]["total_cost"] = sum([i["amount"] for i in order_dict[year]["orders"]])
            if order_dict[year]["orders"]:
                order_dict[year]["most_purchased"] = collections.Counter(
                    [i["location"] for i in order_dict[year]["orders"]]
                ).most_common(1)[0][0]
            else:
                order_dict[year]["most_purchased"] = None

        return dict(order_dict)

    def getOrderPage(self, year):
        # Get the HTML content of an order page for a given year
        year_placeholder = self.generateYearPlaceholder(year)
        order_attempt = self._session.post(PREVORDERS_URL % self.region,
                                           data={"__EVENTTARGET": year_placeholder})
        if not order_attempt.ok:
            raise Exception("Couldn't get order page: %s" % order_attempt.content)
        return order_attempt.content

def print_totals(order_dict):
    for k, v in sorted(order_dict['totals'].items(), key=itemgetter(1), reverse=True):
        print("%s: %0.2f" % (k, v))
    print("\n")

def main():
    parser = argparse.ArgumentParser(description='Find out how much more ashamed you should feel about ordering food online')
    parser.add_argument('email', metavar='email', type=str,
                        help="Your JustEat account's email address")
    parser.add_argument("password", metavar="password", type=str,
                        help="Your JustEat account's password")
    parser.add_argument("--json", "-j", dest="json", action="store_true",
                        help="Dump only order output as JSON")
    parser.add_argument("--region", "-R", dest="region", action="store", default="ie",
                        help="Region from which to fetch order information (untested)")
    parser.add_argument("--totals", "-t", dest="totals", action="store_true",
                        help="Show totals for each location")
    args = parser.parse_args()

    just_eat = JustEat(args.email, args.password, args.region)

    order_data = just_eat.getOrderData()

    if args.totals:
        order_totals = {'totals':{}}
        for year in order_data:
            order_data[year]['totals'] = {}
            for order in order_data[year]['orders']:
                order_data[year]['totals'][order['location']] = order_data[year]['totals'].get(order['location'], 0) + order['amount']
                order_totals['totals'][order['location']] = order_totals['totals'].get(order['location'], 0) + order['amount']

        for year in order_data:
            print year
            print_totals(order_data[year])
        print("Totals: ")
        print_totals(order_totals)

    total_cost = []
    if args.json:
        print(json.dumps(order_data))
    else:
        for year, year_details in order_data.iteritems():
            print("""%d
            \tMost frequented: %s
            \tTotal cost: %0.2f""" % (year,
                                      year_details["most_purchased"],
                                      year_details["total_cost"] if year_details["total_cost"]
                                      else 0.0))
            total_cost.append(year_details["total_cost"])

        print("\nTotal cost: %0.2f" % sum(total_cost))

if __name__ == "__main__":
    main()
