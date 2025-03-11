#!/usr/bin/env python3

import dns.resolver
import time
from prettytable import PrettyTable
import datetime

custom_dns_server = '8.8.8.8' # set name server 'None' for system defaults
interval = 1  # set test intervals

def resolve_domain(domain, table, row_index, success_counts, total_counts, response_times, custom_nameserver=None):
    """Resolves a single domain and updates the table."""
    try:
        resolver = dns.resolver.Resolver()
        if custom_nameserver:
            resolver.nameservers = [custom_nameserver]
            nameserver = custom_nameserver
        else:
            nameserver = resolver.nameservers[0]

        start_time = time.time()
        answers = resolver.resolve(domain)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000 #milliseconds.

        table.rows[row_index][table.field_names.index("Status")] = "Pass"
        table.rows[row_index][table.field_names.index("Last Success")] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_str = ", ".join(str(rdata) for rdata in answers)
        table.rows[row_index][table.field_names.index("Records")] = record_str
        table.rows[row_index][table.field_names.index("DNS Server")] = nameserver

        success_counts[domain] = success_counts.get(domain, 0) + 1
        response_times[domain].append(response_time)

    except dns.resolver.NXDOMAIN:
        table.rows[row_index][table.field_names.index("Status")] = "Fail (NXDOMAIN)"
        table.rows[row_index][table.field_names.index("Records")] = "NXDOMAIN"
    except dns.resolver.Timeout:
        table.rows[row_index][table.field_names.index("Status")] = "Fail (Timeout)"
        table.rows[row_index][table.field_names.index("Records")] = "Timeout"
    except dns.resolver.NoAnswer:
        table.rows[row_index][table.field_names.index("Status")] = "Fail (Invalid Response)"
        table.rows[row_index][table.field_names.index("Records")] = "Invalid Response"
    except dns.resolver.NoNameservers:
        table.rows[row_index][table.field_names.index("Status")] = "Fail (No Response)"
        table.rows[row_index][table.field_names.index("Records")] = "No Response"
    except Exception as e:
        table.rows[row_index][table.field_names.index("Status")] = f"Fail (Error: {e})"
        table.rows[row_index][table.field_names.index("Records")] = f"Error: {e}"

def resolve_domains_continuously(domains, custom_nameserver=None):
    """Resolves a list of domains every second and updates a table."""
    table = PrettyTable()
    table.field_names = ["Domain", "Status", "Last Success", "Records", "DNS Server", "Success %", "Avg Resp (ms)"]
    for domain in domains:
        table.add_row([domain, "Pending", "N/A", "", "N/A", "0.00%", "N/A"])
    success_counts = {}
    total_counts = {}
    response_times = {domain: [] for domain in domains}

    try:
        attempt_count = 0
        while True:
            attempt_count +=1
            for i, domain in enumerate(domains):
                total_counts[domain] = total_counts.get(domain, 0) + 1
                resolve_domain(domain, table, i, success_counts, total_counts, response_times, custom_nameserver)

                if total_counts[domain] > 0:
                  percentage = (success_counts.get(domain, 0) / total_counts[domain]) * 100
                  table.rows[i][table.field_names.index("Success %")] = f"{percentage:.2f}%"

                  if success_counts.get(domain, 0) > 0:
                      avg_resp = sum(response_times[domain])/len(response_times[domain])
                      table.rows[i][table.field_names.index("Avg Resp (ms)")] = f"{avg_resp:.2f}"

            print(table)
            print("Press Ctrl+C to stop")
            time.sleep(interval)
            print("\033[H\033[J", end="")
    except KeyboardInterrupt:
        #print(table)
        print("Total attempts = {}".format(attempt_count))

if __name__ == "__main__":
    domains = [
        "status.mist.com",
        "www.msftconnecttest.com",
        "invalid-domain-test.com",
        "ipv6.msftconnecttest.com",
        "office.microsoft.com"
    ]

    print(f"Starting DNS resolution with DNS server: {custom_dns_server or 'System Default'}. Press Ctrl+C to stop.")
    resolve_domains_continuously(domains, custom_dns_server)
