#!/usr/bin/python
# -*- coding: utf-8 -*-

import boto3
import os
import requests
import json
import urllib

ssm = boto3.client('ssm')
secretsmanager = boto3.client('secretsmanager')

GITLAB_API = 'https://gitlab.com/api/v4'

def get_gitlab_token(secret_arn):
    response = secretsmanager.get_secret_value(SecretId=secret_arn)
    return json.loads(response['SecretString'])['token']

def get_all_gitlab_paths():
    repos = []
    next_token = None
    while True:
        kwargs = {
            'Path': '/gitlab.com/',
            'Recursive': True,
            'WithDecryption': False,
            'MaxResults': 10,
        }
        if next_token:
            kwargs['NextToken'] = next_token
        resp = ssm.get_parameters_by_path(**kwargs)
        for p in resp['Parameters']:
            if not p['Name'].endswith('_hash'):
                repos.append(p['Value'])
        next_token = resp.get('NextToken')
        if not next_token:
            break
    return repos

def repo_path_to_project_id(repo_url):
    path = repo_url.replace('https://gitlab.com/', '').replace('.git', '')
    return urllib.quote(path, safe='')

def ci_enabled_in_settings(project_id, token):
    headers = {'PRIVATE-TOKEN': token}
    url = '%s/projects/%s' % (GITLAB_API, project_id)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return (False, None)
    data = r.json()
    return (data.get('ci_config_path') is not None, data.get('default_branch', 'main'))

def check_existing_merge_request(project_id, source_branch, token):
    headers = {'PRIVATE-TOKEN': token}
    url = '%s/projects/%s/merge_requests?state=opened&source_branch=%s' % (GITLAB_API, project_id, source_branch)
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return True
    return len(r.json()) > 0

def create_branch(project_id, new_branch, base_branch, token):
    headers = {'PRIVATE-TOKEN': token}
    url = '%s/projects/%s/repository/branches' % (GITLAB_API, project_id)
    data = {'branch': new_branch, 'ref': base_branch}
    r = requests.post(url, headers=headers, data=data)
    if r.status_code != 201:
        raise Exception('Erro ao criar branch: %s' % r.text)

def remove_ci_file(project_id, branch, token):
    headers = {'PRIVATE-TOKEN': token}
    url = '%s/projects/%s/repository/commits' % (GITLAB_API, project_id)
    data = {
        'branch': branch,
        'commit_message': 'feat(CI): Removendo arquivo CI do repositorio',
        'actions': json.dumps([
            {'action': 'delete', 'file_path': '.gitlab-ci.yml'}
        ])
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code != 201:
        raise Exception('Erro ao remover arquivo: %s' % r.text)

def open_merge_request(project_id, source_branch, target_branch, token):
    headers = {'PRIVATE-TOKEN': token}
    url = '%s/projects/%s/merge_requests' % (GITLAB_API, project_id)
    data = {
        'title': 'Automated: Remoção do CI YAML',
        'source_branch': source_branch,
        'target_branch': target_branch,
        'description': 'Remoção automática do arquivo `.gitlab-ci.yml` pois estava configurado via settings.',
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code != 201:
        raise Exception('Erro ao abrir MR: %s' % r.text)

def lambda_handler(event, context):
    token = get_gitlab_token(os.environ['GITLAB_SECRET_ARN'])
    repos = get_all_gitlab_paths()
    for repo in repos:
        try:
            project_id = repo_path_to_project_id(repo)
            (has_ci_setting, default_branch) = ci_enabled_in_settings(project_id, token)
            if not has_ci_setting:
                continue
            if default_branch.lower() in ['main', 'master']:
                feature_branch = 'feature/remove-ci-main'
            elif default_branch.lower() in ['dev', 'develop']:
                feature_branch = 'feature/remove-ci-dev'
            else:
                continue
            if check_existing_merge_request(project_id, feature_branch, token):
                continue
            create_branch(project_id, feature_branch, default_branch, token)
            remove_ci_file(project_id, feature_branch, token)
            open_merge_request(project_id, feature_branch, default_branch, token)
        except Exception as e:
            print("Erro ao processar %s: %s" % (repo, str(e)))