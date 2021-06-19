import requests
from bs4 import BeautifulSoup
import datetime


def dantem_login(username: str, password: str) -> requests.Session:
    """
    Creates a session and posts login info to the server.
    :param username: login username
    :param password: user password
    :return: session to use for scanning the marketplace
    """
    session = requests.Session()
    url = "https://dap.dantem.net/auth/login/"
    payload = {"username": username,
               "password": password,
               "send":     "Přihlásit se",
               "_do":      "signInForm-submit"}

    session.post(url, data=payload)
    return session


def scan_and_accept(session: requests.Session,
                    from_date: str,
                    to_date: str,
                    dates: list,
                    accept: bool): -> str:
    """
    Function encompassing the entire scan process.
    Scans the market for new shifts and then either accepts or reports it
    based on arguments.
    :param session: requests.session to use for the scan
    :param from_date: first date to scan
    :param to_date: last date to scan
    :param dates: time availability of the user for accepting shifts
    :param accept: boolean to indicate wheter to autoaccept shifts
    :return: string with info about the results
    """
    now = datetime.datetime.today().strftime('%H:%M:%S')
    scan_response = scan_market(session=session,
                                from_date=from_date,
                                to_date=to_date)
    if is_empty(scan_response):
        return f"{now}  -  Žádné nové nabídky"
        pass
    else:
        shifts = parse_market(scan_response)
        for shift in shifts:
            if is_valid_offer(shift, dates):
                if accept:
                    accept_offer(session, shift)
                return f"{now}  -  Nabídka přijata! - {shift_to_string(shift)}"
            else:
                return f"{now}  -  Nová nabídka neodpovídající " \
                       f"časovým možnostem: {shift_to_string(shift)}"
            

def scan_and_report(session: requests.Session,
                    from_date: str,
                    to_date: str,
                    dates: list) -> str:
    """
    Not used for now.
    """
    now = datetime.datetime.today().strftime('%H:%M:%S')
    scan_response = scan_market(session=session,
                                from_date=from_date,
                                to_date=to_date)
    if is_empty(scan_response):
        return f"{now}  -  Žádné nové nabídky"
        pass
    else:
        shifts = parse_market(scan_response)
        for shift in shifts:
            if is_valid_offer(shift, dates):
                return f"{now}  -  Nová zajímavá nabídka! - " \
                       f"{shift_to_string(shift)}"
            else:
                return f"{now}  -  Nová nabídka neodpovídající " \
                       f"časovým možnostem: {shift_to_string(shift)}"


def scan_market(session: requests.Session,
                from_date: str,
                to_date: str) -> requests.models.Response.text:
    """
    Connects to the marketplace and retrieves its content.
    :param session: requests.session to use for the scan
    :param from_date: first date to scan
    :param to_date: last date to scan
    :return: response text of the marketplace website
    """
    market_form = {"fromDate":      from_date,
                   "toDate":        to_date,
                   "type":          "all",
                   "inventoryType": "all",
                   "transport":     "all",
                   "filter":        "Filtrovat",
                   "_do":           "market-filterForm-submit"
                   }

    response = session.post("https://moznosti.dantem.net/options/market/",
                            data=market_form)
    response.close()
    return response.text


def is_empty(response: requests.models.Response.text) -> bool:
    """
    Checks wheter there are new shifts available on the market.
    :param response: response text of the market website
    :return: True if empty, False otherwise
    """
    no_offer_text = "Aktuálnímu filtru neodpovídají žádné nabídky"
    return no_offer_text in response


def parse_market(response: requests.models.Response.text) -> list:
    """
    Utilizes BeautifulSoup to parse the market website and organize its content.
    :param response: response text of the market website
    :return: list conatining shift info as dictionaries
    """
    soup = BeautifulSoup(response, "html.parser")
    body = soup.findAll("body")[0]
    divs = body.findAll("div")

    time_class = "time"

    dates_h3 = soup.findAll("h3")
    nr_offers = len(dates_h3)
    inv_dict = []

    for i in range(nr_offers):
        date_str = dates_h3[i].text.strip()
        time_div = body.findAll("div", class_=time_class)[i]
        time_range = time_div.text.strip()
        time_str = time_range.split("-")[0].strip()
        date_time_str = date_str + " " + time_str

        # Ve verzi pro VI: place_index je time_div +2
        place_index = divs.index(time_div) + 1
        place = divs[place_index].text.split("\n")[2].strip()[:-1]

        link_index = divs.index(time_div) + 2
        link = divs[link_index].findAll("a")[0].attrs["href"]

        shift = {"datetime": date_time_str, "place": place, "link": link}
        inv_dict.append(shift)

    return inv_dict


def get_datetime(shift: dict) -> datetime.datetime:
    """
    Converts a string of shift start time into a python datetime.
    :param shift: dict with shift info
    :return: datetime object of shift start time
    """
    date_time = shift["datetime"]
    dt = datetime.datetime.strptime(date_time, "%d.%m.%Y %H:%M")
    return dt


def is_in_datetime_range(start: datetime.datetime,
                         end: datetime.datetime,
                         time: datetime.datetime) -> bool:
    """
    Checks whether a datetime is in a given datetime interval.
    :param start: start of the interval to check against
    :param end: end of the interval to check against
    :param time: datetime to check
    :return: True if in interval, False otherwise
    """
    return start <= time <= end


def is_valid_offer(shift: dict,
                   dates: list) -> bool:
    """
    Checks whether the offer is valid based on its date and time availability.
    :param shift: dict with shift info
    :param dates: time availability of the user
    :return: True if the shift is valid, False otherwise
    """
    shift_time = get_datetime(shift)
    is_valid = False
    for date in dates:
        if is_in_datetime_range(date[0], date[1], shift_time):
            is_valid = True
            break

    return is_valid


def accept_offer(session: requests.Session, shift: dict) -> None:
    """
    Accepts the shift offer.
    :param session: active session of the marketplace
    :param shift: dict with shift info
    :return: None
    """
    link = shift["link"]
    session.post(link)


def shift_to_string(shift: dict) -> str:
    """
    Converts a shift dict to a string.
    :param shift: dict with shift info
    :return: string with shift info
    """
    shift_string = ""
    shift_string += shift["datetime"]
    shift_string += ",  "
    shift_string += shift["place"]
    return shift_string


