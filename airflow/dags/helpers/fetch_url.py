import requests
import pandas as pd

def format(country):
    return '-'.join(country.lower().split())

def requester(url):
    return requests.head(url, allow_redirects=True)

def points_to_file(request):
    return request.headers.get("Content-Type", "").startswith("application")

def urls(country):
    gist = 'https://gist.githubusercontent.com/mushroomsandchai/15902c375001a982520b2fb834835cd1/raw/ffde31abc1b1de4726afa861a2e83f6044d3f19c/osm_links.csv'
    df = pd.read_csv(gist)
    country = format(country)
    df = df[df['country'] == country]
    
    if df.shape[0] == 0:
        raise ValueError(f'Country - {country.upper()} not found.')
    else:
        return([(url.removesuffix('-latest.osm.pbf').split('/')[-1] + '.osm.pbf', url, country) for url in df['url']])