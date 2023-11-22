# -*- coding: utf-8 -*-

import time
import dataclasses
from datetime import datetime
from textwrap import dedent

import boto3

from fixa.aws.aws_cloudwatch_logs_insights_query import (
    get_log_group,
    create_log_group,
    delete_log_group,
    get_log_stream,
    create_log_stream,
    delete_log_stream,
    get_ts_in_second,
    get_ts_in_millisecond,
    Event,
    BaseJsonMessage,
    put_log_events,
    strip_out_limit_clause,
    run_query,
    extract_query_results,
)

boto_ses = boto3.session.Session(profile_name="awshsh_app_dev_us_east_1")
logs_client = boto_ses.client("logs")


def test_timestamp():
    now = datetime.utcnow()
    ts1 = get_ts_in_second(now)
    ts2 = get_ts_in_millisecond(now)
    assert ts2 // 1000 == ts1


@dataclasses.dataclass
class ServerStatusMessage(BaseJsonMessage):
    server_id: str
    status: str


class Test:
    def _test(self):
        group_name = "aws_cloudwatch_logs_insights_query_test"
        stream_name = "test-stream"
        delete_log_group(logs_client, group_name)
        time.sleep(1)

        # --- setup
        # at begin, it doesn't exist
        assert get_log_group(logs_client, group_name) is None
        # create it
        assert create_log_group(logs_client, group_name) is True
        # verify it exists
        assert get_log_group(logs_client, group_name)["logGroupName"] == group_name
        # create it again, nothing happens
        assert create_log_group(logs_client, group_name) is False

        # at begin, it doesn't exist
        assert get_log_stream(logs_client, group_name, stream_name) is None
        # create it
        assert create_log_stream(logs_client, group_name, stream_name) is True
        # verify it exists
        assert (
            get_log_stream(logs_client, group_name, stream_name)["logStreamName"]
            == stream_name
        )
        # create it again, nothing happens
        assert create_log_stream(logs_client, group_name, stream_name) is False

        # --- test log events
        events = [
            Event(
                message=ServerStatusMessage(
                    server_id="server-1", status="running"
                ).to_json()
            ),
            Event(
                message=ServerStatusMessage(
                    server_id="server-2", status="stopped"
                ).to_json()
            ),
        ]
        put_log_events(logs_client, group_name, stream_name, events)
        time.sleep(3)

        query = dedent(
            """
        fields @timestamp, @message, @logStream, @log, server_id
        | filter server_id = "server-1"
        | sort @timestamp desc
        """
        )
        query_id, response = run_query(
            logs_client,
            query=strip_out_limit_clause(query),
            log_group_name=group_name,
            last_n_minutes=5,
        )
        results = extract_query_results(response)
        for result in results:
            assert result["server_id"] == "server-1"

        # --- teardown
        # delete the stream
        assert delete_log_stream(logs_client, group_name, stream_name) is True
        # verify it is deleted
        assert get_log_stream(logs_client, group_name, stream_name) is None
        # delete it again, nothing happens
        assert delete_log_stream(logs_client, group_name, stream_name) is False

        # delete the group
        assert delete_log_group(logs_client, group_name) is True
        # verify it is deleted
        assert get_log_group(logs_client, group_name) is None
        # delete it again, nothing happens
        assert delete_log_group(logs_client, group_name) is False

    def _test_auto_create_stream(self):
        group_name = "test_auto_create_stream"
        stream_name = "test_stream"
        delete_log_group(logs_client, group_name)
        time.sleep(1)

        create_log_group(logs_client, group_name)
        events = [
            Event(
                message=ServerStatusMessage(
                    server_id="server-1", status="running"
                ).to_json()
            ),
            Event(
                message=ServerStatusMessage(
                    server_id="server-2", status="stopped"
                ).to_json()
            ),
        ]
        put_log_events(logs_client, group_name, stream_name, events)

    def test(self):
        print("")
        self._test()
        self._test_auto_create_stream()


if __name__ == "__main__":
    from fixa.tests import run_cov_test

    run_cov_test(__file__, "fixa.aws.aws_cloudwatch_logs_insights_query", preview=False)
