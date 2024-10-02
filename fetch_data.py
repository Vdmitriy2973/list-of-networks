import asyncio
import ipaddress
import json
import os
import sys

import aiohttp
from bs4 import BeautifulSoup
from fake_headers import Headers
from loguru import logger

from schemas import Network


async def fetch_data(path: str):
    # Extract data from BGP Scanner
    # working_dir = os.getcwd()
    # data_path = "/path/to/mrt_files"
    # os.chdir(data_path)

    # files = os.listdir(os.getcwd())
    # files = [file for file in files if file.split('.')[-1] == "dump"]
    # files.sort()
    # file = files[-2]

    # os.system(f"/root/bgpscanner/build/bgpscanner -m 43201:0 {file} > {working_dir}/{path}")
    # os.chdir(working_dir)
    # files.clear()

    arr = set(())
    with open(path, "r") as f:
        for route in f.readlines():
            as_all_data = route.split('|')[2].split(' ')
            for as_data in as_all_data:
                arr.add(as_data)

    tasks = []

    try:
        async with aiohttp.ClientSession() as session:
            header = Headers(
                browser="chrome",
                os="win",
                headers=True
            )
            base_url = "https://bgp.he.net/AS"
            for num, elem in enumerate(arr):
                url = f"{base_url}{elem}#_prefixes"
                response = await session.get(url, headers=header.generate())
                task = asyncio.create_task(gather_data(BeautifulSoup(await response.text(), "lxml"), url, num))
                tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        logger.info(f"Unexpected error occurred: {e}")


async def gather_data(soup: BeautifulSoup, url: str, num: int):
    try:
        table_prefixes = soup.find("table", id="table_prefixes4")
        tbody = table_prefixes.find("tbody")
        addresses = [tr.find("a").get("href")[5:] for tr in tbody.find_all("tr")]
        descr = [tr.find_all("td")[1].text for tr in tbody.find_all("tr")]

        for num, elem in enumerate(addresses):
            networks = ipaddress.ip_network(elem)
            first_address, last_address = networks[0], networks[-1]
            try:
                network = Network(
                    network=str(elem),
                    isp=descr[num].replace("\n", '').replace("\t", "").replace("\"", ""),
                    ip=[str(first_address), str(last_address)],
                    ip_int=[int(first_address), int(last_address)])
            except:
                network = Network(network=str(elem),
                                  isp=None,
                                  ip=[str(first_address), str(last_address)],
                                  ip_int=[int(first_address), int(last_address)])
            if Network.model_validate(network):
                return json.loads(network.model_dump_json())

    except AttributeError:
        logger.warning(f"{num + 1:<3}. {url:<5} : STATUS 404. RESOURCE ERROR")


async def main(path: str = "routes.txt") -> None:
    with open(f"networks.json", "w") as f:
        json.dump({"networks": await fetch_data(path)}, f, indent=2)


if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.mkdir("logs")
    log_format = "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> | <level>{level: ^8}</level> |<fg 213,63,213> {file}:{function}:{line}</fg 213,63,213> | <fg 47,80,189>{message}</fg 47,80,189>"
    logger.remove()
    logger.add("logs/data.txt", format=log_format, colorize=False, rotation="10MB", level="WARNING")
    asyncio.run(main())
