import csv
import random
from datetime import datetime, timedelta
import pandas as pd
import holidays

def format_duration(seconds):
    """
    Convert seconds to HH:MM:SS format
    Example: 94 seconds -> "00:01:34"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"

def generate_call_chain():
    """
    Generate realistic call chains based on observed patterns from production data
    """
    external_numbers = [f"0{random.randint(100000000, 999999999)}" for _ in range(5)] + \
                    ["0471662023", "0478707333", "0232360433"]
    
    ivr_queue_extensions = ["Ext.610", "Ext.611", "Ext.612", "Ext.615"]
    agent_extensions = ["Ext.111", "Ext.114", "Ext.115", "Ext.129", "Ext.184", 
                    "Ext.185", "Ext.194", "Ext.195", "Ext.315", "Ext.318"]

    scenario = random.choices(
        ["external_to_agent", "external_transfer", "direct_outbound", "internal"], 
        weights=[40, 30, 15, 15]
    )[0]

    if scenario == "external_to_agent":
        path = [
            random.choice(external_numbers),
            random.choice(ivr_queue_extensions),
            random.choice(agent_extensions)
        ]
    elif scenario == "external_transfer":
        path = [
            random.choice(external_numbers),
            random.choice(ivr_queue_extensions),
            random.choice(agent_extensions),
            random.choice(external_numbers)
        ]
    elif scenario == "direct_outbound":
        path = [
            random.choice(agent_extensions),
            random.choice(external_numbers)
        ]
    else:  # internal
        path = [
            random.choice(agent_extensions),
            random.choice(agent_extensions)
        ]

    return f"Chain: {','.join(path)},"

def is_working_day(date):
    """
    Check if date is a working day (not weekend or holiday)
    """
    fr_holidays = holidays.France()
    return date not in fr_holidays

def determine_duration(is_answered, chain_length):
    """
    Generate realistic call durations based on call type and chain length
    """
    if not is_answered:
        seconds = random.randint(3, 20)
    elif chain_length == 2:  # Direct calls
        seconds = random.randint(30, 300)  # 30s to 5min
    else:  # Calls with transfers
        seconds = random.randint(60, 900)  # 1min to 15min
    
    return format_duration(seconds)

def determine_call_termination(is_answered, from_no, to_no):
    """
    Set termination reason based on business rules
    """
    if not is_answered:
        return "Failed_Cancelled" if random.random() < 0.7 else "TerminatedBySrc"
    
    if from_no.startswith("0"):  # External caller
        return "TerminatedBySrc" if random.random() < 0.6 else "TerminatedByDst"
    else:  # Internal caller
        return "TerminatedByDst" if random.random() < 0.6 else "TerminatedBySrc"

def determine_missed_queue_calls(path_elements, is_answered):
    """
    Track extensions that missed queue calls
    Example: If call goes from 0471662023 -> Ext.611 -> Ext.184 but not answered,
    then Ext.184 is added to missed_queue_calls
    """
    if not is_answered and len(path_elements) > 2:
        # Check if call came through a queue (61x)
        for i, element in enumerate(path_elements):
            if element.startswith("Ext.61"):
                # Return the next extension in the chain that missed the call
                if i + 1 < len(path_elements) and path_elements[i + 1].startswith("Ext."):
                    return path_elements[i + 1]
    return ""

def generate_random_call_data(date, num_records, start_id):
    """
    Generate random CDR records for a given date
    """
    call_data = []
    hour = 8
    minutes = 0
    
    display_names = {
        "Ext.610": "IVR Principal",
        "Ext.611": "File Support",
        "Ext.612": "File Commercial",
        "Ext.615": "File SAV",
        "Ext.184": "Support N2",
        "Ext.185": "Commercial",
        "Ext.194": "Support N1",
        "Ext.195": "SAV",
        "Ext.315": "Direction",
        "Ext.318": "Comptabilité"
    }

    for i in range(num_records):
        historyid = start_id + i
        callid = f"{random.randint(1000000000000000, 9999999999999999)}_{random.randint(1000, 9999)}"
        
        chain = generate_call_chain()
        path_elements = chain.replace("Chain: ", "").replace(",", " ").split()
        
        from_no = path_elements[0]
        to_no = path_elements[1]
        final_number = path_elements[-1]
        
        call_type = "External" if from_no.startswith("0") else "Internal"
        
        # Business hours distribution
        hour = random.choices(
            range(8, 19),
            weights=[5, 10, 15, 20, 15, 10, 5, 15, 20, 15, 10],
            k=1
        )[0]

        # In generate_random_call_data function:
        if any(x.startswith("Ext.61") for x in path_elements):
            queue_ext = next(x for x in path_elements if x.startswith("Ext.61"))
            hour_result, minutes_result = get_valid_hour(date, queue_ext)
            if hour_result is not None:
                hour = hour_result
                minutes = minutes_result
            else:
            # Regular business hours for non-queue calls
                hour = random.randint(8, 18)
                minutes = random.randint(0, 59)
        time_start = date + timedelta(hours=hour, minutes=minutes)

        is_answered = random.random() > 0.2
        
        duration = determine_duration(is_answered, len(path_elements))
        
        if is_answered:
            time_answered = time_start + timedelta(seconds=random.randint(3, 15))
            time_end = time_answered + timedelta(seconds=random.randint(30, 900))
        else:
            time_answered = None
            time_end = time_start + timedelta(seconds=random.randint(3, 20))

        reason_terminated = determine_call_termination(is_answered, from_no, to_no)
        # In generate_random_call_data function:
        missed_queue_calls = determine_missed_queue_calls(path_elements, is_answered)

        call_record = [
            historyid,
            callid,
            duration,
            time_start.strftime("%Y/%m/%d %H:%M:%S"),
            time_answered.strftime("%Y/%m/%d %H:%M:%S") if time_answered else "",
            time_end.strftime("%Y/%m/%d %H:%M:%S"),
            reason_terminated,
            from_no,
            to_no,
            from_no,
            to_no,
            final_number,
            "",  # reason_changed
            final_number,
            final_number,
            "",  # bill_code
            "",  # bill_rate
            "",  # bill_cost
            "",  # bill_name
            chain,
            call_type,
            call_type,
            call_type,
            "External Caller" if from_no.startswith("0") else display_names.get(from_no, "Unknown"),
            display_names.get(to_no, "Unknown"),
            display_names.get(final_number, "Unknown"),
            missed_queue_calls
        ]
        
        call_data.append(call_record)

    return call_data

def get_valid_hour(date, queue_extension):
    """
    Queue schedule rules:
    - Ext.610: Mon-Fri 07:30-17:30, Sat 07:30-14:00
    - Ext.611, Ext.612: Mon-Fri 08:30-17:30, no weekend
    - All queues end at 17:00 on Friday
    """
    weekday = date.weekday()
    is_friday = weekday == 4
    is_saturday = weekday == 5
    is_sunday = weekday == 6

    if queue_extension in ["Ext.611", "Ext.612"] and (is_saturday or is_sunday):
        return None, None

    if queue_extension == "Ext.610":
        start_hour = 7.5
        if is_saturday:
            end_hour = 14
        elif is_friday:
            end_hour = 17
        else:
            end_hour = 17.5
    else:
        if is_friday:
            start_hour = 8.5
            end_hour = 17
        else:
            start_hour = 8.5
            end_hour = 17.5

    hour = random.uniform(start_hour, end_hour)
    full_hour = int(hour)
    minutes = int((hour % 1) * 60)
    
    return full_hour, minutes

def save_to_csv(file_path, call_data):
    """
    Save generated call data to CSV file
    """
    columns = [
        "historyid", "callid", "duration", "time_start", "time_answered", "time_end",
        "reason_terminated", "from_no", "to_no", "from_dn", "to_dn", "dial_no",
        "reason_changed", "final_number", "final_dn", "bill_code", "bill_rate",
        "bill_cost", "bill_name", "chain", "from_type", "to_type", "final_type",
        "from_dispname", "to_dispname", "final_dispname", "missed_queue_calls"
    ]
    
    df = pd.DataFrame(call_data, columns=columns)
    df.to_csv(file_path, index=False)

if __name__ == "__main__":
    start_date = datetime.strptime("2020-05-12", "%Y-%m-%d")
    end_date = datetime.now()
    current_date = start_date
    call_id_counter = 1
    fr_holidays = holidays.France()

    while current_date <= end_date:
        # Skip holidays
        if current_date in fr_holidays:
            current_date += timedelta(days=1)
            continue

        if current_date.weekday() < 5:
            num_records = random.randint(80, 120)
        else:
            num_records = random.randint(10, 30)
            
        call_data = generate_random_call_data(current_date, num_records, call_id_counter)
        file_path = f"./fake_datas/call_data_{current_date.strftime('%Y_%m_%d')}.csv"
        save_to_csv(file_path, call_data)
        
        call_id_counter += num_records
        current_date += timedelta(days=1)
