import random
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from fastapi import UploadFile


class S3Client:
    def __init__(
            self,
            config: dict

    ):
        self.config = config
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def create_bucket(self, bucket_name):
        async with self.get_client() as client:
            buckets_responce = await client.list_buckets()
            buckets_list = [bucket['Name'] for bucket in buckets_responce['Buckets']]
            if bucket_name not in buckets_list:
                await client.create_bucket(Bucket=bucket_name)

    def create_unique_key(self, object_name, list_of_keys):
        ext = object_name.split(".")[-1]
        len_of_hash = 16
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        new_name = ''.join(random.sample(alphabet, len_of_hash))
        while new_name in list_of_keys:
            new_name = ''.join(random.sample(alphabet, len_of_hash))
        return '.'.join([new_name, ext])

    async def upload_file(self, file: UploadFile, bucket_name, acl: str = "public-read"):
        await self.create_bucket(bucket_name)
        object_name = file.filename.split("/")[-1]
        async with self.get_client() as client:
            list_objects_response = await client.list_objects_v2(Bucket=bucket_name)
            list_of_obj = [i["Key"] for i in list_objects_response.get('Contents', [])]
            key = self.create_unique_key(object_name, list_of_obj)
            file_data = await file.read()
            await client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=file_data,
                ACL=acl
            )
        link_to_file = "/".join([self.config['endpoint_url'], bucket_name, key])
        return link_to_file
