"""This file holds the Altair scripts to produce the App Lab and CSXL Visualizations."""

import pandas as pd
import altair as alt

def csxl_distinct_visitors(csv_file_path: str) -> int:
    """
    Calculate the number of distinct visitors at the CSXL.

    Args:
        csv_file_path (str): The file path to the CSV containing CSXL data.

    Returns:
        int: The number of distinct visitors to the CSXL.
    """
    data = pd.read_csv(csv_file_path)
    return data['user_id'].nunique()


def app_lab_distinct_visitors(csv_file_path: str) -> int:
    """
    Calculate the number of distinct visitors at the App Lab.

    Args:
        csv_file_path (str): The file path to the CSV containing App Lab data.

    Returns:
        int: The number of distinct visitors to the App Lab.
    """
    data = pd.read_csv(csv_file_path)
    return data['PID'].nunique()


def csxl_leaderboard(csv_file_path: str) -> alt.Chart:
    """
    Generate a leaderboard (horizontal bar chart) showing the total time spent in the XL for the top 10 users.

    Args:
        csv_file_path (str): The file path to the CSV containing CSXL data.

    Returns:
        alt.Chart: An Altair chart object representing the leaderboard.
    """
    data = pd.read_csv(csv_file_path)

    data['start'] = pd.to_datetime(data['start'], format='mixed')
    data['end'] = pd.to_datetime(data['end'], format='mixed')

    # Convert reservation_length from seconds into days
    data['reservation_length'] = (data['end'] - data['start']).dt.total_seconds() / 3600 / 24

    # Filter out reservations that are too long (for ex, start and end a month apart – looking at you, user 385)
    filtered_data = data[data['reservation_length'] < (8 / 24)]

    # Find the total amount of time each user spent in the XL (according to reservations)
    total_user_reservation_times = filtered_data.groupby('user_id')['reservation_length'].sum().reset_index()

    total_user_reservation_times.columns = ['user_id', 'total_time']

    top_10_users = total_user_reservation_times.sort_values(by='total_time', ascending=False).head(10)

    # Create a horizontal bar chart leaderboard (filtering out reservations > 5 hours long)
    chart = alt.Chart(top_10_users).mark_bar().encode(
        y=alt.Y('user_id:O', title='User ID', sort='-x'),
        x=alt.X('total_time:Q', title='Total Time (Days)'),
        tooltip=alt.Tooltip('total_time:Q', format='.2f')
    ).properties(
        title='CSXL Total Time per User'
    ).configure_mark(color='#4786c6')

    return chart

def app_lab_leaderboard(csv_file_path: str) -> alt.Chart:
    """
    Generate a leaderboard (horizontal bar chart) showing the total time spent in the App Lab for the top 10 users.

    Args:
        csv_file_path (str): The file path to the CSV containing App Lab data.

    Returns:
        alt.Chart: An Altair chart object representing the leaderboard.
    """
    data = pd.read_csv(csv_file_path)

    # Create convert duration to number of days per reservation
    data['Duration (days)'] = pd.to_timedelta(data['Duration']).dt.total_seconds() / (24 * 60 * 60) 

    # Filter out outlier reservations
    filtered_data = data[data['Duration (days)'] < (8 * 24)]

    # Create table for top 10 students in duration of time.  
    duration_by_pid = filtered_data.groupby(['PID'])
    duration_by_pid = duration_by_pid['Duration (days)'].sum().reset_index()
    duration_by_pid = duration_by_pid.sort_values(by='Duration (days)', ascending=False)
    duration_by_pid = duration_by_pid.head(10)

    chart = alt.Chart(duration_by_pid).mark_bar().encode(
        y=alt.Y('PID:O', title='User ID', sort="-x"),
        x=alt.X('Duration (days)', title='Total Time (Days)'),
        tooltip=alt.Tooltip('Duration (days)')
    ).properties(
        title='App Lab Total Time per User'
    ).configure_mark(color='#4786c6')

    return chart


