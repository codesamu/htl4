#!/usr/bin/env python3

import sys
import requests

BASE_URL = "http://10.10.11.11:5003/api/users"


def usage() -> None:
	print("Usage:")
	print("  python3 client.py list")
	print("  python3 client.py get <id>")
	print("  python3 client.py create <name> <email>")


def main(argv: list[str]) -> int:
	if not argv:
		usage()
		return 2

	cmd = argv[0]

	try:
		if cmd == "list":
			resp = requests.get(BASE_URL, timeout=10)
			resp.raise_for_status()
			print(resp.json())
			return 0
		elif cmd == "get":
			if len(argv) < 2:
				usage()
				return 2
			user_id = argv[1]
			resp = requests.get(f"{BASE_URL}/{user_id}", timeout=10)
			if resp.status_code == 404:
				print({"error": "Not Found", "id": user_id})
				return 1
			resp.raise_for_status()
			print(resp.json())
			return 0
		elif cmd == "create":
			if len(argv) < 3:
				usage()
				return 2
			name = argv[1]
			email = argv[2]
			resp = requests.post(BASE_URL, json={"name": name, "email": email}, timeout=10)
			resp.raise_for_status()
			print(resp.json() if resp.content else {"status": resp.status_code})
			return 0
		else:
			usage()
			return 2
	except requests.RequestException as exc:
		print({"error": str(exc)})
		return 1


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:])) 
