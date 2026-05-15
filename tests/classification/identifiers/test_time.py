from risk_assessment.classification.identifiers import DateTime, DayOfTheWeek


def test_day_of_the_week():
    identifier = DayOfTheWeek()

    assert identifier.is_of_this_type("Monday")
    assert identifier.is_of_this_type("Mon")
    assert identifier.is_of_this_type("Tuesday")
    assert identifier.is_of_this_type("Tue")
    assert identifier.is_of_this_type("Wednesday")
    assert identifier.is_of_this_type("Wed")
    assert identifier.is_of_this_type("Thursday")
    assert identifier.is_of_this_type("Thu")
    assert identifier.is_of_this_type("Friday")
    assert identifier.is_of_this_type("Fri")
    assert identifier.is_of_this_type("Saturday")
    assert identifier.is_of_this_type("Sat")
    assert identifier.is_of_this_type("Sunday")
    assert identifier.is_of_this_type("Sun")

    assert identifier.is_of_this_type("monday")
    assert identifier.is_of_this_type("mon")
    assert identifier.is_of_this_type("tuesday")
    assert identifier.is_of_this_type("tue")
    assert identifier.is_of_this_type("wednesday")
    assert identifier.is_of_this_type("wed")
    assert identifier.is_of_this_type("thursday")
    assert identifier.is_of_this_type("thu")
    assert identifier.is_of_this_type("friday")
    assert identifier.is_of_this_type("fri")
    assert identifier.is_of_this_type("saturday")
    assert identifier.is_of_this_type("sat")
    assert identifier.is_of_this_type("sunday")
    assert identifier.is_of_this_type("sun")

    assert identifier.is_of_this_type("MONDAY")
    assert identifier.is_of_this_type("MON")
    assert identifier.is_of_this_type("TUESDAY")
    assert identifier.is_of_this_type("TUE")
    assert identifier.is_of_this_type("WEDNESDAY")
    assert identifier.is_of_this_type("WED")
    assert identifier.is_of_this_type("THURSDAY")
    assert identifier.is_of_this_type("THU")
    assert identifier.is_of_this_type("FRIDAY")
    assert identifier.is_of_this_type("FRI")
    assert identifier.is_of_this_type("SATURDAY")
    assert identifier.is_of_this_type("SAT")
    assert identifier.is_of_this_type("SUNDAY")
    assert identifier.is_of_this_type("SUN")


def test_datetime():
    dates = [
        "October 17 2018",
        "October 17, 2018",
        "October the 17th 2018",
        "October the 17th, 2018",
        "Jun 10, 2017",
        "1 May 25",
        "28 Jun 2010",
        "Jul 5, 13",
    ]

    identifier = DateTime()

    for date in dates:
        assert identifier.is_of_this_type(date), date


def test_invalid_patterns():
    identifier = DateTime()

    invalid_patterns = [
        "8684     04-08-1951",
        "foobar",
        "01-01-1981 27:05:22",
        "Tue, 32 Apr 2017 10:35:17 GMT",
        "",
    ]

    for date in invalid_patterns:
        assert not identifier.is_of_this_type(date), date


