import boto3
import moto
import s3_parq
import pytest
import dfmock
from s3_parq.fetch_parq import fetch
import pandas as pd

@moto.mock_s3
def test_end_to_end():
    # make it
    df = dfmock.DFMock(count=10000)
    df.columns = {"string_options": {"option_count": 4, "option_type": "string"},
                  "int_options": {"option_count": 4, "option_type": "int"},
                  "datetime_options": {"option_count": 5, "option_type": "datetime"},
                  "float_options": {"option_count": 2, "option_type": "float"},
                  "metrics": "integer"
                  }
    df.generate_dataframe()

    s3_client = boto3.client('s3')

    bucket_name = 'thistestbucket'
    key = 'thisdataset'

    s3_client.create_bucket(Bucket=bucket_name)

    pub = s3_parq.S3Parq()

    ## pub it
    pub.publish(
        bucket=bucket_name,
        key=key,
        dataframe=df.dataframe,
        partitions=['string_options',
                    'datetime_options', 'float_options']
    )

    # go get it

    dataframe = fetch(
        bucket=bucket_name,
        key=key,
        filters={}
    )

    assert dataframe.shape == df.dataframe.shape
    pd.DataFrame.eq(dataframe, df.dataframe)

    
