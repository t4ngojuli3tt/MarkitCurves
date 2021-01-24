import xml.etree.ElementTree as ET
import zipfile as zf
import requests
import io


def get_markit_yiled(yyyymmdd, ccy):

    url = f'https://www.markit.com/news/InterestRates_{ccy}_{yyyymmdd}.zip'

    # Use request pkg to get data from url
    markit_zip = requests.get(url, stream=True)

    # Use zipfile and io to get zipfile object
    zip_file = zf.ZipFile(io.BytesIO(markit_zip.content))
    # To open Interest rate xml which is second on the list
    xml_name = zip_file.namelist()[1]
    # Read and decode to get xml string
    xml = zip_file.open(xml_name).read().decode()

    # xml tree form string
    tree = ET.fromstring(xml)

    date = tree.find('effectiveasof').text
    curvepoints = tree.findall('.//curvepoint')

    yield_dict = {}

    for i in curvepoints:
        yield_dict[i.find('tenor').text] = float(i.find('parrate').text)
    return (date, yield_dict)


if __name__ == "__main__":
    yyyymmdd = '20201230'
    ccy = 'USD'

    date, yield_dict = get_markit_yiled(yyyymmdd, ccy)

    print(date, yield_dict)
