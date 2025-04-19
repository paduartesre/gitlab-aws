#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import boto3
import json
import hashlib
from datetime import datetime
from urllib import urlencode, urlopen
from urllib2 import Request

ssm = boto3.client("ssm")
secretsmanager = boto3.client("secretsmanager")
sns = boto3.client("sns")
lambda_client = boto3.client("lambda")

def get_gitlab_token(secret_arn):
    response = secretsmanager.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])["token"]

def fetch_gitlab_repos(token):
    headers = {"PRIVATE-TOKEN": token}
    repos = []
    page = 1
    while True:
        url = "https://gitlab.com/api/v4/projects?membership=true&per_page=100&page={}".format(page)
        req = Request(url, headers=headers)
        with urlopen(req) as resp:
            data = json.load(resp)
            if not data:
                break
            for repo in data:
                repos.append(repo["http_url_to_repo"])
        page += 1
    return repos

def hash_list(lst):
    return hashlib.sha256("".join(sorted(lst)).encode()).hexdigest()

def save_repos_to_ssm(repos):
    for url in repos:
        path = "/gitlab.com/{}".format("/".join(url.split("/")[-3:]))
        ssm.put_parameter(Name=path, Value=url, Type="String", Overwrite=True)

def compare_with_previous_state(new_hash):
    today_key = "/gitlab.com/_latest_hash"
    yesterday_key = "/gitlab.com/_previous_hash"
    
    try:
        old_hash = ssm.get_parameter(Name=today_key)["Parameter"]["Value"]
        ssm.put_parameter(
            Name=yesterday_key, Value=old_hash, Type="String", Overwrite=True
        )
    except ssm.exceptions.ParameterNotFound:
        old_hash = ""
    ssm.put_parameter(Name=today_key, Value=new_hash, Type="String", Overwrite=True)
    return old_hash != new_hash

def notify_change(repo_count):
    sns.publish(
        TopicArn=os.environ["SNS_TOPIC_ARN"],
        Subject="GitLab CI- Mudanças detectadas",
        Message="Foram detectadas {} mudanças na lista de repositórios.".format(repo_count),
    )

def trigger_configurator():
    lambda_client.invoke(
        FunctionName="gitlab_ci_configurator",
        InvocationType="Event",
        Payload=json.dumps({}).encode(),
    )

def lambda_handler(event, context):
    token = get_gitlab_token(os.environ["GITLAB_SECRET_ARN"])
    repos = fetch_gitlab_repos(token)
    save_repos_to_ssm(repos)
    hash_current = hash_list(repos)
    changed = compare_with_previous_state(hash_current)
    
    if changed:
        notify_change(len(repos))
        trigger_configurator()