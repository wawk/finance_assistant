from src.assistant.utils.bill_parser import parse_bill_fields

def main():
    test_commands = [
       "Add a water bill for 205 dollars due August 30th",
        "Add my electric bill for 120.50 due August 15",
        "Add garbage bill for 100 due next Friday",
        "Add gym payment due Sep 6th for 60.",
        "Add my Netflix bill for 15 due August 20 monthly",
        "Add my car insurance for 900 due December 1st yearly",
        "Add my gym membership for 60 due Sep 6th every month",
        "Add my HOA fee for 300 due July 1 quarterly",
        "Add my propane bill for 200 due November 15 seasonal",
        "Add my medical bill for 400 due tomorrow one time",
 
    ]

    for cmd in test_commands:
        fields = parse_bill_fields(cmd)
        print(f"\nCommand: {cmd}")
        print("  name     :", fields["name"])
        print("  amount   :", fields["amount"])
        print("  due_date :", fields["due_date"])
        print("  category :", fields["category"])
        print("  frequency:", fields["frequency"])

if __name__ == "__main__":
    main()