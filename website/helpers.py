
import random


def determine_style(gain_or_loss_percentage):
    if gain_or_loss_percentage > 0:
        return "color: #00A000;"
    else:
        return "color: red;"

def calculate_future_value(initial_value, growth_rate, num_years):
    future_value = initial_value * (1 + growth_rate) ** num_years
    return future_value

def calculate_intrinsic_value(ev_mktcap,current_revenue,revenue_growth_rate,metric,metric_margin,ratio,ror,num_of_years,shares_outstanding,shares_growth):
    ending_value = current_revenue * (1 + revenue_growth_rate) ** num_of_years
    shares_ending = shares_outstanding * (1 + shares_growth) ** num_of_years
    fair_value = ((ending_value * metric_margin * ratio) / shares_ending) * ((1 / (1+ror) ) ** num_of_years)

    return fair_value


def calculate_annual_growth_rate(initial_value, end_value, num_years):
    if initial_value <= 0 or end_value <= 0 or num_years <= 0:
        raise ValueError("All inputs must be positive numbers and number of years must be greater than zero.")

    growth_rate = ((end_value / initial_value) ** (1 / num_years)) - 1
    annual_growth_rate_percentage = growth_rate * 100
    return round(annual_growth_rate_percentage,2)

def get_random_color():
    # Generate a random color in hexadecimal format
    color = "#{:02X}{:02X}{:02X}".format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )
    return color