def test_is_of_this_type_for_valid_patterns():
    identifier = DateTime()

    valid_datetimes = [
        "17 Jan 2019 15:35:00",
        "17 Jan 2019 15:35:00 -0000",
        "January 30, 2012 2:19 PM",
        "08-12-1981 00:00:11",
        "08/12/1981 00:00:11",
        "08-12-1981",
        "1981-12-08",
        "Jan 01, 1920",
        "Jan 1, 1920",
        "Jan 1,1920",
        "January 1, 1920",
        "January 1,1920",
        "January 1 1920",
        "Jan 1 1920",
        "Tue, 25 Apr 2017 10:35:17 UTC",
        "Tue, 25 Apr 2017 10:35:17 GMT",
        "22-JULY-2008",
        "22-JUL-2008",
        "22-jul-2008",
        "January 23, 2006",
        "January 23rd, 2006",
        "Jan 23, 2006",
        "01/23/2006",
        "1/23/2006",
        "01-23-2006",
        "01.23.2006",
        "200601232216",
        "Wed Oct 04 16:26:52 2006",
        "Wed Sep 19, 2007 11:36 AM",
        "6/4/2006 12:01 PM",
        "11/9/2007 11:12:04 AM",
        "Thu Dec 4, 2008 9:18 AM",
        "11/01/2004 11:35:30",
        "Mon Apr 14 23:51:59 2003",
        "Thu Apr 3 23:51:59 2003",
        "jun 6, 2007 12:50 pm",
        "May 6, 2007 3:50 PM",
        "May 6, 2007 3:50 PM",
        "May 16, 2007 3:50 PM",
        "6/11/2004 at 4:00 PM",
        "jun 6, 2007 3:50 PM",
        "JUN 6, 2007 3:50 PM",
        "May 6, 2007 3:50 PM",
        "May 6, 2007 12:50 PM",
        "Wed Aug 29, 2007 1:55 PM",
        "Wed Aug 2, 2006 3:13 PM",
        "1/20/2004 at 9:51 AM",
        "4/21/08",
        "4/14/98",
        "4/9/2007 9:34 am",
        "4/9/2007",
        "9:34 am",
        # "4/9/2007   9:34 am",  # this is ridiculous
        "10/29/2009 1:53 PM",
        "12/28/2007 06:42:23",
        "Wed Apr 29, 2009",
        "3:00 PM",
        # "Wed Apr 29, 2009  3:00 PM",  # this is ridiculous
        "August of 2008",
        "February 2004",
        "3/22/01 at 2:30PM",
        "November 13 at 8am",
        "1/5/2013",
        "12/12/1948",
        "12-12-07",
        "4/9/2004 at 7:40 AM",
        "7 August '12",
        "'12-August",
        "January 2016",
        "22 January 2016",
        "31 Dec 2016",
        "02/26/2001,6:24 AM",
        "March of 1995",
        "January 3",
        "January 3rd of this year",
        "6-12-06",
        "2016-02-18T20:15:37.421Z",
        "2014-10-07T14:45:00Z",
        "2016-08-18 09:52:39.694821",
        "2016-08-18 09:52:39.694",
        "2013-01-29 23:00:00",
        "2009-09-25 23:00:00.0",
        "2016-02-21 23:00:00.0",
    ]

    for date in valid_datetimes:
        assert identifier.is_of_this_type(date), date


def test_specific_values():
    identifier = DateTime()

    assert identifier.is_of_this_type("2017-11-16T00:01:08.570+11:00")
    assert identifier.is_of_this_type("January 30, 2012 2:19 PM")
    assert identifier.is_of_this_type("16 April 2018 02:28:46 UTC")
    assert identifier.is_of_this_type("Monday 16 April 2018 02:28:46 UTC")


def test_pattern():
    from datetime import datetime

    assert datetime.strptime("2020/10/26 7:56:35 AM GMT", "%Y/%m/%d %I:%M:%S %p %Z")
    try:
        datetime.strptime("2020/10/26 7:56:35 AM GMT+9", "%Y/%m/%d %I:%M:%S %p %Z")
        assert False
    except ValueError:
        assert True


def test_dates_in_japanese():
    identifier = DateTime()

    assert identifier.is_of_this_type("2020/10/26 7:56:35 午後 GMT+9")
    assert identifier.is_of_this_type("2019年1月13")
    assert identifier.is_of_this_type("1929年7月28日")
    assert identifier.is_of_this_type("1994年5月19日")
    assert identifier.is_of_this_type("1961年1月20日")
    # new round
    assert identifier.is_of_this_type("10年"), "10年 == 2010"
    assert identifier.is_of_this_type("09年7月12日"), "09年7月12日 == July 12, 2009"
    assert identifier.is_of_this_type("09年3・1"), "09年3・1 == March 1, 2009"
    assert identifier.is_of_this_type("11年1"), "11年1 == January 2011"


