import time
import logging
import os
import sys

import requests
from github3 import GitHub


log = logging.getLogger(__name__)

OWNER = 'elifesciences'
REPO = 'elife-article-xml'
SHA = '2e032ca678970d84401af9db56f7c346816416d0'
TOKENS = [CHANGE_ME]

API_BASE = 'https://prod--gateway.elifesciences.org'


def _get_files(owner, repo, sha, tokens):
    """Get repo file paths
    """
    # TODO: use other tokens if first fails
    github_api = GitHub(token=tokens[0])
    repo_api = github_api.repository(owner, repo)
    # First attempt - use GitHub Tree API
    files = _get_files_tree_api(repo_api, sha)
    if files is None:
        # Tree is trancated - use GitHub Contents API
        files = _get_files_contents_api(repo_api, sha)
    log.debug(
        'Remaining GitHub API calls: %s',
        github_api.rate_limit()['rate']['remaining'])
    return files


def _get_files_tree_api(repo_api, sha):
    """Get repo file paths using GitHub Tree API.
    """
    files = []
    # https://github.com/sigmavirus24/github3.py/issues/656
    tree = repo_api.tree('%s?recursive=1' % sha).to_json()
    if tree['truncated']:
        return None
    for item in tree['tree']:
        if item['type'] == 'blob':
            files.append(item['path'])
    return files


def _get_files_contents_api(repo_api, sha, contents=None):
    """Get repo file paths using GitHub Contents API.
    """
    files = []
    if not contents:
        contents = repo_api.contents('', sha)
    for key in sorted(contents):
        item = contents[key]
        if item.type == 'file':
            files.append(item.path)
        elif item.type == 'dir':
            dir_contents = repo_api.contents(item.path, sha)
            files.extend(
                _get_files_contents_api(repo_api, sha, dir_contents))
    return files


def _get_article_ids_from_repo():
    """Parse all article names in the dump repo to get all ids
    """

    files = _get_files(OWNER, REPO, SHA, TOKENS)
    ids = []

    for _file in files:
        # elife-00308-v1.xml
        name = os.path.basename(_file)
        if name.startswith('elife'):
            ids.append(name[6:11])

    return ids


def get_article_ids():
    ids = get_article_ids()
    with open('elife_article_ids.txt', 'w') as f:

        for _id in ids:
            f.write(_id + '\n')

    print('Written {} ids in elife_article_ids.txt'.format(len(ids)))


def download_articles():

    offset = 0

    with open('elife_article_ids.txt', 'r') as f:
        ids = f.readlines()
    for index, _id in enumerate(ids[offset:]):
        _id = _id.strip('\n')
        name = 'articles/{}.json'.format(_id)
        if not os.path.exists(name):
            url = API_BASE + '/articles/' + _id
            response = requests.get(url)
            with open(name, 'wb') as out_file:
                out_file.write(response.content)
            print('Saved {0} ({1}/{2})'.format(name, index + offset, len(ids)))
            time.sleep(5)

USAGE = '''
python articles.py [ids|download]
'''


if __name__ == '__main__':

    if len(sys.argv) != 2 or sys.argv[1] not in ('ids', 'download'):
        print(USAGE)
        sys.exit(1)

    if sys.argv[1] == 'ids':
        get_article_ids()
    elif sys.argv[1] == 'download':
        download_articles()
