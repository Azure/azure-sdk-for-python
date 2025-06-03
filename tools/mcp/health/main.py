import sys
import csv
import logging
from io import StringIO
from typing import Dict, Any

import httpx
from mcp.server.fastmcp import FastMCP


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)

mcp = FastMCP("python_sdk_health")


@mcp.tool("check_library_health")
def check_library_health(library_name: str) -> Dict[str, Any]:
    """Checks the health status of a client library.

    :param str library_name: The name of the library to check.
    :returns: A dictionary containing the result of the command.
    """

    url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/python-sdk-health-report/scripts/repo_health_status_report/health_report.csv"
    response = httpx.get(url)

    try:
        response.raise_for_status()

        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)
        
        headers = next(reader)
        column_headers = headers[1:]

        result = {}
        for row in reader:
            if row:
                key = row[0]
                values_dict = {header: value for header, value in zip(column_headers, row[1:])}
                result[key] = values_dict
        
    except httpx.HTTPError as e:
        logger.error(f"Error downloading health report: {e}")
        return {
            "success": False,
            "stderr": f"Failed to fetch health report for {library_name}. Status code: {response.status_code}",
            "stdout": "",
            "code": response.status_code
        }

    return {
        "success": True,
        "stdout": result[library_name] if library_name in result else f"No health data found for {library_name}",
        "stderr": "",
        "code": response.status_code
    }

if __name__ == "__main__":
    mcp.run(transport='stdio')
