"""
Queries and import function signatures from https://www.4byte.directory/
"""
import requests
import known_hashes


def get_results(url):
    """
    Queries the API for a json formatted list of functions and their associated function signatures
    """
    resp = requests.get(url)
    resp.raise_for_status()

    json_data = resp.json()
    next_url = json_data["next"]
    results = json_data["results"]

    for result in results:
        hex_sig = result["hex_signature"]
        text_sig = result["text_signature"]
        # If a key already exists, do not overwrite it. This helps cover the corner
        # case of a hash collision. An example of this is
        # owner() and ideal_warn_timed(uint256,uint128)
        if int(hex_sig, 16) not in known_hashes.known_hashes:
            # hex_sig is a 'str', parse it into an 'int'
            known_hashes.known_hashes[int(hex_sig, 16)] = text_sig

    return next_url


def iterate_paginated_results(url):
    """
    4byte paginates the results for effeciency because there are > 400,000 function signatures.
    This will move from page to page and collect all the signatures available.
    """
    i = 1
    while True:
        print(f"Iterating results on page: {i}")
        url = get_results(url)
        if not url:
            break

        i += 1

    print("Finished iterating over results")


def sort_dict(unsorted_dict):
    sorted_dict = dict(sorted(unsorted_dict.items()))
    return sorted_dict


def save_results():
    """
    Write the dict to the known_hashes.py file
    We write the key and value as shown below to maintain the current format
    of the key being an int - displayed as hex (4 bytes).
    """
    sorted_dict = sort_dict(known_hashes.known_hashes)
    with open("known_hashes.py", "w") as f:
        f.write("known_hashes = {\n")
        for k, v in sorted_dict.items():
            # format the key as so
            # pad the output with 0's (#0)
            # pad the output to 10 char's (10)
            # format into hex representation (x)
            f.write(f"  {k:#010x}: '{v}',\n")
        f.write("}\n")

    print("Saved results!")


if __name__ == "__main__":
    iterate_paginated_results("https://www.4byte.directory/api/v1/signatures/")
    save_results()