def popular_times_comparison(app_lab_csv_file_path: str, csxl_csv_file_path: str):
    """
    Generate visualizations (bar charts) showing the popular times in the App Lab + CSXL, with equivalent y axis scales.

    Args:
        app_lab_csv_file_path (str): The file path to the CSV containing App Lab data.
        csv_file_path (str): The file path to the CSV containing CSXL data.

    Returns:
        list[alt.Chart]: A list of Altair chart objects representing the popular times in the App Lab.
        The App Lab chart appears first in the list and is followed by the CSXL chart.
    """
    app_lab_data = pd.read_csv(app_lab_csv_file_path)

    app_lab_data['date'] = pd.to_datetime(app_lab_data['date'], format='mixed')

    app_lab_data['timeIn'] = pd.to_timedelta(app_lab_data['timeIn'])

    app_lab_data['start'] = app_lab_data['date'] + app_lab_data['timeIn']

    # Get the day of the week
    app_lab_data['day_of_week'] = app_lab_data['start'].dt.day_name()

    # Get the hour of the day in non-military time (also remove leading 0s, for example, 01pm -> 1pm)
    app_lab_data['civilian_time'] = app_lab_data['start'].dt.strftime("%I %p").str.lstrip("0")

    # Group reservations by the day of the week + hour of the day + count the number ofidfferent reservations
    app_lab_reservations_per_hour = app_lab_data.groupby(["day_of_week", "civilian_time"]).size().reset_index(name="count")

    # Filter out Saturday and Sunday from App Lab data (since XL does not take reservations on weekends)
    app_lab_reservations_per_hour = app_lab_reservations_per_hour[app_lab_reservations_per_hour['day_of_week'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]

    xl_data = pd.read_csv(csxl_csv_file_path)

    xl_data['start'] = pd.to_datetime(xl_data['start'], format='mixed')

    # Get the day of the week
    xl_data['day_of_week'] = xl_data['start'].dt.day_name()

    # Get the hour of the day in non-military time (also remove leading 0s, for example, 01pm -> 1pm)
    xl_data['civilian_time'] = xl_data['start'].dt.strftime('%I %p').str.lstrip("0")

    # Group reservations by the day of the week + hour of the day + count the number of different reservations
    xl_reservations_per_hour = xl_data.groupby(['day_of_week', 'civilian_time']).size().reset_index(name='count')

    # Determine the maximum count for both datasets (for scaling the y axes)
    max_count = max(app_lab_reservations_per_hour['count'].max(), xl_reservations_per_hour['count'].max())

    # Create a domain for equal x axis
    x_domain = ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM']

    app_lab_chart = alt.Chart(app_lab_reservations_per_hour).mark_bar().encode(
        x=alt.X('civilian_time:N', title='Hour of the Day', sort=x_domain),
        y=alt.Y('count:Q', title='Reservations', scale=alt.Scale(domain=[0, max_count])),
        column=alt.Column('day_of_week:N', title=None, sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']),
        tooltip=alt.Tooltip('count:Q')
    ).properties(
        height=150,
        title='Popular Times in the App Lab'
    ).configure_mark(color='#4786c6')

    xl_chart = alt.Chart(xl_reservations_per_hour).mark_bar().encode(
        x=alt.X('civilian_time:N', title='Hour of the Day', sort=x_domain, scale=alt.Scale(domain=x_domain)),
        y=alt.Y('count:Q', title='Reservations', scale=alt.Scale(domain=[0, max_count])),
        column=alt.Column('day_of_week:N', title=None, sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']),
        tooltip=alt.Tooltip('count:Q')
    ).properties(
        height=150,
        title='Popular Times in the CSXL'
    ).configure_mark(color='#4786c6')

    return [app_lab_chart, xl_chart]

def leaderboard_comparison(csxl_csv_file_path: str, app_lab_csv_file_path: str) -> list:
    """
    Generate visualizations (bar charts) showing user leaderboards for the App Lab + CSXL, with equivalent x axis scales.

    Args:
        app_lab_csv_file_path (str): The file path to the CSV containing App Lab data.
        csxl_csv_file_path (str): The file path to the CSV containing CSXL data.

    Returns:
        list[alt.Chart]: A list of Altair chart objects representing the leaderboards for App Lab and CSXL use.
        The App Lab chart appears first in the list and is followed by the CSXL chart.
    """
    # Read CSXL data
    csxl_data = pd.read_csv(csxl_csv_file_path)
    # Parse date-time columns with specified format
    csxl_data['start'] = pd.to_datetime(csxl_data['start'], format='mixed')
    csxl_data['end'] = pd.to_datetime(csxl_data['end'], format='mixed')

    # Convert reservation_length from seconds into days
    csxl_data['reservation_length'] = (csxl_data['end'] - csxl_data['start']).dt.total_seconds() / 3600 / 24

    # Filter out reservations that are too long (for ex, start and end a month apart – looking at you, user 385)
    filtered_data = csxl_data[csxl_data['reservation_length'] < (8 / 24)]

    # Calculate total time per user in CSXL
    total_user_reservation_times = filtered_data.groupby('user_id')['reservation_length'].sum().reset_index()
    total_user_reservation_times.columns = ['user_id', 'total_time']
    top_10_users_csxl = total_user_reservation_times.sort_values(by='total_time', ascending=False).head(10)
    maximum_csxl = total_user_reservation_times['total_time'].max()

    # Read App Lab data
    app_lab_data = pd.read_csv(app_lab_csv_file_path)
    # Create convert duration to number of days per reservation
    app_lab_data['Duration (days)'] = pd.to_timedelta(app_lab_data['Duration']).dt.total_seconds() / (24 * 60 * 60) 

    # Filter out outlier reservations
    filtered_data = app_lab_data[app_lab_data['Duration (days)'] < (8 * 24)]

    # Create table for top 10 students in duration of time.  
    duration_by_pid = filtered_data.groupby(['PID'])
    duration_by_pid = duration_by_pid['Duration (days)'].sum().reset_index()
    duration_by_pid = duration_by_pid.sort_values(by='Duration (days)', ascending=False)
    duration_by_pid = duration_by_pid.head(10)

    # Determine the maximum time across both datasets
    max_time = maximum_csxl

    # Create Altair charts
    app_lab_chart = alt.Chart(duration_by_pid).mark_bar().encode(
        y=alt.Y('PID:O', title='User ID', sort="-x"),
        x=alt.X('Duration (days)', title='Total Time (Days)', scale=alt.Scale(domain=[None, max_time + 1])),
        tooltip=alt.Tooltip('Duration (days)')
    ).properties(
        title='App Lab Total Time per User'
    ).configure_mark(color='#4786c6')

    csxl_chart = alt.Chart(top_10_users_csxl).mark_bar().encode(
        y=alt.Y('user_id:O', title='User ID', sort='-x'),
        x=alt.X('total_time:Q', title='Total Time (Days)', scale=alt.Scale(domain=[None, max_time + 1])),
        tooltip=alt.Tooltip('total_time:Q', format='.2f')
    ).properties(
        title='CSXL Total Time per User'
    ).configure_mark(color='#4786c6')

    return [app_lab_chart, csxl_chart]

def reservations_by_seat_type(csv_file_path: str):
    """
    Generates a bar chart showing the number of reservations by seat type in the CSXL.

    Args:
        csv_file_path (str): The file path to the CSV containing CSXL data.

    Returns:
        alt.Chart: An Altair chart object representing the reservations by seat type.
    """
    # This is just for csxl
    data = pd.read_csv(csv_file_path)

    reservations_by_seat_type = data.groupby("title").size().reset_index(name="count")

    chart = alt.Chart(reservations_by_seat_type).mark_bar().encode( 
        y = alt.Y("title:N", title="Seat Type"),
        x = alt.X("count:Q", title="Number of Reservations"),
        tooltip=['count']
    ).properties(
        title="CSXL Reservations by Seat Type",
        height=150
    ).configure_mark(color='#4786c6')

    return chart