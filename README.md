justDespair
=======

justDespair is an innovation in guilt-generation
technologies. justDespair will collect all historical order
information from just-eat.ie (and hopefully other regions using the
just-eat platform), total the amount spent over the years and make you
feel very bad about your life choices.

JustDespair's functionality is now available online with a score tracking component [here](https://justdespair.com/).

What it tells you
-------

* How much you spent per year
* Which restaurant you frequented the most per year
* A total of all previous purchases on just-eat, ever.

How to use
-------

```python justDespair.py my@email.addesss myjusteatpassword```

Passing the ```--json``` command line argument will output a dictionary of the yearly order information as JSON only. No maximums are calculated.

The ```--region``` flag is an untested feature for using justDespair against JustEat sites outside of the default of Ireland.

Library
-------

justDespair can be used as a simple library as follows:

```
import justDespair
just_eat = justDespair.JustEat("glutton@example.com", "some_password")
order_data = just_eat.getOrderData()
order_data.keys()
[2008, 2009, 2010, 2011, 2012, 2013, 2014]
```

Requirements
-------
justDespair requires [requests](http://docs.python-requests.org/en/latest/) and [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/).

TODO
-------
The per-order pages linked from the pages that justDespair currently reads contain even more information about the orders. The number one most embarassing details that I'd like to extract is average time order was placed at (I am thinking late), latest time and earliest time relative to 9AM.

I have no idea how much uniformity there is across different JustEat platforms so I am very interested to see how the --region flag works against sites other than the Irish version.
