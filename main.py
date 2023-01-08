import json

# load and parsing json data  -->  name, cpu and memory usage, created_at, status and IP address

with open('sample-data.json') as json_file:
    data = json.load(json_file)

    for container in data:
        print("name:", container["name"])

        try:
            print("usage cpu:", container["state"]["cpu"]["usage"])
        except Exception as e:
            print(f"usage cpu: None data {e}")

        try:
            print("usage memory:", container["state"]["memory"]["usage"])
        except Exception as e:
            print(f"usage memory: None data {e}")

        print("created_at:", container["created_at"])

        print("status:", container["status"])

        try:
            print("ip address:", container["state"]["network"]["eth0"]["addresses"][0]["address"])
        except Exception as e:
            print(f"ip address: None data {e}")

        print("\n")
