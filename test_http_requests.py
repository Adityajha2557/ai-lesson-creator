"""
HTTP request/response test script for the AI Lesson Creator assignment.

This script uses httpbin's public test endpoints to demonstrate:
- GET request returning 200
- POST request returning 200
- GET request returning 404
- POST request returning 400
- GET request returning 500

These are controlled HTTP status tests. They do not modify your lesson app
or require any API keys.
"""
import requests

BASE_URL = "https://httpbin.org"


def run_test(name, method, url, expected_status, **kwargs):
    print(f"\n--- {name} ---")
    print(f"Request: {method} {url}")

    try:
        response = requests.request(method, url, timeout=20, **kwargs)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:300].replace(chr(10), ' ')}")

        if response.status_code == expected_status:
            print(f"RESULT: PASS (expected {expected_status})")
            return True

        print(f"RESULT: FAIL (expected {expected_status}, got {response.status_code})")
        return False

    except requests.RequestException as exc:
        print(f"RESULT: ERROR ({exc})")
        return False


def main():
    tests = [
        (
            "Successful GET request",
            "GET",
            f"{BASE_URL}/get",
            200,
            {},
        ),
        (
            "Successful POST request",
            "POST",
            f"{BASE_URL}/post",
            200,
            {"json": {"lesson_title": "HTTP Status Codes", "duration": 45}},
        ),
        (
            "Client error - Not Found",
            "GET",
            f"{BASE_URL}/status/404",
            404,
            {},
        ),
        (
            "Client error - Bad Request",
            "POST",
            f"{BASE_URL}/status/400",
            400,
            {"json": {"invalid": True}},
        ),
        (
            "Server error - Internal Server Error",
            "GET",
            f"{BASE_URL}/status/500",
            500,
            {},
        ),
    ]

    results = []
    for name, method, url, expected, kwargs in tests:
        results.append(run_test(name, method, url, expected, **kwargs))

    passed = sum(results)
    print("\n==============================")
    print(f"HTTP TEST SUMMARY: {passed}/{len(results)} passed")
    print("==============================")

    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
