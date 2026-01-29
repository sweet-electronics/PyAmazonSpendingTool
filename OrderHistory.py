import csv
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt

CSV_FILE = "Retail.OrderHistory.1.csv"


# -----------------------
# Utility Functions
# -----------------------

def parse_money(value):
    if value is None:
        return None

    value = value.strip()
    if not value:
        return None

    value = value.replace(",", "")

    try:
        return float(value)
    except ValueError:
        return None


# -----------------------
# Data Loading
# -----------------------

def load_orders(csv_path):
    """
    Returns dict:
    order_id -> { "date": datetime, "subtotal": float }
    """
    orders = {}

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            order_id = row["Order ID"]

            if order_id in orders:
                continue

            subtotal = parse_money(row["Shipment Item Subtotal"])
            if subtotal is None:
                continue

            dt = datetime.fromisoformat(
                row["Order Date"].replace("Z", "")
            )

            orders[order_id] = {
                "date": dt,
                "subtotal": subtotal,
                "refund": 0.0
            }

    return orders


def load_refunds(csv_path):
    """
    Returns dict:
    order_id -> total_refund_amount
    """
    refunds = defaultdict(float)

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            order_id = row["OrderID"]

            amount = parse_money(row["AmountRefunded"])
            if amount is None:
                continue

            refunds[order_id] += amount

    return refunds


def apply_refunds(orders, refunds):
    for order_id, refund_amount in refunds.items():
        if order_id in orders:
            orders[order_id]["refund"] += refund_amount


# -----------------------
# Reporting
# -----------------------

def yearly_totals(orders):
    totals = defaultdict(float)

    for order in orders.values():
        net = order["subtotal"] - order["refund"]
        totals[order["date"].year] += net

    return totals


def monthly_totals_for_year(orders, year):
    totals = defaultdict(float)

    for order in orders.values():
        if order["date"].year == year:
            net = order["subtotal"] - order["refund"]
            totals[order["date"].month] += net

    return totals


def plot_monthly_totals(monthly_totals, year):
    months = range(1, 13)
    values = [monthly_totals.get(m, 0.0) for m in months]

    plt.figure()
    plt.bar(months, values)
    plt.xticks(months, [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ])
    plt.xlabel("Month")
    plt.ylabel("Net Amount Spent ($)")
    plt.title(f"Amazon Net Spend by Month — {year}")
    plt.tight_layout()
    plt.show()


# -----------------------
# Menu
# -----------------------

def print_menu(refunds_loaded):
    print("\n=== Amazon Spend Analyzer ===")
    print("1) View yearly totals")
    print("2) View monthly graph for a year")
    print("3) Load refunds CSV")
    print("4) Exit")
    if refunds_loaded:
        print("   (Refunds applied ✔)")


def main():
    print("Loading Amazon order data...")
    orders = load_orders(CSV_FILE)

    if not orders:
        print("No valid order data found.")
        return

    refunds_loaded = False

    while True:
        print_menu(refunds_loaded)
        choice = input("Select an option: ").strip()

        if choice == "1":
            totals = yearly_totals(orders)
            print("\nYearly Totals")
            if refunds_loaded:
                print(" (Net with Refunds):")
            for year in sorted(totals):
                print(f"{year}: ${totals[year]:,.2f}")

        elif choice == "2":
            try:
                year = int(input("Enter year (e.g. 2026): "))
            except ValueError:
                print("Invalid year.")
                continue

            monthly = monthly_totals_for_year(orders, year)

            if not monthly:
                print(f"No data found for {year}.")
                continue

            plot_monthly_totals(monthly, year)

        elif choice == "3":
            refund_path = input("Enter refunds CSV path: ").strip()

            try:
                refunds = load_refunds(refund_path)
                apply_refunds(orders, refunds)
                refunds_loaded = True
                print(f"Loaded refunds for {len(refunds)} orders.")
            except Exception as e:
                print(f"Failed to load refunds file: {e}")

        elif choice == "4":
            print("Goodbye 👋")
            break

        else:
            print("Invalid selection.")


if __name__ == "__main__":
    main()
