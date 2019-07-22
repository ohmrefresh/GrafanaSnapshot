#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import os
import datetime
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from PyInquirer import (Token, ValidationError, Validator, prompt, style_from_dict)
import time

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

name = "GrafanaSnapshotLibrary"

def get_annotations(url, token, time_from=None, time_to=None, alert_id=None, dashboard_id=None, panel_id=None, tags=[], limit=None):
    api_ep = "{}/api/annotations".format(url)
    method = "GET"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token)
    }

    params = {}
    if time_from:
        params["time_from"] = time_from
    if time_to:
        params["time_to"] = time_to
    if alert_id:
        params["alertId"] = alert_id
    if dashboard_id:
        params["dashboardID"] = dashboard_id
    if panel_id:
        params["panelId"] = panel_id
    if tags:
        params["tags"] = tags
    if limit:
        params["limit"] = limit

    response = requests.request(
        method,
        api_ep,
        params=params,
        headers=headers,
        verify=False)
    return response.json()


def create_annotations(url, token, tags=[], time_from=None, time_to=None):
    api_ep = "{}/api/annotations".format(url)
    method = "POST"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    post_json = {
        "time": time_from,
        "timeEnd": time_to,
        "isRegion": bool('false'),
        "tags": tags,
        "text": "Test"
    }

    response = requests.request(
        method,
        api_ep,
        json=post_json,
        headers=headers,
        verify=False)

    return response.json()


def delete_annotations_by_region_id(url, token, region_id=None):

    """
    Delete Annotation By RegionId  (https://grafana.com/docs/http_api/annotations/#delete-annotation-by-regionid)
    DELETE /api/annotations/region/:id
    Deletes the annotation that matches the specified region id. A region is an annotation that covers
    a timerange and has a start and end time. In the Grafana database,
    this is a stored as two annotations connected by a region id.
    :param region_id:
    :return a json:
    """

    api_ep = "{}/api/annotations/region/{}".format(url, region_id)
    method = "DELETE"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    response = requests.request(
        method,
        api_ep,
        headers=headers,
        verify=False)

    return response.json()


def get_dashboard(url, token, slug):
    api_ep = "{}/api/dashboards/db/{}".format(url, slug)
    method = "GET"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    response = requests.request(
        method,
        api_ep,
        headers=headers,
        verify=False)

    return response.json()


def search_dashboards(url, token, query=None, tags=[], starred=None, tagcloud=None):
    api_ep = "{}/api/search".format(url)
    method = "GET"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    params = {}
    if query:
        params["query"] = query
    if tags:
        params["tag"] = tags
    if starred:
        params["starred"] = starred
    if tagcloud:
        params["tagcloud"] = tagcloud

    response = requests.request(
        method,
        api_ep,
        params=params,
        headers=headers,
        verify=False)

    return response.json()


def create_snapshot(url, token, dashboard, name=None, expire=None, external=None, key=None, deleteKey=None, time_from=None,
                    time_to=None):
    api_ep = "{}/api/snapshots".format(url)
    method = "POST"
    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    dashboard = dashboard["dashboard"] if "dashboard" in dashboard else dashboard

    if time_from:
        dashboard["time"]["from"] = time_str_from_unix_ms(time_from)
    if time_to:
        dashboard["time"]["to"] = time_str_from_unix_ms(time_to)

    post_json = {
        "dashboard": dashboard
    }
    if name:
        post_json["name"] = name
    if expire:
        post_json["expire"] = expire
    if external:
        post_json["external"] = external
    if key:
        post_json["key"] = key
    if deleteKey:
        post_json["deleteKey"] = deleteKey

    response = requests.request(
        method,
        api_ep,
        json=post_json,
        headers=headers,
        verify=False)

    return response.json()


def time_str_from_unix_ms(unix_ms):
    return datetime.datetime.utcfromtimestamp(int(unix_ms / 1000)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def datetime_string_to_timestamp(date_time_str):
    return int(datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S').strftime("%s"))


def get_dashboard_u(url, key):
    return "{}/dashboard/snapshot/{}".format(url, key)


def run():
    info = askInformation()
    url = info.get('base_url')
    token = info.get('api_token')

    parser = argparse.ArgumentParser(description='Create Snapshot on Grafana with official api (https://grafana.com/docs/http_api/)')

    parser.add_argument('-s', "--start", metavar='start', help='Start date time ex. 1563183710618', type=int, required=True)
    parser.add_argument('-e', "--end", metavar='end', help='End date time ex. 1563185212275', type=int, required=True)
    parser.add_argument('-t', "--tags", metavar='tags', help='Tag in grafana ex. tag-name,tag-name1', required=True)
    args = parser.parse_args()

    date_time_start = int(args.start)
    date_time_end = int(args.end)
    tags = args.tags

    dashboards_info = search_dashboards(url, token, tags=[tags])
    snapshot_list = {}
    for dashboard_info in dashboards_info:
        slug = os.path.basename(dashboard_info["uri"])
        region_str = "{0[0]}_{0[1]}".format(tuple(map(time_str_from_unix_ms, [date_time_start, date_time_end])))
        snapshot_name = "{}_{}".format(slug, region_str)
        snapshot_list[snapshot_name] = get_dashboard_u(url, create_snapshot(url,
                                                                            token,
                                                                            get_dashboard(url, token, slug),
                                                                            name=snapshot_name,
                                                                            time_from=date_time_start,
                                                                            time_to=date_time_end)['key'])
    print(snapshot_list)

class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))

style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})


def askInformation():
    questions = [
        {
            'type': 'input',
            'name': 'base_url',
            'message': 'Grafana url >',
            'default': 'https://127.0.0.1:3000',
            'validate': EmptyValidator
        },
        {
            'type': 'password',
            'name': 'api_token',
            'message': 'API token >',
            'default': 'xxx=',
            'validate': EmptyValidator
        }
    ]
    answers = prompt(questions, style=style)
    return answers

if __name__ == "__main__":
    run()