def test_is_of_this_type_for_valid_patterns_fast():
    identifier = DateTime(fast=True)

    valid_datetimes = [
        "17 Jan 2019 15:35:00",
        "17 Jan 2019 15:35:00 -0000",
        "January 30, 2012 2:19 PM",
        "08-12-1981 00:00:11",
        "08/12/1981 00:00:11",
        "08-12-1981",
        "1981-12-08",
        "Jan 01, 1920",
        "Jan 1, 1920",
        "Jan 1,1920",
        "January 1, 1920",
        "January 1,1920",
        "January 1 1920",
        "Jan 1 1920",
        "Tue, 25 Apr 2017 10:35:17 UTC",
        "Tue, 25 Apr 2017 10:35:17 GMT",
        "22-JULY-2008",
        "22-JUL-2008",
        "22-jul-2008",
        "January 23, 2006",
        "January 23rd, 2006",
        "Jan 23, 2006",
        "01/23/2006",
        "1/23/2006",
        "01-23-2006",
        "01.23.2006",
        "200601232216",
        "Wed Oct 04 16:26:52 2006",
        "Wed Sep 19, 2007 11:36 AM",
        "6/4/2006 12:01 PM",
        "11/9/2007 11:12:04 AM",
        "Thu Dec 4, 2008 9:18 AM",
        "11/01/2004 11:35:30",
        "Mon Apr 14 23:51:59 2003",
        "Thu Apr 3 23:51:59 2003",
        "jun 6, 2007 12:50 pm",
        "May 6, 2007 3:50 PM",
        "May 6, 2007 3:50 PM",
        "May 16, 2007 3:50 PM",
        "6/11/2004 at 4:00 PM",
        "jun 6, 2007 3:50 PM",
        "JUN 6, 2007 3:50 PM",
        "May 6, 2007 3:50 PM",
        "May 6, 2007 12:50 PM",
        "Wed Aug 29, 2007 1:55 PM",
        "Wed Aug 2, 2006 3:13 PM",
        "1/20/2004 at 9:51 AM",
        "4/21/08",
        "4/14/98",
        "4/9/2007 9:34 am",
        "4/9/2007",
        "9:34 am",
        # "4/9/2007   9:34 am",  # this is ridiculous
        "10/29/2009 1:53 PM",
        "12/28/2007 06:42:23",
        "Wed Apr 29, 2009",
        "3:00 PM",
        # "Wed Apr 29, 2009  3:00 PM",  # this is ridiculous
        "August of 2008",
        "February 2004",
        "3/22/01 at 2:30PM",
        "November 13 at 8am",
        "1/5/2013",
        "12/12/1948",
        "12-12-07",
        "4/9/2004 at 7:40 AM",
        "7 August '12",
        "'12-August",
        "January 2016",
        "22 January 2016",
        "31 Dec 2016",
        "02/26/2001,6:24 AM",
        "March of 1995",
        "January 3",
        "January 3rd of this year",
        "6-12-06",
        "2016-02-18T20:15:37.421Z",
        "2014-10-07T14:45:00Z",
        "2016-08-18 09:52:39.694821",
        "2016-08-18 09:52:39.694",
        "2013-01-29 23:00:00",
        "2009-09-25 23:00:00.0",
        "2016-02-21 23:00:00.0",
    ]

    for date in valid_datetimes:
        assert identifier.is_of_this_type(date), date


def test_invalid_patterns_fast():
    identifier = DateTime(fast=True)

    invalid_patterns = [
        "8684     04-08-1951",
        "foobar",
        "01-01-1981 27:05:22",
        "Tue, 32 Apr 2017 10:35:17 GMT",
        "",
    ]

    for date in invalid_patterns:
        assert not identifier.is_of_this_type(date), date
