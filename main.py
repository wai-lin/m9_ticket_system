from test.isolation_test import run_isolation_test
from test.performance_test import run_performance_test


def main():
    print("Hello from m9-ticket-system!")


if __name__ == "__main__":
    run_performance_test(1000)
    run_isolation_test(user_a_id=1, user_b_id=2, target_seat_id=1)
