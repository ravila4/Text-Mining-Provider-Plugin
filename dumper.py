import  requests

def get_datasets(username="NCATSTranslator", repo="Text-Mining-Provider-Roadmap"):
    path = "sample-kg/text-mined/kgx"
    url = "https://api.github.com/repos/{}/{}/contents/{}".format(
            username, repo, path)

    response = requests.get(url).json()
    last_version = [r["name"] for r in response][-1]
    url = url + "/" + last_version
    response = requests.get(url).json()
    assert len(response) == 2
    for doc in response:
        download_url = doc['download_url']
        filename = doc['name']
        text = requests.get('https://raw.githubusercontent.com/NCATSTranslator/Text-Mining-Provider-Roadmap/master/sample-kg/text-mined/kgx/v0.1/sample-craft-edges.v0.1.kgx.tsv').text
        with open(filename, 'w') as f:
            f.write(text)

if __name__ == "__main__":
    get_datasets()
