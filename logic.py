from datetime import date
def calculate_days_left(expiry_date):
    today = date.today()

    expiry = date.fromisoformat(expiry_date)

    days_left = (expiry - today).days

    return days_left
def get_priority(days_left):

    if days_left < 0:
        return "Expired"

    elif days_left == 0:
        return "Expiring Today"

    elif days_left <= 3:
        return "High"

    elif days_left <= 7:
        return "Medium"

    else:
        return "Low"